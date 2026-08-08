from __future__ import annotations

import ctypes
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import windows_runtime


class _FakeFunction:
    def __init__(self, callback):
        self._callback = callback
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)
        return self._callback(*args)


class _FakeKernel32:
    def __init__(self):
        self.buffer = None
        self.GlobalAlloc = _FakeFunction(self._global_alloc)
        self.GlobalLock = _FakeFunction(self._global_lock)
        self.GlobalUnlock = _FakeFunction(lambda handle: 1)
        self.GlobalFree = _FakeFunction(lambda handle: None)

    def _global_alloc(self, flags, size):
        self.buffer = ctypes.create_string_buffer(size)
        return 1

    def _global_lock(self, handle):
        return ctypes.addressof(self.buffer)


class _FakeUser32:
    def __init__(self, open_results=(1,), set_result=1):
        self._open_results = iter(open_results)
        self._set_result = set_result
        self.OpenClipboard = _FakeFunction(lambda owner: next(self._open_results))
        self.CloseClipboard = _FakeFunction(lambda: 1)
        self.EmptyClipboard = _FakeFunction(lambda: 1)
        self.SetClipboardData = _FakeFunction(lambda clipboard_format, handle: self._set_result)


class CopyUnicodeTextToClipboardTests(unittest.TestCase):
    def _copy_with_fake_win32(self, text: str, *, open_results=(1,), set_result=1):
        user32 = _FakeUser32(open_results=open_results, set_result=set_result)
        kernel32 = _FakeKernel32()

        def fake_windll(name, **kwargs):
            return {"user32": user32, "kernel32": kernel32}[name]

        with (
            patch.object(windows_runtime.ctypes, "WinDLL", side_effect=fake_windll),
            patch.object(windows_runtime.time, "sleep") as sleep,
        ):
            result = windows_runtime.copy_unicode_text_to_clipboard(text)

        return result, user32, kernel32, sleep

    def test_preserves_unicode_prompt_as_utf16le(self):
        for text in (
            "色调艳丽，过曝，静态，细节模糊不清，",
            "café, naïve, 🐉",
        ):
            with self.subTest(text=text):
                result, user32, kernel32, _ = self._copy_with_fake_win32(text)

                self.assertTrue(result)
                self.assertEqual(user32.SetClipboardData.calls, [(windows_runtime.CF_UNICODETEXT, 1)])
                self.assertEqual(
                    kernel32.buffer.raw[: len((text + "\x00").encode("utf-16-le"))],
                    (text + "\x00").encode("utf-16-le"),
                )
                self.assertEqual(kernel32.GlobalFree.calls, [])

    def test_retries_when_another_process_temporarily_locks_clipboard(self):
        result, user32, _, sleep = self._copy_with_fake_win32(
            "positive prompt 色调艳丽",
            open_results=(0, 1),
        )

        self.assertTrue(result)
        self.assertEqual(len(user32.OpenClipboard.calls), 2)
        sleep.assert_called_once_with(windows_runtime._CLIPBOARD_RETRY_DELAY_SECONDS)

    def test_frees_memory_when_windows_does_not_take_ownership(self):
        result, user32, kernel32, _ = self._copy_with_fake_win32(
            "negative prompt 色调艳丽",
            set_result=None,
        )

        self.assertFalse(result)
        self.assertEqual(len(user32.CloseClipboard.calls), 1)
        self.assertEqual(kernel32.GlobalFree.calls, [(1,)])


if __name__ == "__main__":
    unittest.main()
