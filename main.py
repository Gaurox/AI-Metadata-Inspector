from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app_config import get_frame_extraction_config
from exif_reader import (
    EXIFTOOL,
    collect_found_tags,
    collect_found_tags_fast,
    debug,
    exiftool_exists,
)
from frame_extractor import extract_frames
from info_builder import build_info_payload
from info_window import show_info_window
from prompt_extractors import extract_prompt_data, extract_prompt_data_fast


VALID_MODES = (
    "positive",
    "negative",
    "info",
    "debug",
    "export_txt",
    "export_json",
    "extract_frames",
)


def get_hidden_subprocess_kwargs():
    kwargs = {}
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs



def _diagnostic_log_path() -> Path:
    try:
        local_app_data = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        log_dir = Path(local_app_data) / "AI Metadata Inspector" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / "ai_info_error.log"
    except Exception:
        return Path(tempfile.gettempdir()) / "ai_info_error.log"


def _write_diagnostic(message: str) -> None:
    try:
        path = _diagnostic_log_path()
        with path.open("a", encoding="utf-8", errors="replace") as f:
            f.write("\n" + "=" * 72 + "\n")
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write(str(message) + "\n")
    except Exception:
        pass


def _show_visible_error(title: str, message: str) -> None:
    full_message = str(message)
    try:
        # Keep the dialog reasonably readable.
        if len(full_message) > 3500:
            full_message = full_message[:3500] + "\n...(truncated)"
        ps_script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "[System.Windows.Forms.MessageBox]::Show($args[0], $args[1], "
            "[System.Windows.Forms.MessageBoxButtons]::OK, "
            "[System.Windows.Forms.MessageBoxIcon]::Error) | Out-Null"
        )
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass", "-Command", ps_script, full_message, title],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            **get_hidden_subprocess_kwargs(),
        )
    except Exception:
        pass


def copy_to_clipboard(text: str) -> bool:
    text = "" if text is None else str(text)

    try:
        result = subprocess.run(
            ["clip.exe"],
            input=text,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=5,
            **get_hidden_subprocess_kwargs(),
        )
        debug(f"clip.exe returncode={result.returncode} len={len(text)}")
        if result.returncode == 0:
            return True
    except Exception as e:
        debug(f"clip.exe exception: {e}")

    try:
        ps = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Set-Clipboard -Value ([Console]::In.ReadToEnd())",
            ],
            input=text,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=5,
            **get_hidden_subprocess_kwargs(),
        )
        debug(f"powershell clipboard returncode={ps.returncode} len={len(text)}")
        return ps.returncode == 0
    except Exception as e:
        debug(f"powershell clipboard exception: {e}")
        return False


def _atomic_write_text(out_file: Path, content: str) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path_str = tempfile.mkstemp(
        prefix="ai_meta_export_",
        suffix=out_file.suffix,
        dir=out_file.parent,
    )
    temp_path = Path(temp_path_str)
    try:
        os.close(fd)
        temp_path.write_text(content, encoding="utf-8", errors="replace")
        os.replace(temp_path, out_file)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass


def export_payload(file_path: str, payload: dict, mode: str) -> int:
    out_path = Path(file_path)

    if mode in ("debug", "export_txt"):
        out_file = out_path.with_suffix(".ai_info.txt")
        _atomic_write_text(out_file, payload.get("copy_all", ""))
        debug(f"EXPORT TXT={out_file}")
        return 0

    if mode == "export_json":
        out_file = out_path.with_suffix(".ai_info.json")
        _atomic_write_text(out_file, json.dumps(payload, indent=2, ensure_ascii=False))
        debug(f"EXPORT JSON={out_file}")
        return 0

    return 8


def _try_fast_prompt_copy(file_path: str, mode: str) -> int | None:
    if mode not in ("positive", "negative"):
        return None

    found_fast = collect_found_tags_fast(file_path)
    debug(f"FAST_FOUND_TAGS_COUNT={len(found_fast)}")

    if not found_fast:
        return None

    prompt_data = extract_prompt_data_fast(found_fast)
    extracted = prompt_data.get(mode)

    if extracted is not None and (extracted != "" or mode == "negative"):
        debug(f"FAST EXTRACTION MATCH mode={mode} len={len(extracted)}")
        if copy_to_clipboard(extracted):
            debug("EXIT 0: fast extraction copied")
            return 0
        debug("FAST PATH COPY FAILED, FALLBACK TO FULL")

    return None


def main():
    debug("=" * 70)
    debug(f"ARGV={sys.argv}")

    if len(sys.argv) < 2:
        debug("EXIT 1: no file argument")
        sys.exit(1)

    file_path = sys.argv[1]
    mode = "positive"

    if len(sys.argv) >= 3:
        arg_mode = (sys.argv[2] or "").strip().lower()
        if arg_mode in VALID_MODES:
            mode = arg_mode

    debug(f"FILE={file_path}")
    debug(f"MODE={mode}")
    debug(f"EXIFTOOL={EXIFTOOL}")

    if mode == "extract_frames":
        if not Path(file_path).is_file():
            debug("EXIT 3: target file missing")
            sys.exit(3)

        config = get_frame_extraction_config()
        result = extract_frames(file_path, config)
        debug(f"EXIT {result}: extract_frames")
        sys.exit(result)

    if not exiftool_exists():
        debug("EXIT 2: exiftool missing")
        sys.exit(2)

    if not Path(file_path).is_file():
        debug("EXIT 3: target file missing")
        sys.exit(3)

    fast_result = _try_fast_prompt_copy(file_path, mode)
    if fast_result is not None:
        sys.exit(fast_result)

    found = collect_found_tags(file_path)

    debug(f"FOUND_TAGS_COUNT={len(found)}")
    if found:
        debug("FOUND_TAGS=" + ", ".join(tag for tag, _ in found))

    if mode == "info":
        _write_diagnostic("INFO MODE REACHED\nfile=" + str(file_path) + "\nfound_tags=" + str(len(found)))
        try:
            payload = build_info_payload(file_path, found)
            _write_diagnostic("PAYLOAD BUILT OK\nkeys=" + ", ".join(sorted(payload.keys())))
        except Exception:
            err = traceback.format_exc()
            _write_diagnostic("PAYLOAD BUILD FAILED\n" + err)
            _show_visible_error(
                "AI Metadata Inspector - AI Info error",
                "AI Info failed while building metadata payload.\n\n" + err + "\nLog: " + str(_diagnostic_log_path()),
            )
            sys.exit(70)

        try:
            opened = show_info_window(payload)
        except Exception:
            err = traceback.format_exc()
            _write_diagnostic("WINDOW OPEN CRASHED\n" + err)
            _show_visible_error(
                "AI Metadata Inspector - AI Info error",
                "AI Info crashed while opening the window.\n\n" + err + "\nLog: " + str(_diagnostic_log_path()),
            )
            sys.exit(71)

        if opened:
            _write_diagnostic("WINDOW OPENED OK")
            debug("EXIT 0: info window opened")
            sys.exit(0)

        _write_diagnostic("show_info_window returned False")
        _show_visible_error(
            "AI Metadata Inspector - AI Info error",
            "AI Info did not open. show_info_window() returned False.\n\nLog: " + str(_diagnostic_log_path()),
        )
        debug("EXIT 7: info window failed")
        sys.exit(7)

    if mode in ("debug", "export_txt", "export_json"):
        payload = build_info_payload(file_path, found)
        sys.exit(export_payload(file_path, payload, mode))

    if not found:
        debug("EXIT 4: no matching tags found")
        sys.exit(4)

    prompt_data = extract_prompt_data(found)
    extracted = prompt_data.get(mode)

    if extracted is not None and (extracted != "" or mode == "negative"):
        debug(f"SHARED EXTRACTION MATCH mode={mode} len={len(extracted)}")
        if copy_to_clipboard(extracted):
            debug("EXIT 0: shared extraction copied")
            sys.exit(0)
        debug("EXIT 5: shared extraction copy failed")
        sys.exit(5)

    debug("EXIT 6: no prompt extracted")
    sys.exit(6)


if __name__ == "__main__":
    main()
