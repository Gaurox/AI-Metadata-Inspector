#Requires -Version 5.1
<#
.SYNOPSIS
    Generates the release traceability manifest for an exact source checkout.

.DESCRIPTION
    Records the requested product version, current Git commit, bundled component
    versions and SHA-256 values, plus the installer hash when it is present.
    Publish this JSON file with the installer and its .sha256 sidecar.
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$')]
    [string]$Version,

    [string]$OutputDir = (Join-Path $PSScriptRoot "..\Output")
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$manifestPath = Join-Path $OutputDir "AI_Metadata_Inspector_release_manifest.json"

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

function Get-ComponentRecord {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string[]]$VersionArguments,
        [Parameter(Mandatory = $true)][string]$VersionPattern
    )

    $absolutePath = Join-Path $projectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
        throw "Bundled component not found: $RelativePath"
    }

    $versionOutput = @(& $absolutePath @VersionArguments 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read component version: $RelativePath"
    }

    $versionLine = $versionOutput |
        ForEach-Object { $_.ToString().Trim() } |
        Where-Object { $_ -match $VersionPattern } |
        Select-Object -First 1
    if (-not $versionLine) {
        throw "Unable to parse component version: $RelativePath"
    }

    [ordered]@{
        path = $RelativePath
        version = $versionLine
        sha256 = (Get-FileHash -LiteralPath $absolutePath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$gitCommit = (& git -C $projectRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or -not $gitCommit) {
    throw "Unable to determine the source Git commit."
}

$sourceStatus = @(& git -C $projectRoot status --porcelain)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to determine the source working-tree status."
}
$sourceTreeDirty = $sourceStatus.Count -gt 0

$manifest = [ordered]@{
    schema_version = 1
    product_version = $Version
    generated_utc = [DateTime]::UtcNow.ToString("o")
    source_commit = $gitCommit
    source_tree_dirty = $sourceTreeDirty
    components = @(
        (Get-ComponentRecord -RelativePath "ffmpeg.exe" -VersionArguments @("-version") -VersionPattern "^ffmpeg version\s+"),
        (Get-ComponentRecord -RelativePath "exiftool.exe" -VersionArguments @("-ver") -VersionPattern "^\d+\.\d+"),
        (Get-ComponentRecord -RelativePath "python_embeded\python.exe" -VersionArguments @("--version") -VersionPattern "^Python\s+")
    )
}

$installerPath = Join-Path $OutputDir "AI_Metadata_Inspector_Setup.exe"
if (Test-Path -LiteralPath $installerPath -PathType Leaf) {
    $manifest.installer = [ordered]@{
        file = [IO.Path]::GetFileName($installerPath)
        sha256 = (Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$json = $manifest | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText($manifestPath, $json + [Environment]::NewLine, $utf8NoBom)
Write-Host "Written: $manifestPath" -ForegroundColor Green
