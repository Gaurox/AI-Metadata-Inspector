from __future__ import annotations

import ctypes
import os
import time
from pathlib import Path


MB_OK = 0x00000000
MB_ICONERROR = 0x00000010
MB_SETFOREGROUND = 0x00010000

# Clipboard formats and GlobalAlloc flags from WinUser.h / WinBase.h.
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
_CLIPBOARD_RETRY_COUNT = 10
_CLIPBOARD_RETRY_DELAY_SECONDS = 0.05


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


def copy_unicode_text_to_clipboard(text: str) -> bool:
    """Copy text to the Windows clipboard without a console code-page conversion.

    Explorer actions run without an interactive console.  Passing UTF-8 through
    ``clip.exe`` or Windows PowerShell in that context can decode CJK, emoji,
    and accented text using the active console code page.  CF_UNICODETEXT
    stores UTF-16 text directly in the Windows clipboard instead.
    """
    if os.name != "nt":
        return False

    value = "" if text is None else str(text)
    # CF_UNICODETEXT is a NUL-terminated UTF-16LE string. An embedded NUL
    # cannot be represented by this clipboard format, so do not leave one to
    # truncate the rest of a prompt silently.
    encoded_value = (value.replace("\x00", "") + "\x00").encode("utf-16-le")

    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        user32.OpenClipboard.argtypes = (ctypes.c_void_p,)
        user32.OpenClipboard.restype = ctypes.c_int
        user32.CloseClipboard.argtypes = ()
        user32.CloseClipboard.restype = ctypes.c_int
        user32.EmptyClipboard.argtypes = ()
        user32.EmptyClipboard.restype = ctypes.c_int
        user32.SetClipboardData.argtypes = (ctypes.c_uint, ctypes.c_void_p)
        user32.SetClipboardData.restype = ctypes.c_void_p

        kernel32.GlobalAlloc.argtypes = (ctypes.c_uint, ctypes.c_size_t)
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = (ctypes.c_void_p,)
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = (ctypes.c_void_p,)
        kernel32.GlobalUnlock.restype = ctypes.c_int
        kernel32.GlobalFree.argtypes = (ctypes.c_void_p,)
        kernel32.GlobalFree.restype = ctypes.c_void_p
    except Exception:
        return False

    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded_value))
    if not handle:
        return False

    clipboard_open = False
    clipboard_owns_handle = False
    try:
        memory = kernel32.GlobalLock(handle)
        if not memory:
            return False

        try:
            ctypes.memmove(memory, encoded_value, len(encoded_value))
        finally:
            kernel32.GlobalUnlock(handle)

        for attempt in range(_CLIPBOARD_RETRY_COUNT):
            if user32.OpenClipboard(None):
                clipboard_open = True
                break
            if attempt + 1 < _CLIPBOARD_RETRY_COUNT:
                time.sleep(_CLIPBOARD_RETRY_DELAY_SECONDS)

        if not clipboard_open:
            return False

        if not user32.EmptyClipboard():
            return False

        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            return False

        # Once SetClipboardData succeeds, Windows owns the HGLOBAL memory.
        clipboard_owns_handle = True
        return True
    except Exception:
        return False
    finally:
        if clipboard_open:
            user32.CloseClipboard()
        if not clipboard_owns_handle:
            kernel32.GlobalFree(handle)
