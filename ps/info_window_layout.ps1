function Add-SimpleCopyFieldRow {
    param(
        [Parameter(Mandatory = $true)] $Parent,
        [Parameter(Mandatory = $true)] [int]$Y,
        [Parameter(Mandatory = $true)] [string]$LabelText,
        [Parameter(Mandatory = $false)] $Value
    )

    $label = New-Object System.Windows.Forms.Label
    $label.Text = $LabelText
    $label.Location = New-Object System.Drawing.Point(0, ($Y + 4))
    $label.Size = New-Object System.Drawing.Size(155, 24)
    $label.BorderStyle = "FixedSingle"
    $label.TextAlign = [System.Drawing.ContentAlignment]::MiddleLeft
    $label.Padding = New-Object System.Windows.Forms.Padding(8, 0, 0, 0)
    $label.BackColor = [System.Drawing.Color]::White
    $label.ForeColor = [System.Drawing.Color]::Black
    $label.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $Parent.Controls.Add($label)

    $tb = New-Object System.Windows.Forms.TextBox
    $tb.Location = New-Object System.Drawing.Point(168, $Y)
    $tb.Size = New-Object System.Drawing.Size(730, 26)
    $tb.ReadOnly = $true
    $tb.Multiline = $false
    $tb.ScrollBars = "None"
    $tb.Text = Normalize-DisplayText $Value ""
    $tb.BackColor = [System.Drawing.Color]::White
    $tb.ForeColor = [System.Drawing.Color]::Black
    $tb.BorderStyle = "FixedSingle"
    $Parent.Controls.Add($tb)

    Add-CopyButton $Parent 916 $Y 100 26 $tb "Copy" | Out-Null
}

function Add-PassSection {
    param(
        [Parameter(Mandatory = $true)] $Parent,
        [Parameter(Mandatory = $true)] [int]$Y,
        [Parameter(Mandatory = $true)] $PassData,
        [Parameter(Mandatory = $true)] [int]$Index
    )

    $section = New-Object System.Windows.Forms.Panel
    $section.Location = New-Object System.Drawing.Point(14, $Y)
    $section.Size = New-Object System.Drawing.Size(1032, 360)
    $section.BackColor = [System.Drawing.Color]::White
    $section.BorderStyle = "FixedSingle"
    $Parent.Controls.Add($section)

    $title = New-Object System.Windows.Forms.Label
    $title.Text = "Sampler Pass $Index"
    $title.Location = New-Object System.Drawing.Point(0, 10)
    $title.Size = New-Object System.Drawing.Size(420, 24)
    $title.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $title.ForeColor = [System.Drawing.Color]::Black
    $title.BackColor = [System.Drawing.Color]::White
    $section.Controls.Add($title)

    $subtitle = New-Object System.Windows.Forms.Label
    $subtitle.Text = Normalize-DisplayText $PassData.label ""
    $subtitle.Location = New-Object System.Drawing.Point(156, 11)
    $subtitle.Size = New-Object System.Drawing.Size(520, 22)
    $subtitle.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $subtitle.ForeColor = [System.Drawing.Color]::DimGray
    $subtitle.BackColor = [System.Drawing.Color]::White
    $section.Controls.Add($subtitle)

    Add-SimpleCopyFieldRow $section 46  "Node ID"             $PassData.node_id
    Add-SimpleCopyFieldRow $section 76  "Type"                $PassData.node_type
    Add-SimpleCopyFieldRow $section 106 "Seed"                $PassData.seed
    Add-SimpleCopyFieldRow $section 136 "Noise Seed"          $PassData.noise_seed
    Add-SimpleCopyFieldRow $section 166 "Add Noise"           $PassData.add_noise
    Add-SimpleCopyFieldRow $section 196 "Denoise"             $PassData.denoise
    Add-SimpleCopyFieldRow $section 226 "Steps"               $PassData.steps
    Add-SimpleCopyFieldRow $section 256 "CFG"                 $PassData.cfg
    Add-SimpleCopyFieldRow $section 286 "Sampler / Scheduler" ((Normalize-DisplayText $PassData.sampler "") + " / " + (Normalize-DisplayText $PassData.scheduler ""))
    Add-SimpleCopyFieldRow $section 316 "Steps / Noise"       ("Start: " + (Normalize-DisplayText $PassData.start_at_step "") + " | End: " + (Normalize-DisplayText $PassData.end_at_step "") + " | Leftover: " + (Normalize-DisplayText $PassData.return_with_leftover_noise ""))

    return [int]($Y + 372)
}

function Show-AIInfoWindow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$JsonPath
    )

    try {
        $data = Get-Content -LiteralPath $JsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Unable to read metadata info data.", "AI Metadata Inspector")
        return
    }

    $fileTypeText = SafeText $data.file_type ""
    $mimeText = SafeText $data.mime ""
    $mediaFpsText = SafeText $data.media_fps ""
    $workflowFpsText = SafeText $data.workflow_fps ""
    $isVideo = ($fileTypeText -match "MP4|MOV|AVI|MKV|WEBM|M4V|VIDEO") -or ($mimeText -match "^video/")
    $hasCleanWorkflowFps = $workflowFpsText -match "^\d+(\.\d+)?$"

    $form = New-Object System.Windows.Forms.Form

    $iconPath = Join-Path $AppDir "icons\app.ico"
    if (Test-Path -LiteralPath $iconPath) {
       $form.Icon = New-Object System.Drawing.Icon($iconPath)
       $form.ShowIcon = $true
    }

    $APP_VERSION = "1.3.3"
    $form.Text = "AI Metadata Inspector v$APP_VERSION"
    $form.StartPosition = "CenterScreen"
    $screenArea = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
    $targetWidth = 1120
    $targetHeight = 1120
    $maxWidth = [Math]::Max(980, ($screenArea.Width - 40))
    $maxHeight = [Math]::Max(820, ($screenArea.Height - 40))
    if ($targetWidth -gt $maxWidth) { $targetWidth = $maxWidth }
    if ($targetHeight -gt $maxHeight) { $targetHeight = $maxHeight }

    $form.Size = New-Object System.Drawing.Size($targetWidth, $targetHeight)
    $form.MinimumSize = New-Object System.Drawing.Size(980, 820)
    $form.BackColor = [System.Drawing.Color]::FromArgb(245, 246, 248)
    $form.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $form.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::None

    $headerHeight = 132
    $contentTop = $headerHeight + 8

    $headerHost = New-Object System.Windows.Forms.Panel
    $headerHost.Location = New-Object System.Drawing.Point(0, 0)
    $headerHost.Size = New-Object System.Drawing.Size($form.ClientSize.Width, $contentTop)
    $headerHost.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
    $headerHost.Padding = New-Object System.Windows.Forms.Padding(6, 6, 12, 4)
    $headerHost.Margin = New-Object System.Windows.Forms.Padding(0)
    $headerHost.BackColor = $form.BackColor
    $form.Controls.Add($headerHost)

    $main = New-Object System.Windows.Forms.FlowLayoutPanel
    $main.Location = New-Object System.Drawing.Point(0, $contentTop)
    $main.Size = New-Object System.Drawing.Size($form.ClientSize.Width, ($form.ClientSize.Height - $contentTop))
    $main.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Bottom -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
    $main.FlowDirection = "TopDown"
    $main.WrapContents = $false
    $main.AutoScroll = $true
    $main.Padding = New-Object System.Windows.Forms.Padding(12)
    $main.BackColor = $form.BackColor
    $main.Margin = New-Object System.Windows.Forms.Padding(0)
    $form.Controls.Add($main)

    $header = New-Object System.Windows.Forms.Panel
    $header.Width = 1060
    $header.Height = 118
    $header.BackColor = [System.Drawing.Color]::White
    $header.BorderStyle = "FixedSingle"
    $header.Location = New-Object System.Drawing.Point(6, 6)
    $headerHost.Controls.Add($header)

    $fileName = New-Object System.Windows.Forms.Label
    $fileName.Text = SafeText $data.file_name "(unknown file)"
    $fileName.Location = New-Object System.Drawing.Point(16, 12)
    $fileName.Size = New-Object System.Drawing.Size(790, 24)
    $fileName.Font = New-Object System.Drawing.Font("Segoe UI Semibold", 10)
    $fileName.ForeColor = [System.Drawing.Color]::Black
    $fileName.BackColor = [System.Drawing.Color]::White
    $header.Controls.Add($fileName)

    $filePathTitle = New-Object System.Windows.Forms.Label
    $filePathTitle.Text = "Path"
    $filePathTitle.Location = New-Object System.Drawing.Point(16, 39)
    $filePathTitle.Size = New-Object System.Drawing.Size(80, 20)
    $filePathTitle.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $filePathTitle.ForeColor = [System.Drawing.Color]::Black
    $filePathTitle.BackColor = [System.Drawing.Color]::White
    $header.Controls.Add($filePathTitle)

    $filePath = New-Object System.Windows.Forms.Label
    $filePath.Text = Normalize-DisplayText $data.file_path ""
    $filePath.Location = New-Object System.Drawing.Point(16, 60)
    $filePath.Size = New-Object System.Drawing.Size(790, 20)
    $filePath.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $filePath.ForeColor = [System.Drawing.Color]::DimGray
    $filePath.BackColor = [System.Drawing.Color]::White
    $filePath.TextAlign = [System.Drawing.ContentAlignment]::TopLeft
    $header.Controls.Add($filePath)

    $headerCopyPositive = New-Object System.Windows.Forms.Button
    $headerCopyPositive.Location = New-Object System.Drawing.Point(16, 86)
    $headerCopyPositive.Size = New-Object System.Drawing.Size(112, 26)
    $headerCopyPositive.Text = "Copy Positive"
    $headerCopyPositive.Add_Click({
        if (Copy-Text $positiveBox.Text) {
            Set-CopiedState $headerCopyPositive "Copy Positive"
        }
    })
    $header.Controls.Add($headerCopyPositive)

    $headerCopyNegative = New-Object System.Windows.Forms.Button
    $headerCopyNegative.Location = New-Object System.Drawing.Point(136, 86)
    $headerCopyNegative.Size = New-Object System.Drawing.Size(112, 26)
    $headerCopyNegative.Text = "Copy Negative"
    $headerCopyNegative.Add_Click({
        if (Copy-Text $negativeBox.Text) {
            Set-CopiedState $headerCopyNegative "Copy Negative"
        }
    })
    $header.Controls.Add($headerCopyNegative)

    $headerCopySeed = New-Object System.Windows.Forms.Button
    $headerCopySeed.Location = New-Object System.Drawing.Point(256, 86)
    $headerCopySeed.Size = New-Object System.Drawing.Size(88, 26)
    $headerCopySeed.Text = "Copy Seed"
    $headerCopySeed.Add_Click({
        if (Copy-Text $data.seed) {
            Set-CopiedState $headerCopySeed "Copy Seed"
        }
    })
    $header.Controls.Add($headerCopySeed)

    $headerCopyAll = New-Object System.Windows.Forms.Button
    $headerCopyAll.Location = New-Object System.Drawing.Point(352, 86)
    $headerCopyAll.Size = New-Object System.Drawing.Size(88, 26)
    $headerCopyAll.Text = "Copy All"
    $headerCopyAll.Add_Click({
        if (Copy-Text $data.copy_all) {
            Set-CopiedState $headerCopyAll "Copy All"
        }
    })
    $header.Controls.Add($headerCopyAll)

    $headerClose = New-Object System.Windows.Forms.Button
    $headerClose.Location = New-Object System.Drawing.Point(448, 86)
    $headerClose.Size = New-Object System.Drawing.Size(72, 26)
    $headerClose.Text = "Close"
    $headerClose.Add_Click({ $form.Close() })
    $header.Controls.Add($headerClose)

    $previewFrame = New-Object System.Windows.Forms.Panel
    $previewFrame.Location = New-Object System.Drawing.Point(830, 12)
    $previewFrame.Size = New-Object System.Drawing.Size(200, 94)
    $previewFrame.BackColor = [System.Drawing.Color]::FromArgb(248, 248, 248)
    $previewFrame.BorderStyle = "FixedSingle"
    $header.Controls.Add($previewFrame)

    $previewLabel = New-Object System.Windows.Forms.Label
    $previewLabel.Text = "Preview"
    $previewLabel.Location = New-Object System.Drawing.Point(0, 0)
    $previewLabel.Size = New-Object System.Drawing.Size(198, 20)
    $previewLabel.Font = New-Object System.Drawing.Font("Segoe UI", 8.5, [System.Drawing.FontStyle]::Bold)
    $previewLabel.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
    $previewLabel.ForeColor = [System.Drawing.Color]::Black
    $previewLabel.BackColor = [System.Drawing.Color]::FromArgb(240, 240, 240)
    $previewFrame.Controls.Add($previewLabel)

    $picture = New-Object System.Windows.Forms.PictureBox
    $picture.Location = New-Object System.Drawing.Point(6, 24)
    $picture.Size = New-Object System.Drawing.Size(186, 64)
    $picture.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::Zoom
    $picture.BackColor = [System.Drawing.Color]::White
    $previewFrame.Controls.Add($picture)

    $previewStatus = New-Object System.Windows.Forms.Label
    $previewStatus.Text = "Loading preview..."
    $previewStatus.Location = New-Object System.Drawing.Point(6, 24)
    $previewStatus.Size = New-Object System.Drawing.Size(186, 64)
    $previewStatus.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
    $previewStatus.ForeColor = [System.Drawing.Color]::DimGray
    $previewStatus.BackColor = [System.Drawing.Color]::White
    $previewFrame.Controls.Add($previewStatus)
    $previewStatus.BringToFront()

    $fileInfoHeight = 140
    if ($isVideo -and -not [string]::IsNullOrWhiteSpace($mediaFpsText)) {
        $fileInfoHeight = 204
    } elseif ($isVideo) {
        $fileInfoHeight = 172
    }

    $fileInfo = New-Card "FILE INFORMATION" $fileInfoHeight
    Add-FieldRow $fileInfo 56  "Type"       $data.file_type "Copy" $false
    Add-FieldRow $fileInfo 88  "File Size"  $data.file_size "Copy" $false
    if ($isVideo) {
        Add-FieldRow $fileInfo 120 "Duration"   $data.duration "Copy" $false
    }
    if ($isVideo -and -not [string]::IsNullOrWhiteSpace($mediaFpsText)) {
        Add-FieldRow $fileInfo 152 "Media FPS"  $data.media_fps "Copy" $false
    }
    $main.Controls.Add($fileInfo)

    $modelCardHeight = 210
    if ($isVideo) {
        $modelCardHeight = 242
    }
    if ($hasCleanWorkflowFps) {
        $modelCardHeight = if ($isVideo) { 274 } else { 242 }
    }

    $modelCard = New-Card "MODEL & OUTPUT" $modelCardHeight
    Add-FieldRow $modelCard 56  "Model"            $data.model "Copy" $true
    Add-FieldRow $modelCard 88  "CLIP"             $data.clips "Copy" $false
    Add-FieldRow $modelCard 120 "VAE"              $data.vae "Copy" $false
    Add-FieldRow $modelCard 152 "File Dimensions"  $data.file_dimensions "Copy" $false
    if ($isVideo) {
        Add-FieldRow $modelCard 184 "Length / Frames"  $data.length_frames "Copy" $false
    }
    if ($hasCleanWorkflowFps) {
        $workflowFpsTop = if ($isVideo) { 216 } else { 184 }
        Add-FieldRow $modelCard $workflowFpsTop "Workflow FPS" $data.workflow_fps "Copy" $false
    }
    $main.Controls.Add($modelCard)

    $positiveHeight = Get-FastPromptHeight $data.positive
    $positiveCard = New-Card "Positive Prompt" (56 + $positiveHeight + 20)
    $positiveBox = New-ReadOnlyTextBox 14 56 891 $positiveHeight $data.positive $true
    $positiveCard.Controls.Add($positiveBox)
    Add-CopyButton $positiveCard 920 56 100 30 $positiveBox "Copy" | Out-Null
    $main.Controls.Add($positiveCard)

    $negativeHeight = Get-FastPromptHeight $data.negative
    $negativeCard = New-Card "Negative Prompt" (56 + $negativeHeight + 20)
    $negativeBox = New-ReadOnlyTextBox 14 56 891 $negativeHeight $data.negative $true
    $negativeCard.Controls.Add($negativeBox)
    Add-CopyButton $negativeCard 920 56 100 30 $negativeBox "Copy" | Out-Null
    $main.Controls.Add($negativeCard)

    $gen = New-Card "GENERATION SETTINGS" 370
    Add-FieldRow $gen 56  "Seed"         $data.seed "Copy" $true
    Add-FieldRow $gen 88  "Seed Source"  $data.seed_source "Copy" $false
    Add-FieldRow $gen 120 "Noise Seed"   $data.noise_seed "Copy" $true
    Add-FieldRow $gen 152 "Denoise"      $data.denoise "Copy" $false
    Add-FieldRow $gen 184 "Add Noise"    $data.add_noise "Copy" $false
    Add-FieldRow $gen 216 "Steps"        $data.steps "Copy" $false
    Add-FieldRow $gen 248 "CFG"          $data.cfg "Copy" $false
    Add-FieldRow $gen 280 "Sampler"      $data.sampler "Copy" $true
    Add-FieldRow $gen 312 "Scheduler"    $data.scheduler "Copy" $false
    $main.Controls.Add($gen)

    $form.Add_Shown({
        $deferredTimer = New-Object System.Windows.Forms.Timer
        $deferredTimer.Interval = 1
        $deferredTimer.Add_Tick({
            param($sender, $e)
            $sender.Stop()
            try {
                $samplers = @()
                if ($data.samplers_details -is [System.Array]) {
                    $samplers = $data.samplers_details
                } elseif ($null -ne $data.samplers_details) {
                    $samplers = @($data.samplers_details)
                }

                if ($samplers.Count -gt 0) {
                    $passesCardHeight = 56 + ($samplers.Count * 372) + 10
                    $passesCard = New-Card "SAMPLER PASSES" $passesCardHeight
                    $currentY = 56
                    $i = 1
                    foreach ($pass in $samplers) {
                        $currentY = [int](Add-PassSection $passesCard $currentY $pass $i)
                        $i++
                    }
                    $main.Controls.Add($passesCard)
                }

                $loraText = ""
                if ($data.loras -is [System.Array]) {
                    $loraText = ($data.loras -join "`r`n")
                } else {
                    $loraText = Normalize-DisplayText $data.loras ""
                }

                $loraCard = New-Card "LoRAs" 226
                $loraBox = New-ReadOnlyTextBox 14 56 891 136 $loraText $true
                $loraCard.Controls.Add($loraBox)
                Add-CopyButton $loraCard 920 56 100 30 $loraBox "Copy" | Out-Null
                $main.Controls.Add($loraCard)

                $tagsCard = New-Card "METADATA SOURCES" 226
                $tagsBox = New-ReadOnlyTextBox 14 56 891 136 $data.found_tags $true
                $tagsCard.Controls.Add($tagsBox)
                Add-CopyButton $tagsCard 920 56 100 30 $tagsBox "Copy" | Out-Null
                    $main.Controls.Add($tagsCard)
                    $main.AutoScrollPosition = New-Object System.Drawing.Point(0, 0)

                try {
                    $previewImage = Try-GetPreviewImage (SafeText $data.file_path "") 360 220
                } catch {
                    $previewImage = $null
                }

                if ($previewImage -ne $null) {
                    $picture.Image = $previewImage
                    $previewStatus.Visible = $false
                } else {
                    $previewStatus.Text = "Preview unavailable"
                }
            } finally {
                try { $sender.Dispose() } catch {}
            }
        })
        $deferredTimer.Start()
    })

    $form.Add_FormClosed({
        try {
            if ($picture.Image -ne $null) {
                $picture.Image.Dispose()
            }
        } catch {
        }
    })

    [void]$form.ShowDialog()
}
