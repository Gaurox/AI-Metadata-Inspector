from __future__ import annotations

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from exif_reader import cleanup_stale_temp_files, debug, get_private_temp_dir


# Important: no timeout here. The PowerShell process owns the WinForms window,
# so it is expected to stay alive until the user closes the AI Info window.
INFO_WINDOW_TIMEOUT_SECONDS = None


def _write_visible_error(title: str, message: str) -> None:
    """Best-effort visible error for silent Explorer/VBS launches."""
    try:
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            f"[System.Windows.Forms.MessageBox]::Show({message!r}, {title!r}) | Out-Null"
        )
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-STA",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps,
            ],
            check=False,
            timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        pass


def _append_ai_info_log(message: str) -> None:
    try:
        base = Path(os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local"))
        log_dir = base / "AI Metadata Inspector" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "ai_info_error.log"
        with log_file.open("a", encoding="utf-8", errors="replace") as f:
            f.write("\n" + "=" * 72 + "\n")
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write(str(message) + "\n")
    except Exception:
        pass


def _get_gui_subprocess_kwargs() -> dict:
    """
    For a GUI PowerShell/WinForms window, do NOT pass STARTUPINFO with
    STARTF_USESHOWWINDOW/SW_HIDE. That can hide the WinForms form itself.

    CREATE_NO_WINDOW is enough to prevent the console window while still
    allowing WinForms windows to appear.
    """
    kwargs: dict = {}
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


def _show_info_window_powershell(payload: dict) -> bool:
    base_dir = Path(__file__).resolve().parent
    cleanup_stale_temp_files(("ai_meta_info_",))
    tmp_dir = get_private_temp_dir()
    launcher_path = base_dir / "ps" / "info_window_launcher.ps1"

    _append_ai_info_log(f"PowerShell window path={launcher_path}")

    if not launcher_path.exists():
        message = f"Missing PowerShell launcher:\n{launcher_path}"
        debug(f"INFO WINDOW POWERSHELL LAUNCHER MISSING: {launcher_path}")
        _append_ai_info_log(message)
        _write_visible_error("AI Metadata Inspector", message)
        return False

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

        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-STA",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(launcher_path),
            "-JsonPath",
            str(json_path),
            "-AppDir",
            str(base_dir),
        ]

        _append_ai_info_log("Launching PowerShell GUI with CREATE_NO_WINDOW only")
        debug("POWERSHELL GUI LAUNCH: CREATE_NO_WINDOW only, no STARTUPINFO hide flag")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=INFO_WINDOW_TIMEOUT_SECONDS,
            **_get_gui_subprocess_kwargs(),
        )

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        if stdout:
            debug(f"POWERSHELL GUI STDOUT: {stdout[:500]}")
            _append_ai_info_log(f"STDOUT: {stdout[:2000]}")
        if stderr:
            debug(f"POWERSHELL GUI STDERR: {stderr[:500]}")
            _append_ai_info_log(f"STDERR: {stderr[:2000]}")

        debug(f"POWERSHELL GUI RETURN CODE={result.returncode}")
        _append_ai_info_log(f"PowerShell GUI return code={result.returncode}")

        if result.returncode != 0:
            message = (
                "The AI Info PowerShell window failed.\n\n"
                f"Return code: {result.returncode}\n\n"
                f"STDERR:\n{stderr[:1200] if stderr else '(empty)'}"
            )
            _write_visible_error("AI Metadata Inspector", message)

        return result.returncode == 0

    except Exception as e:
        message = f"INFO WINDOW POWERSHELL ERROR: {e}"
        debug(message)
        _append_ai_info_log(message)
        _write_visible_error("AI Metadata Inspector", message)
        return False

    finally:
        try:
            json_path.unlink(missing_ok=True)
        except Exception:
            pass


def show_info_window(payload: dict) -> bool:
    # PowerShell WinForms is the stable production path for the Explorer shell
    # integration. Tkinter remains only as a fallback because embedded Python
    # Tk builds can vary and can fail silently from a hidden VBS launch.
    if _show_info_window_powershell(payload):
        return True

    try:
        _tkinter_pyd = Path(__file__).resolve().parent / "python_embeded" / "_tkinter.pyd"
        if _tkinter_pyd.exists():
            from info_window_py import show_info_window_py

            return bool(show_info_window_py(payload))
    except Exception as e:
        debug(f"PYTHON INFO WINDOW FALLBACK FAILED: {e}")
        _append_ai_info_log(f"PYTHON INFO WINDOW FALLBACK FAILED: {e}")

    return False
