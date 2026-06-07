from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from exif_reader import cleanup_stale_temp_files, debug, get_hidden_subprocess_kwargs, get_private_temp_dir


INFO_WINDOW_TIMEOUT_SECONDS = 120


def _show_info_window_powershell(payload: dict) -> bool:
    base_dir = Path(__file__).resolve().parent
    cleanup_stale_temp_files(("ai_meta_info_",))
    tmp_dir = get_private_temp_dir()
    launcher_path = base_dir / "ps" / "info_window_launcher.ps1"

    if not launcher_path.exists():
        debug(f"INFO WINDOW POWERSHELL LAUNCHER MISSING: {launcher_path}")
        return False

    # Use a randomly-named temp file so concurrent runs don't collide
    fd, json_path_str = tempfile.mkstemp(
        prefix="ai_meta_info_", suffix=".json", dir=tmp_dir
    )
    json_path = Path(json_path_str)

    try:
        os.close(fd)
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
            errors="replace",
        )

        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
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
            timeout=INFO_WINDOW_TIMEOUT_SECONDS,
            **get_hidden_subprocess_kwargs(),
        )

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        if stdout:
            debug(f"POWERSHELL GUI STDOUT: {stdout[:500]}")
        if stderr:
            debug(f"POWERSHELL GUI STDERR: {stderr[:500]}")
        debug(f"POWERSHELL GUI RETURN CODE={result.returncode}")
        return result.returncode == 0

    finally:
        try:
            json_path.unlink(missing_ok=True)
        except Exception:
            pass


def show_info_window(payload: dict) -> bool:
    _tkinter_pyd = Path(__file__).resolve().parent / "python_embeded" / "_tkinter.pyd"
    if _tkinter_pyd.exists():
        try:
            from info_window_py import show_info_window_py
            if show_info_window_py(payload):
                return True
            debug("PYTHON INFO WINDOW RETURNED FALSE, FALLING BACK TO POWERSHELL")
        except Exception as e:
            debug(f"PYTHON INFO WINDOW UNAVAILABLE: {e}")
    else:
        debug("TKINTER ABSENT FROM EMBEDDED RUNTIME — USING POWERSHELL WINDOW")

    try:
        return _show_info_window_powershell(payload)
    except Exception as e:
        debug(f"INFO WINDOW POWERSHELL ERROR: {e}")
        return False
