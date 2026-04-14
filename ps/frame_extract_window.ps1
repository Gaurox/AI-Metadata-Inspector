param(
    [Parameter(Mandatory = $true)]
    [string]$VideoPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputFolder,

    [Parameter(Mandatory = $true)]
    [int]$FfmpegProcessId
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

$form = New-Object System.Windows.Forms.Form
$form.Text = "AI Metadata Inspector - Extract Frames"
$form.StartPosition = "CenterScreen"
$form.Size = New-Object System.Drawing.Size(660, 235)
$form.MinimumSize = New-Object System.Drawing.Size(660, 235)
$form.MaximumSize = New-Object System.Drawing.Size(660, 235)
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

$buttonCancel = New-Object System.Windows.Forms.Button
$buttonCancel.Location = New-Object System.Drawing.Point(505, 150)
$buttonCancel.Size = New-Object System.Drawing.Size(115, 30)
$buttonCancel.Text = "Cancel"
$form.Controls.Add($buttonCancel)

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 800

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
        $labelStatus.Text = "Extraction already completed."
        $timer.Stop()
        $form.Close()
        return
    }

    $buttonCancel.Enabled = $true
    $labelStatus.Text = "Unable to cancel extraction."
})

$timer.Add_Tick({
    if (-not (Test-TargetProcessAlive -TargetProcessId $FfmpegProcessId)) {
        $script:CompletedNormally = $true
        $script:IsClosingInternally = $true
        $labelStatus.Text = "Extraction completed."
        $timer.Stop()
        $form.Close()
    }
})

$form.Add_Shown({
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