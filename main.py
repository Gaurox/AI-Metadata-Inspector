from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from exif_reader import EXIFTOOL, collect_found_tags, exiftool_exists, debug
from info_builder import build_info_payload
from info_window import show_info_window
from prompt_extractors import extract_prompt_data


VALID_MODES = ("positive", "negative", "info", "debug", "export_txt", "export_json")


def get_hidden_subprocess_kwargs():
    kwargs = {}
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


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
            **get_hidden_subprocess_kwargs(),
        )
        debug(f"powershell clipboard returncode={ps.returncode} len={len(text)}")
        return ps.returncode == 0
    except Exception as e:
        debug(f"powershell clipboard exception: {e}")
        return False


def export_payload(file_path: str, payload: dict, mode: str) -> int:
    out_path = Path(file_path)

    if mode in ("debug", "export_txt"):
        out_file = out_path.with_suffix(".ai_info.txt")
        out_file.write_text(payload.get("copy_all", ""), encoding="utf-8", errors="replace")
        debug(f"EXPORT TXT={out_file}")
        return 0

    if mode == "export_json":
        out_file = out_path.with_suffix(".ai_info.json")
        out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", errors="replace")
        debug(f"EXPORT JSON={out_file}")
        return 0

    return 8


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

    if not exiftool_exists():
        debug("EXIT 2: exiftool missing")
        sys.exit(2)

    if not Path(file_path).exists():
        debug("EXIT 3: target file missing")
        sys.exit(3)

    found = collect_found_tags(file_path)

    debug(f"FOUND_TAGS_COUNT={len(found)}")
    if found:
        debug("FOUND_TAGS=" + ", ".join(tag for tag, _ in found))

    if mode == "info":
        payload = build_info_payload(file_path, found)
        if show_info_window(payload):
            debug("EXIT 0: info window opened")
            sys.exit(0)
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
