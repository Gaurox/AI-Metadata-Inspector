#Requires -Version 5.1
<#
.SYNOPSIS
    Generate a SHA-256 checksum for the built AI Metadata Inspector installer.

.DESCRIPTION
    Looks for AI_Metadata_Inspector_Setup.exe in the Output\ directory (produced
    by Inno Setup) and writes a .sha256 sidecar file alongside it.
    Publish both files with each GitHub release so users can verify downloads.

.EXAMPLE
    .\tools\generate_checksum.ps1

.EXAMPLE
    # Override the output directory:
    .\tools\generate_checksum.ps1 -OutputDir "D:\build\Output"
#>
param(
    [string]$OutputDir = (Join-Path $PSScriptRoot ".." "Output")
)

$ErrorActionPreference = "Stop"

$installerName = "AI_Metadata_Inspector_Setup.exe"
$installerPath = Join-Path $OutputDir $installerName

if (-not (Test-Path -LiteralPath $installerPath)) {
    Write-Host ""
    Write-Host "ERROR: Installer not found." -ForegroundColor Red
    Write-Host "  Expected: $installerPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Build the installer with Inno Setup first, then run this script." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Computing SHA-256 for: $installerPath" -ForegroundColor Cyan

$hash = Get-FileHash -LiteralPath $installerPath -Algorithm SHA256
$hexLower = $hash.Hash.ToLowerInvariant()

# Standard BSD/Linux checksum format: <hash>  <filename>
$checksumLine = "$hexLower  $installerName"

$checksumFile = Join-Path $OutputDir ($installerName + ".sha256")
[System.IO.File]::WriteAllText($checksumFile, $checksumLine + "`n", [System.Text.Encoding]::ASCII)

Write-Host ""
Write-Host "SHA-256 : $hexLower" -ForegroundColor Green
Write-Host "Written : $checksumFile" -ForegroundColor Green
Write-Host ""
Write-Host "Publish both files on the GitHub Release page." -ForegroundColor White
Write-Host "Users can verify with:" -ForegroundColor White
Write-Host "  (Get-FileHash 'AI_Metadata_Inspector_Setup.exe' -Algorithm SHA256).Hash" -ForegroundColor Gray
Write-Host ""
