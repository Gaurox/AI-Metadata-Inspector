from __future__ import annotations

import math
import os
import subprocess
import tempfile
import time
from pathlib import Path

from exif_reader import (
    cleanup_stale_temp_files,
    collect_media_info,
    debug,
    get_private_temp_dir,
)
from windows_runtime import get_system_executable


FRAME_PATTERN = "frame_%06d.png"
CANCEL_EXIT_CODE = 1223
MANAGED_SHARED_FOLDER_NAME = "_ai_metadata_inspector_shared_frames"
EXTRACTION_LOCK_FILE = ".ai_metadata_inspector.lock"
LOCK_STALE_AFTER_SECONDS = 21_600
FFMPEG_WAIT_TIMEOUT_SECONDS = 86_400


def get_hidden_subprocess_kwargs():
    kwargs = {}
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent


def get_ffmpeg_path() -> Path:
    return get_base_dir() / "ffmpeg.exe"


def get_window_script_path() -> Path:
    return get_base_dir() / "ps" / "frame_extract_window.ps1"


def safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _lock_file_path(folder: Path) -> Path:
    return folder / EXTRACTION_LOCK_FILE


def _is_stale_lock(lock_path: Path) -> bool:
    try:
        age_seconds = max(0.0, time.time() - lock_path.stat().st_mtime)
        return age_seconds >= LOCK_STALE_AFTER_SECONDS
    except Exception:
        return False


def acquire_output_lock(folder: Path) -> tuple[int, Path] | tuple[None, None]:
    lock_path = _lock_file_path(folder)

    if lock_path.exists() and _is_stale_lock(lock_path):
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass

    fd: int | None = None
    acquired = False
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
        lock_contents = str(os.getpid()).encode("ascii", errors="strict")
        if os.write(fd, lock_contents) != len(lock_contents):
            raise OSError("incomplete extraction lock write")
        acquired = True
        return fd, lock_path
    except FileExistsError:
        debug(f"EXTRACTION LOCK EXISTS: {lock_path}")
        return None, None
    except OSError as e:
        debug(f"EXTRACTION LOCK CREATE/WRITE FAILED: {e}")
        return None, None
    finally:
        if not acquired:
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    pass
            if fd is not None:
                try:
                    lock_path.unlink(missing_ok=True)
                except Exception:
                    pass


def release_output_lock(lock_handle: int | None, lock_path: Path | None) -> None:
    if lock_handle is not None:
        try:
            os.close(lock_handle)
        except Exception:
            pass
    if lock_path is not None:
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass


def clean_existing_frames(folder: Path) -> None:
    if not folder.exists():
        return

    frames = list(folder.glob("frame_*.png"))
    if frames:
        debug(f"CLEANING {len(frames)} EXISTING FRAME(S) IN {folder}")
    for file in frames:
        try:
            file.unlink()
        except Exception as e:
            debug(f"FAILED TO DELETE FRAME: {file} ({e})")


def build_output_folder(
    file_path: Path,
    mode: str,
    fixed_dir: str | None,
    fixed_folder_behavior: str | None,
) -> Path:
    video_name = file_path.stem
    folder_name = f"{video_name}-frames"

    if mode == "fixed_folder" and fixed_dir:
        behavior = str(fixed_folder_behavior or "").strip().lower()
        fixed_base = Path(fixed_dir)

        if behavior == "single_shared_folder":
            # Never clean a user-selected folder directly. Shared mode always
            # uses one managed child folder dedicated to this application.
            return fixed_base / MANAGED_SHARED_FOLDER_NAME

        return fixed_base / folder_name

    return file_path.parent / folder_name


def _parse_fraction(text: str) -> float | None:
    raw = str(text or "").strip()
    if not raw:
        return None

    try:
        if "/" in raw:
            left, right = raw.split("/", 1)
            denominator = float(right.strip())
            if denominator == 0:
                return None
            return float(left.strip()) / denominator
        return float(raw)
    except Exception:
        return None


def _parse_duration_seconds(value) -> float | None:
    raw = str(value or "").strip()
    if not raw:
        return None

    normalized = raw.lower().replace(" sec", "").replace(" secs", "").strip()

    if ":" in normalized:
        parts = normalized.split(":")
        try:
            parts_f = [float(part.strip()) for part in parts]
        except Exception:
            parts_f = []

        if len(parts_f) == 3:
            return (parts_f[0] * 3600.0) + (parts_f[1] * 60.0) + parts_f[2]
        if len(parts_f) == 2:
            return (parts_f[0] * 60.0) + parts_f[1]

    try:
        return float(normalized)
    except Exception:
        return None


def estimate_total_frames(input_file: Path) -> int:
    try:
        media = collect_media_info(str(input_file))
    except Exception as e:
        debug(f"FAILED TO READ MEDIA INFO FOR PROGRESS: {e}")
        return 0

    fps_raw = media.get("VideoFrameRate", "")
    duration_raw = media.get("Duration", "")

    fps = _parse_fraction(fps_raw)
    duration_seconds = _parse_duration_seconds(duration_raw)

    debug(
        "PROGRESS ESTIMATE INPUT "
        f"fps_raw={fps_raw!r} duration_raw={duration_raw!r} "
        f"fps={fps!r} duration_seconds={duration_seconds!r}"
    )

    if fps is None or duration_seconds is None:
        return 0

    if fps <= 0 or duration_seconds <= 0:
        return 0

    estimated = int(math.ceil(fps * duration_seconds))
    if estimated <= 0:
        return 0

    debug(f"ESTIMATED TOTAL FRAMES={estimated}")
    return estimated


def launch_ffmpeg(input_file: Path, output_folder: Path) -> subprocess.Popen:
    ffmpeg_path = get_ffmpeg_path()
    output_pattern = str(output_folder / FRAME_PATTERN)

    cmd = [
        str(ffmpeg_path),
        "-nostdin",
        "-protocol_whitelist",
        "file,pipe,data",
        "-y",
        "-i",
        str(input_file),
        "-fps_mode",
        "passthrough",
        output_pattern,
    ]

    debug(f"FFMPEG CMD: {' '.join(cmd)}")

    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(get_base_dir()),
        **get_hidden_subprocess_kwargs(),
    )


def run_progress_window(
    video_path: Path,
    output_folder: Path,
    ffmpeg_pid: int,
    expected_frame_count: int,
) -> int:
    script_path = get_window_script_path()

    if not script_path.exists():
        debug(f"WINDOW SCRIPT NOT FOUND: {script_path}")
        return 6

    cleanup_stale_temp_files(("ai_meta_launcher_",))
    tmp_dir = get_private_temp_dir()

    launcher_script = r'''
param(
    [string]$ScriptPath,
    [string]$VideoPath,
    [string]$OutputFolder,
    [int]$FfmpegProcessId,
    [int]$ExpectedFrameCount
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not (Test-Path -LiteralPath $ScriptPath)) {
    Write-Error "Missing script: $ScriptPath"
    exit 6
}

& $ScriptPath `
    -VideoPath $VideoPath `
    -OutputFolder $OutputFolder `
    -FfmpegProcessId $FfmpegProcessId `
    -ExpectedFrameCount $ExpectedFrameCount

exit $LASTEXITCODE
'''.strip()

    # Use a randomly-named temp file to avoid collisions and path prediction
    fd, launcher_path_str = tempfile.mkstemp(
        prefix="ai_meta_launcher_", suffix=".ps1", dir=tmp_dir
    )
    launcher_path = Path(launcher_path_str)

    try:
        try:
            os.close(fd)
            launcher_path.write_text(
                launcher_script,
                encoding="utf-8",
                errors="replace",
            )
        except Exception as e:
            debug(f"FAILED TO WRITE FRAME WINDOW LAUNCHER: {e}")
            return 6

        cmd = [
            get_system_executable("WindowsPowerShell\\v1.0\\powershell.exe"),
            "-NoProfile",
            "-STA",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(launcher_path),
            "-ScriptPath",
            str(script_path),
            "-VideoPath",
            str(video_path),
            "-OutputFolder",
            str(output_folder),
            "-FfmpegProcessId",
            str(ffmpeg_pid),
            "-ExpectedFrameCount",
            str(expected_frame_count),
        ]

        debug(f"WINDOW CMD (launcher={launcher_path.name}): {' '.join(cmd[:-10])}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                cwd=str(get_base_dir()),
                **get_hidden_subprocess_kwargs(),
            )
        except Exception as e:
            debug(f"WINDOW LAUNCH ERROR: {e}")
            return 6

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        if stdout:
            debug(f"WINDOW STDOUT: {stdout[:500]}")
        if stderr:
            debug(f"WINDOW STDERR: {stderr[:500]}")
        debug(f"WINDOW RETURN CODE={result.returncode}")
        return result.returncode

    finally:
        try:
            launcher_path.unlink(missing_ok=True)
        except Exception:
            pass


def terminate_process_if_needed(process: subprocess.Popen | None) -> None:
    if process is None:
        return

    try:
        if process.poll() is None:
            process.kill()
            debug(f"PROCESS KILLED PID={process.pid}")
    except Exception as e:
        debug(f"FAILED TO KILL PID={getattr(process, 'pid', '?')} ({e})")


def wait_process_safely(process: subprocess.Popen | None, timeout: int | None = None) -> int:
    if process is None:
        return -1

    try:
        return process.wait(timeout=timeout)
    except Exception as e:
        debug(f"FAILED TO WAIT PID={getattr(process, 'pid', '?')} ({e})")
        return -1


def run_ffmpeg_with_cancel_ui(input_file: Path, output_folder: Path) -> int:
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path.exists():
        debug(f"FFMPEG NOT FOUND: {ffmpeg_path}")
        return 2

    window_script = get_window_script_path()
    if not window_script.exists():
        debug(f"WINDOW SCRIPT NOT FOUND: {window_script}")
        return 6

    safe_mkdir(output_folder)
    lock_handle, lock_path = acquire_output_lock(output_folder)
    if lock_handle is None:
        return 8

    ffmpeg_process: subprocess.Popen | None = None

    try:
        clean_existing_frames(output_folder)
        expected_frame_count = estimate_total_frames(input_file)

        ffmpeg_process = launch_ffmpeg(input_file, output_folder)
        debug(f"FFMPEG STARTED PID={ffmpeg_process.pid}")

        window_code = run_progress_window(
            input_file,
            output_folder,
            ffmpeg_process.pid,
            expected_frame_count,
        )

        ffmpeg_code = ffmpeg_process.poll()
        debug(f"FFMPEG POLL AFTER WINDOW={ffmpeg_code}")

        if window_code == CANCEL_EXIT_CODE:
            debug("EXTRACTION CANCELLED BY USER")
            terminate_process_if_needed(ffmpeg_process)
            wait_process_safely(ffmpeg_process, timeout=5)
            clean_existing_frames(output_folder)
            return CANCEL_EXIT_CODE

        if ffmpeg_code is None:
            ffmpeg_code = wait_process_safely(
                ffmpeg_process,
                timeout=FFMPEG_WAIT_TIMEOUT_SECONDS,
            )
            if ffmpeg_code == -1:
                terminate_process_if_needed(ffmpeg_process)
                clean_existing_frames(output_folder)
                return 4

        debug(f"FFMPEG FINAL RETURN CODE={ffmpeg_code}")

        if window_code != 0:
            debug("WINDOW CLOSED UNEXPECTEDLY OR FAILED TO START")
            terminate_process_if_needed(ffmpeg_process)
            wait_process_safely(ffmpeg_process, timeout=5)
            clean_existing_frames(output_folder)
            return 7

        if ffmpeg_code == 0:
            debug("EXTRACTION SUCCESS")
            return 0

        debug(f"FFMPEG FAILED WITH CODE={ffmpeg_code}")
        clean_existing_frames(output_folder)
        return 4

    except Exception as e:
        debug(f"EXTRACTION ERROR: {e}")
        terminate_process_if_needed(ffmpeg_process)
        try:
            clean_existing_frames(output_folder)
        except Exception as cleanup_error:
            debug(f"FAILED TO CLEAN FRAMES AFTER EXTRACTION ERROR: {cleanup_error}")
        return 5
    finally:
        release_output_lock(lock_handle, lock_path)


def extract_frames(file_path: str, config: dict) -> int:
    try:
        input_file = Path(file_path)

        if not input_file.is_file():
            debug(f"INPUT FILE NOT FOUND: {input_file}")
            return 1

        mode = str(config.get("mode", "next_to_video")).strip().lower()
        fixed_dir = config.get("fixed_folder")
        fixed_folder_behavior = str(
            config.get("fixed_folder_behavior", "subfolder_per_video")
        ).strip().lower()

        output_folder = build_output_folder(
            input_file,
            mode,
            fixed_dir,
            fixed_folder_behavior,
        )

        debug(f"EXTRACT MODE={mode}")
        debug(f"FIXED FOLDER BEHAVIOR={fixed_folder_behavior}")
        debug(f"OUTPUT FOLDER={output_folder}")

        return run_ffmpeg_with_cancel_ui(input_file, output_folder)

    except Exception as e:
        debug(f"EXTRACTION CRASH: {e}")
        return 5
