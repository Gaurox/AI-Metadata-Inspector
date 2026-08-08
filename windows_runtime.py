from __future__ import annotations

import ctypes
import os
from pathlib import Path


MB_OK = 0x00000000
MB_ICONERROR = 0x00000010
MB_SETFOREGROUND = 0x00010000


def get_system_executable(name: str) -> str:
    """Return an explicit System32 executable path without PATH lookup."""
    system_root = os.environ.get("SystemRoot") or os.environ.get("WINDIR") or r"C:\Windows"
    return str(Path(system_root) / "System32" / name)


def show_error_message(title: str, message: str) -> bool:
    """Display a Unicode native error dialog without interpreting its text."""
    try:
        result = ctypes.windll.user32.MessageBoxW(
            None,
            str(message),
            str(title),
            MB_OK | MB_ICONERROR | MB_SETFOREGROUND,
        )
        return bool(result)
    except Exception:
        return False
