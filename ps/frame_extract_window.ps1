param(
    [Parameter(Mandatory = $true)]
    [string]$VideoPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputFolder,

    [Parameter(Mandatory = $true)]
    [int]$FfmpegProcessId,

    [Parameter(Mandatory = $false)]
    [int]$ExpectedFrameCount = 0
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Test-TargetProcessAlive {
    param(
        [Parameter(Mandatory = $true)]
        [int]$TargetProcessId
    )

    try {
        $proc = Get-Process -Id $TargetProcessId -ErrorAction Stop
        return ($null -ne $proc -and -not $proc.HasExited)
    }
    catch {
        return $false
    }
}

function Stop-TargetProcessSafe {
    param(
        [Parameter(Mandatory = $true)]
        [int]$TargetProcessId
    )

    try {
        $proc = Get-Process -Id $TargetProcessId -ErrorAction Stop
        if ($null -ne $proc -and -not $proc.HasExited) {
            Stop-Process -Id $TargetProcessId -Force -ErrorAction Stop
            return $true
        }
    }
    catch {
    }

    return $false
}

function Get-ExtractedFrameCount {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FolderPath
    )

    try {
        if (-not (Test-Path -LiteralPath $FolderPath)) {
            return 0
        }

        $files = Get-ChildItem -LiteralPath $FolderPath -Filter 'frame_*.png' -File -ErrorAction Stop
        return @($files).Count
    }
    catch {
        return 0
    }
}

function Update-ProgressUi {
    param(
        [Parameter(Mandatory = $true)]
        [int]$CurrentFrameCount,

        [Parameter(Mandatory = $true)]
        [bool]$IsCompleted
    )

    $displayCount = $CurrentFrameCount
    if ($displayCount -lt 0) {
        $displayCount = 0
    }

    if ($ExpectedFrameCount -gt 0) {
        $safeMax = $ExpectedFrameCount
        if ($safeMax -lt 1) {
            $safeMax = 1
        }

        $clampedValue = $displayCount
        if ($clampedValue -gt $safeMax) {
            $clampedValue = $safeMax
        }

        $progressBar.Style = [System.Windows.Forms.ProgressBarStyle]::Continuous
        $progressBar.Minimum = 0
        $progressBar.Maximum = $safeMax
        $progressBar.Value = $clampedValue

        $percent = [int][Math]::Round(($clampedValue * 100.0) / $safeMax)
        if ($percent -gt 100) {
            $percent = 100
        }

        if ($IsCompleted) {
            $labelStatus.Text = "Extraction completed."
        }
        else {
            $labelStatus.Text = "Extraction in progress..."
        }

        $labelProgress.Text = "$displayCount / $ExpectedFrameCount frames ($percent%)"
        return
    }

    $progressBar.Style = [System.Windows.Forms.ProgressBarStyle]::Marquee
    $progressBar.MarqueeAnimationSpeed = 25

    if ($IsCompleted) {
        $labelStatus.Text = "Extraction completed."
    }
    else {
        $labelStatus.Text = "Extraction in progress..."
    }

    $labelProgress.Text = "$displayCount frames extracted"
}

$form = New-Object System.Windows.Forms.Form
$form.Text = "AI Metadata Inspector - Extract Frames"
$form.StartPosition = "CenterScreen"
$form.Size = New-Object System.Drawing.Size(660, 285)
$form.MinimumSize = New-Object System.Drawing.Size(660, 285)
$form.MaximumSize = New-Object System.Drawing.Size(660, 285)
$form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.TopMost = $true

$labelTitle = New-Object System.Windows.Forms.Label
$labelTitle.Location = New-Object System.Drawing.Point(20, 15)
$labelTitle.Size = New-Object System.Drawing.Size(600, 24)
$labelTitle.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$labelTitle.Text = "Extracting PNG frames from video..."
$form.Controls.Add($labelTitle)

$labelVideoCaption = New-Object System.Windows.Forms.Label
$labelVideoCaption.Location = New-Object System.Drawing.Point(20, 50)
$labelVideoCaption.Size = New-Object System.Drawing.Size(95, 20)
$labelVideoCaption.Text = "Video:"
$form.Controls.Add($labelVideoCaption)

$textVideo = New-Object System.Windows.Forms.TextBox
$textVideo.Location = New-Object System.Drawing.Point(120, 47)
$textVideo.Size = New-Object System.Drawing.Size(500, 23)
$textVideo.ReadOnly = $true
$textVideo.Text = $VideoPath
$form.Controls.Add($textVideo)

$labelFolderCaption = New-Object System.Windows.Forms.Label
$labelFolderCaption.Location = New-Object System.Drawing.Point(20, 82)
$labelFolderCaption.Size = New-Object System.Drawing.Size(95, 20)
$labelFolderCaption.Text = "Output folder:"
$form.Controls.Add($labelFolderCaption)

$textFolder = New-Object System.Windows.Forms.TextBox
$textFolder.Location = New-Object System.Drawing.Point(120, 79)
$textFolder.Size = New-Object System.Drawing.Size(500, 23)
$textFolder.ReadOnly = $true
$textFolder.Text = $OutputFolder
$form.Controls.Add($textFolder)

$labelStatusCaption = New-Object System.Windows.Forms.Label
$labelStatusCaption.Location = New-Object System.Drawing.Point(20, 118)
$labelStatusCaption.Size = New-Object System.Drawing.Size(95, 20)
$labelStatusCaption.Text = "Status:"
$form.Controls.Add($labelStatusCaption)

$labelStatus = New-Object System.Windows.Forms.Label
$labelStatus.Location = New-Object System.Drawing.Point(120, 118)
$labelStatus.Size = New-Object System.Drawing.Size(420, 20)
$labelStatus.Text = "Extraction in progress..."
$form.Controls.Add($labelStatus)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(120, 148)
$progressBar.Size = New-Object System.Drawing.Size(500, 22)
if ($ExpectedFrameCount -gt 0) {
    $progressBar.Style = [System.Windows.Forms.ProgressBarStyle]::Continuous
    $progressBar.Minimum = 0
    $progressBar.Maximum = $ExpectedFrameCount
    $progressBar.Value = 0
}
else {
    $progressBar.Style = [System.Windows.Forms.ProgressBarStyle]::Marquee
    $progressBar.MarqueeAnimationSpeed = 25
}
$form.Controls.Add($progressBar)

$labelProgress = New-Object System.Windows.Forms.Label
$labelProgress.Location = New-Object System.Drawing.Point(120, 176)
$labelProgress.Size = New-Object System.Drawing.Size(420, 20)
if ($ExpectedFrameCount -gt 0) {
    $labelProgress.Text = "0 / $ExpectedFrameCount frames (0%)"
}
else {
    $labelProgress.Text = "0 frames extracted"
}
$form.Controls.Add($labelProgress)

$buttonCancel = New-Object System.Windows.Forms.Button
$buttonCancel.Location = New-Object System.Drawing.Point(505, 205)
$buttonCancel.Size = New-Object System.Drawing.Size(115, 30)
$buttonCancel.Text = "Cancel"
$form.Controls.Add($buttonCancel)

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 500

$script:WasCancelled = $false
$script:CompletedNormally = $false
$script:IsClosingInternally = $false

$buttonCancel.Add_Click({
    $buttonCancel.Enabled = $false
    $labelStatus.Text = "Cancelling extraction..."

    $stopped = Stop-TargetProcessSafe -TargetProcessId $FfmpegProcessId

    if ($stopped) {
        $script:WasCancelled = $true
        $script:IsClosingInternally = $true
        $labelStatus.Text = "Extraction cancelled."
        $timer.Stop()
        $form.Close()
        return
    }

    if (-not (Test-TargetProcessAlive -TargetProcessId $FfmpegProcessId)) {
        $script:CompletedNormally = $true
        $script:IsClosingInternally = $true
        Update-ProgressUi -CurrentFrameCount (Get-ExtractedFrameCount -FolderPath $OutputFolder) -IsCompleted $true
        $timer.Stop()
        $form.Close()
        return
    }

    $buttonCancel.Enabled = $true
    $labelStatus.Text = "Unable to cancel extraction."
})

$timer.Add_Tick({
    $currentFrameCount = Get-ExtractedFrameCount -FolderPath $OutputFolder

    if (-not (Test-TargetProcessAlive -TargetProcessId $FfmpegProcessId)) {
        $script:CompletedNormally = $true
        $script:IsClosingInternally = $true
        Update-ProgressUi -CurrentFrameCount $currentFrameCount -IsCompleted $true
        $timer.Stop()
        $form.Close()
        return
    }

    Update-ProgressUi -CurrentFrameCount $currentFrameCount -IsCompleted $false
})

$form.Add_Shown({
    Update-ProgressUi -CurrentFrameCount (Get-ExtractedFrameCount -FolderPath $OutputFolder) -IsCompleted $false
    $timer.Start()
})

$form.Add_FormClosing({
    param($sender, $e)

    if ($script:IsClosingInternally) {
        return
    }

    if (Test-TargetProcessAlive -TargetProcessId $FfmpegProcessId) {
        $answer = [System.Windows.Forms.MessageBox]::Show(
            "Extraction is still running.`r`n`r`nDo you want to cancel it?",
            "AI Metadata Inspector",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Question
        )

        if ($answer -eq [System.Windows.Forms.DialogResult]::Yes) {
            $null = Stop-TargetProcessSafe -TargetProcessId $FfmpegProcessId
            $script:WasCancelled = $true
            $script:IsClosingInternally = $true
            $timer.Stop()
            return
        }

        $e.Cancel = $true
    }
})

[void]$form.ShowDialog()

if ($script:WasCancelled) {
    exit 1223
}

if ($script:CompletedNormally) {
    exit 0
}

if (-not (Test-TargetProcessAlive -TargetProcessId $FfmpegProcessId)) {
    exit 0
}

exit 1
