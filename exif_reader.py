from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

_LOG_FILE = None
APP_DATA_DIRNAME = "AI Metadata Inspector"
DEBUG_LOG_ENV = "AI_METADATA_INSPECTOR_DEBUG"
MAX_LOG_BYTES = 262_144
MAX_METADATA_TEXT_CHARS = 2_000_000
EXIFTOOL_TIMEOUT_SECONDS = 20
PRIVATE_TEMP_MAX_AGE_SECONDS = 86_400


def get_app_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA") or str(
        Path.home() / "AppData" / "Local"
    )
    path = Path(local_app_data) / APP_DATA_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_private_temp_dir() -> Path:
    try:
        temp_dir = get_app_data_dir() / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    except Exception:
        temp_dir = Path(tempfile.gettempdir()) / "AI_Metadata_Inspector"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir


def cleanup_stale_temp_files(prefixes: tuple[str, ...], max_age_seconds: int = PRIVATE_TEMP_MAX_AGE_SECONDS) -> None:
    now_ts = datetime.now().timestamp()
    try:
        temp_dir = get_private_temp_dir()
    except Exception:
        return

    for path in temp_dir.iterdir():
        try:
            if not path.is_file():
                continue
            if not any(path.name.startswith(prefix) for prefix in prefixes):
                continue
            age_seconds = now_ts - path.stat().st_mtime
            if age_seconds >= max_age_seconds:
                path.unlink(missing_ok=True)
        except Exception:
            continue


def _debug_enabled() -> bool:
    return os.environ.get(DEBUG_LOG_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def _redact_debug_message(msg: str) -> str:
    text = str(msg or "")
    text = re.sub(r"(?i)\b[A-Z]:\\[^ \r\n\t]+", "<path>", text)
    text = re.sub(r"(?i)(argv=).*", r"\1<redacted>", text)
    text = re.sub(r"(?i)(file=).*", r"\1<redacted>", text)
    text = re.sub(r"(?i)(output folder=).*", r"\1<redacted>", text)
    text = re.sub(r"(?i)(export txt=).*", r"\1<redacted>", text)
    text = re.sub(r"(?i)(export json=).*", r"\1<redacted>", text)
    if len(text) > 500:
        text = text[:500] + "...(truncated)"
    return text


def _get_log_file() -> Path:
    global _LOG_FILE
    if _LOG_FILE is None:
        try:
            log_dir = get_app_data_dir() / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            _LOG_FILE = log_dir / "prompt_tool_debug.log"
        except Exception:
            _LOG_FILE = Path(tempfile.gettempdir()) / "ai_metadata_inspector_debug.log"
    return _LOG_FILE


def debug(msg: str) -> None:
    if not _debug_enabled():
        return
    try:
        log_file = _get_log_file()
        if log_file.exists() and log_file.stat().st_size > MAX_LOG_BYTES:
            backup = log_file.with_name("prompt_tool_debug.log.1")
            try:
                if backup.exists():
                    backup.unlink()
                log_file.rename(backup)
            except Exception:
                pass
        with log_file.open("a", encoding="utf-8", errors="replace") as f:
            safe_msg = _redact_debug_message(msg)
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {safe_msg}\n")
    except Exception:
        pass


EXIFTOOL = str(BASE_DIR / "exiftool.exe")

# Priority-oriented text tags for fast prompt copy operations.
FAST_TEXT_TAGS = [
    "prompt",
    "Prompt",
    "workflow",
    "Workflow",
    "Parameters",
    "XMP:Prompt",
    "Comment",
    "Description",
    "ImageDescription",
    "UserComment",
    "XPComment",
    "XMP:Description",
    "QuickTime:Comment",
    "QuickTime:Description",
    "QuickTime:Title",
    "ID3:Comment",
    "ID3:Lyrics",
    "ID3:Title",
    "Caption",
    "Lyrics",
    "Title",
    "Subject",
]

# Keep the historical tag list for compatibility with the rest of the app.
TAGS = list(FAST_TEXT_TAGS)

MEDIA_TAGS = [
    "FileType",
    "MIMEType",
    "ImageWidth",
    "ImageHeight",
    "SourceImageWidth",
    "SourceImageHeight",
    "VideoFrameRate",
    "AvgBitrate",
    "Duration",
    "FileSize",
]

FULL_INFO_TAGS = FAST_TEXT_TAGS + [tag for tag in MEDIA_TAGS if tag not in FAST_TEXT_TAGS]
_METADATA_CACHE: dict[tuple[str, tuple[str, ...]], dict[str, str]] = {}


def get_hidden_subprocess_kwargs():
    kwargs = {}
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


def _normalize_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "\n".join(parts).strip()[:MAX_METADATA_TEXT_CHARS]
    if isinstance(value, dict):
        try:
            return json.dumps(value, ensure_ascii=False).strip()[:MAX_METADATA_TEXT_CHARS]
        except Exception:
            return str(value).strip()[:MAX_METADATA_TEXT_CHARS]
    return str(value).strip()[:MAX_METADATA_TEXT_CHARS]


def _run_exiftool_cmd(cmd: list[str]) -> tuple[dict[str, str], str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=EXIFTOOL_TIMEOUT_SECONDS,
            **get_hidden_subprocess_kwargs(),
        )
    except subprocess.TimeoutExpired:
        return {}, "EXIFTOOL TIMEOUT"
    except Exception as e:
        return {}, f"EXCEPTION: {e}"

    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()

    if stderr:
        debug(f"EXIFTOOL STDERR: {stderr}")

    if not stdout:
        return {}, stderr

    if len(stdout) > MAX_METADATA_TEXT_CHARS:
        debug("EXIFTOOL STDOUT TOO LARGE")
        return {}, "EXIFTOOL OUTPUT TOO LARGE"

    try:
        payload = json.loads(stdout)
        if not isinstance(payload, list) or not payload:
            return {}, stderr
        record = payload[0]
        if not isinstance(record, dict):
            return {}, stderr
    except Exception as e:
        debug(f"EXIFTOOL JSON PARSE ERROR: {e}")
        return {}, stderr

    out: dict[str, str] = {}
    for key, value in record.items():
        normalized = _normalize_value(value)
        if normalized:
            out[str(key)] = normalized

    return out, stderr


def _build_exiftool_cmd(file_path: str, tags: list[str], use_utf8_filename: bool) -> list[str]:
    cmd = [EXIFTOOL, "-j"]
    if use_utf8_filename:
        cmd.extend(["-charset", "filename=UTF8"])
    cmd.extend(f"-{tag}" for tag in tags)
    cmd.append(file_path)
    return cmd


def _run_exiftool_json(file_path: str, tags: list[str]) -> dict[str, str]:
    cmd_utf8 = _build_exiftool_cmd(file_path, tags, use_utf8_filename=True)
    debug(f"EXIFTOOL TRY UTF8 PATH={file_path} TAGS={len(tags)}")
    data, stderr = _run_exiftool_cmd(cmd_utf8)

    if data:
        return data

    path_has_non_ascii = any(ord(ch) > 127 for ch in str(file_path))
    stderr_lower = (stderr or "").lower()

    should_retry = (
        path_has_non_ascii
        or "file not found" in stderr_lower
        or "error opening file" in stderr_lower
    )

    if should_retry:
        debug("EXIFTOOL RETRY WITHOUT filename=UTF8")
        cmd_plain = _build_exiftool_cmd(file_path, tags, use_utf8_filename=False)
        data2, stderr2 = _run_exiftool_cmd(cmd_plain)
        if data2:
            return data2
        if stderr2:
            debug(f"EXIFTOOL RETRY FAILED: {stderr2}")

    return {}


def _cache_key(file_path: str, tags: list[str]) -> tuple[str, tuple[str, ...]]:
    normalized_tags = tuple(dict.fromkeys(str(tag) for tag in tags))
    return str(Path(file_path)), normalized_tags


def exiftool_exists() -> bool:
    return Path(EXIFTOOL).exists()


def collect_metadata_for_tags(file_path: str, tags: list[str], force_refresh: bool = False) -> dict[str, str]:
    unique_tags = list(dict.fromkeys(str(tag) for tag in tags))
    key = _cache_key(file_path, unique_tags)

    if not force_refresh and key in _METADATA_CACHE:
        return dict(_METADATA_CACHE[key])

    metadata = _run_exiftool_json(file_path, unique_tags)
    _METADATA_CACHE[key] = dict(metadata)
    debug(f"EXIFTOOL JSON TAGS_FOUND={len(metadata)} REQUESTED={len(unique_tags)}")
    return dict(metadata)


def collect_all_metadata(file_path: str, force_refresh: bool = False) -> dict[str, str]:
    return collect_metadata_for_tags(file_path, FULL_INFO_TAGS, force_refresh=force_refresh)


def run_exiftool(tag: str, file_path: str) -> str:
    metadata = collect_all_metadata(file_path)
    return metadata.get(tag, "")


def _collect_found_tags_from_metadata(metadata: dict[str, str], tags: list[str]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for tag in tags:
        value = metadata.get(tag, "")
        if value:
            found.append((tag, value))
    return found


def collect_found_tags_fast(file_path: str) -> list[tuple[str, str]]:
    metadata = collect_metadata_for_tags(file_path, FAST_TEXT_TAGS)
    return _collect_found_tags_from_metadata(metadata, FAST_TEXT_TAGS)


def collect_found_tags(file_path: str) -> list[tuple[str, str]]:
    metadata = collect_all_metadata(file_path)
    return _collect_found_tags_from_metadata(metadata, TAGS)


def collect_media_info(file_path: str) -> dict[str, str]:
    metadata = collect_all_metadata(file_path)
    out: dict[str, str] = {}
    for tag in MEDIA_TAGS:
        value = metadata.get(tag, "")
        if value:
            out[tag] = value
    return out
