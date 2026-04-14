from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from exif_reader import debug


FRAME_PATTERN = "frame_%06d.png"
CANCEL_EXIT_CODE = 1223


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


def clean_existing_frames(folder: Path) -> None:
    if not folder.exists():
        return

    for file in folder.glob("frame_*.png"):
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

        if behavior == "single_shared_folder":
            return Path(fixed_dir)

        return Path(fixed_dir) / folder_name

    return file_path.parent / folder_name


def launch_ffmpeg(input_file: Path, output_folder: Path) -> subprocess.Popen:
    ffmpeg_path = get_ffmpeg_path()
    output_pattern = str(output_folder / FRAME_PATTERN)

    cmd = [
        str(ffmpeg_path),
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
        **get_hidden_subprocess_kwargs(),
    )


def run_progress_window(video_path: Path, output_folder: Path, ffmpeg_pid: int) -> int:
    script_path = get_window_script_path()

    if not script_path.exists():
        debug(f"WINDOW SCRIPT NOT FOUND: {script_path}")
        return 6

    tmp_dir = Path(tempfile.gettempdir())
    launcher_path = tmp_dir / "ai_metadata_inspector_frame_extract_launcher.ps1"
    log_path = tmp_dir / "ai_metadata_inspector_frame_extract_gui_debug.log"

    launcher_script = r'''
param(
    [string]$ScriptPath,
    [string]$VideoPath,
    [string]$OutputFolder,
    [int]$FfmpegProcessId
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
    -FfmpegProcessId $FfmpegProcessId

exit $LASTEXITCODE
'''.strip()

    try:
        launcher_path.write_text(
            launcher_script,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:
        debug(f"FAILED TO WRITE FRAME WINDOW LAUNCHER: {e}")
        return 6

    cmd = [
        "powershell.exe",
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
    ]

    debug(f"WINDOW CMD: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except Exception as e:
        debug(f"WINDOW LAUNCH ERROR: {e}")
        return 6

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
        debug(f"FAILED TO WRITE FRAME WINDOW LOG: {e}")

    debug(f"WINDOW RETURN CODE={result.returncode} LOG={log_path}")
    return result.returncode


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
    clean_existing_frames(output_folder)

    ffmpeg_process: subprocess.Popen | None = None

    try:
        ffmpeg_process = launch_ffmpeg(input_file, output_folder)
        debug(f"FFMPEG STARTED PID={ffmpeg_process.pid}")

        window_code = run_progress_window(input_file, output_folder, ffmpeg_process.pid)

        ffmpeg_code = ffmpeg_process.poll()
        debug(f"FFMPEG POLL AFTER WINDOW={ffmpeg_code}")

        if window_code == CANCEL_EXIT_CODE:
            debug("EXTRACTION CANCELLED BY USER")
            terminate_process_if_needed(ffmpeg_process)
            wait_process_safely(ffmpeg_process, timeout=5)
            clean_existing_frames(output_folder)
            return CANCEL_EXIT_CODE

        if ffmpeg_code is None:
            ffmpeg_code = wait_process_safely(ffmpeg_process)

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
        clean_existing_frames(output_folder)
        return 5


def extract_frames(file_path: str, config: dict) -> int:
    try:
        input_file = Path(file_path)

        if not input_file.exists():
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