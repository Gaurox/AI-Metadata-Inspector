from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEBUG_LOG = BASE_DIR / "prompt_tool_debug.log"


def debug(msg: str) -> None:
    try:
        with DEBUG_LOG.open("a", encoding="utf-8", errors="replace") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


EXIFTOOL = str(BASE_DIR / "exiftool.exe")

TAGS = [
    "prompt",
    "Prompt",
    "workflow",
    "Workflow",
    "Parameters",
    "Comment",
    "Description",
    "ImageDescription",
    "UserComment",
    "XPComment",
    "Caption",
    "Lyrics",
    "Title",
    "Subject",
    "XMP:Prompt",
    "XMP:Description",
    "QuickTime:Comment",
    "QuickTime:Description",
    "QuickTime:Title",
    "ID3:Comment",
    "ID3:Lyrics",
    "ID3:Title",
]

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

_ALL_TAGS = TAGS + [tag for tag in MEDIA_TAGS if tag not in TAGS]
_METADATA_CACHE: dict[str, dict[str, str]] = {}


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
        return "\n".join(parts).strip()
    if isinstance(value, dict):
        try:
            return json.dumps(value, ensure_ascii=False).strip()
        except Exception:
            return str(value).strip()
    return str(value).strip()


def _run_exiftool_cmd(cmd: list[str]) -> tuple[dict[str, str], str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            **get_hidden_subprocess_kwargs(),
        )
    except Exception as e:
        return {}, f"EXCEPTION: {e}"

    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()

    if stderr:
        debug(f"EXIFTOOL STDERR: {stderr}")

    if not stdout:
        return {}, stderr

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
    # Essai 1 : comportement actuel
    cmd_utf8 = _build_exiftool_cmd(file_path, tags, use_utf8_filename=True)
    debug(f"EXIFTOOL TRY UTF8 PATH={file_path}")
    data, stderr = _run_exiftool_cmd(cmd_utf8)

    if data:
        return data

    # Si le chemin contient des caractères non ASCII ou si exiftool a renvoyé "file not found",
    # on réessaie sans -charset filename=UTF8
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


def exiftool_exists() -> bool:
    return Path(EXIFTOOL).exists()


def collect_all_metadata(file_path: str, force_refresh: bool = False) -> dict[str, str]:
    cache_key = str(Path(file_path))
    if not force_refresh and cache_key in _METADATA_CACHE:
        return dict(_METADATA_CACHE[cache_key])

    metadata = _run_exiftool_json(file_path, _ALL_TAGS)
    _METADATA_CACHE[cache_key] = dict(metadata)
    debug(f"EXIFTOOL JSON TAGS_FOUND={len(metadata)}")
    return dict(metadata)


def run_exiftool(tag: str, file_path: str) -> str:
    metadata = collect_all_metadata(file_path)
    return metadata.get(tag, "")


def collect_found_tags(file_path: str) -> list[tuple[str, str]]:
    metadata = collect_all_metadata(file_path)
    found: list[tuple[str, str]] = []
    for tag in TAGS:
        value = metadata.get(tag, "")
        if value:
            found.append((tag, value))
    return found


def collect_media_info(file_path: str) -> dict[str, str]:
    metadata = collect_all_metadata(file_path)
    out: dict[str, str] = {}
    for tag in MEDIA_TAGS:
        value = metadata.get(tag, "")
        if value:
            out[tag] = value
    return out