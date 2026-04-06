from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import json

from exif_reader import debug


def show_info_window(payload: dict) -> bool:
    try:
        base_dir = Path(__file__).resolve().parent
        tmp_dir = Path(tempfile.gettempdir())

        json_path = tmp_dir / "ai_metadata_inspector_info.json"
        launcher_path = tmp_dir / "ai_metadata_inspector_info_launcher.ps1"

        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
            errors="replace",
        )

        launcher_script = r'''
param(
    [string]$JsonPath,
    [string]$AppDir
)

$ErrorActionPreference = "Stop"

$helpersPath = Join-Path $AppDir "ps\info_window_helpers.ps1"
$layoutPath  = Join-Path $AppDir "ps\info_window_layout.ps1"

if (-not (Test-Path -LiteralPath $helpersPath)) {
    [System.Windows.Forms.MessageBox]::Show("Missing file: ps\info_window_helpers.ps1", "AI Metadata Inspector")
    exit 1
}

if (-not (Test-Path -LiteralPath $layoutPath)) {
    [System.Windows.Forms.MessageBox]::Show("Missing file: ps\info_window_layout.ps1", "AI Metadata Inspector")
    exit 1
}

. $helpersPath
. $layoutPath

Show-AIInfoWindow -JsonPath $JsonPath
'''
        launcher_path.write_text(
            launcher_script,
            encoding="utf-8",
            errors="replace",
        )

        result = subprocess.Popen(
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
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        debug(f"POWERSHELL GUI STARTED pid={result.pid}")
        return True

    except Exception as e:
        debug(f"INFO WINDOW ERROR: {e}")
        return False