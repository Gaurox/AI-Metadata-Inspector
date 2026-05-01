param(
    [Parameter(Mandatory = $true)]
    [string]$JsonPath,

    [Parameter(Mandatory = $true)]
    [string]$AppDir
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

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
