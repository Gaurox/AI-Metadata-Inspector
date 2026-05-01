from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from exif_reader import debug


def _show_info_window_powershell(payload: dict) -> bool:
    base_dir = Path(__file__).resolve().parent
    tmp_dir = Path(tempfile.gettempdir())

    json_path = tmp_dir / "ai_metadata_inspector_info.json"
    log_path = tmp_dir / "ai_metadata_inspector_powershell_gui_debug.log"
    launcher_path = base_dir / "ps" / "info_window_launcher.ps1"

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        errors="replace",
    )

    if not launcher_path.exists():
        debug(f"INFO WINDOW POWERSHELL LAUNCHER MISSING: {launcher_path}")
        return False

    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(launcher_path),
            "-JsonPath",
            str(json_path),
            "-AppDir",
            str(base_dir),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        log_path.write_text(
            "STDOUT:\n"
            + (result.stdout or "")
            + "\n\nSTDERR:\n"
            + (result.stderr or "")
            + f"\n\nRETURN CODE: {result.returncode}\n",
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:
        debug(f"FAILED TO WRITE POWERSHELL LOG: {e}")

    debug(f"POWERSHELL GUI RETURN CODE={result.returncode} LOG={log_path}")
    return result.returncode == 0


def show_info_window(payload: dict) -> bool:
    try:
        from info_window_py import show_info_window_py

        if show_info_window_py(payload):
            return True
        debug("PYTHON INFO WINDOW RETURNED FALSE, FALLING BACK TO POWERSHELL")
    except Exception as e:
        debug(f"PYTHON INFO WINDOW UNAVAILABLE: {e}")

    try:
        return _show_info_window_powershell(payload)
    except Exception as e:
        debug(f"INFO WINDOW POWERSHELL ERROR: {e}")
        return False
