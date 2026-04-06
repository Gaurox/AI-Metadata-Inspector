function Add-SimpleCopyFieldRow {
    param(
        [Parameter(Mandatory = $true)] $Parent,
        [Parameter(Mandatory = $true)] [int]$Y,
        [Parameter(Mandatory = $true)] [string]$LabelText,
        [Parameter(Mandatory = $false)] $Value
    )

    $label = New-Object System.Windows.Forms.Label
    $label.Text = $LabelText
    $label.Location = New-Object System.Drawing.Point(14, ($Y + 4))
    $label.Size = New-Object System.Drawing.Size(150, 24)
    $label.BorderStyle = "FixedSingle"
    $label.TextAlign = [System.Drawing.ContentAlignment]::MiddleLeft
    $label.Padding = New-Object System.Windows.Forms.Padding(8, 0, 0, 0)
    $label.BackColor = [System.Drawing.Color]::White
    $label.ForeColor = [System.Drawing.Color]::Black
    $label.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $Parent.Controls.Add($label)

    $tb = New-Object System.Windows.Forms.TextBox
    $tb.Location = New-Object System.Drawing.Point(178, $Y)
    $tb.Size = New-Object System.Drawing.Size(730, 30)
    $tb.ReadOnly = $true
    $tb.Multiline = $false
    $tb.ScrollBars = "None"
    $tb.Text = Normalize-DisplayText $Value ""
    $tb.BackColor = [System.Drawing.Color]::White
    $tb.ForeColor = [System.Drawing.Color]::Black
    $tb.BorderStyle = "FixedSingle"
    $Parent.Controls.Add($tb)

    Add-CopyButton $Parent 928 $Y 100 30 $tb "Copy" | Out-Null
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
    $section.Size = New-Object System.Drawing.Size(1014, 392)
    $section.BackColor = [System.Drawing.Color]::White
    $section.BorderStyle = "FixedSingle"
    $Parent.Controls.Add($section)

    $title = New-Object System.Windows.Forms.Label
    $title.Text = "Sampler Pass $Index"
    $title.Location = New-Object System.Drawing.Point(10, 10)
    $title.Size = New-Object System.Drawing.Size(420, 24)
    $title.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $title.ForeColor = [System.Drawing.Color]::Black
    $title.BackColor = [System.Drawing.Color]::White
    $section.Controls.Add($title)

    $subtitle = New-Object System.Windows.Forms.Label
    $subtitle.Text = Normalize-DisplayText $PassData.label ""
    $subtitle.Location = New-Object System.Drawing.Point(170, 11)
    $subtitle.Size = New-Object System.Drawing.Size(520, 22)
    $subtitle.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $subtitle.ForeColor = [System.Drawing.Color]::DimGray
    $subtitle.BackColor = [System.Drawing.Color]::White
    $section.Controls.Add($subtitle)

    Add-SimpleCopyFieldRow $section 46  "Node ID"             $PassData.node_id
    Add-SimpleCopyFieldRow $section 78  "Type"                $PassData.node_type
    Add-SimpleCopyFieldRow $section 110 "Seed"                $PassData.seed
    Add-SimpleCopyFieldRow $section 142 "Noise Seed"          $PassData.noise_seed
    Add-SimpleCopyFieldRow $section 174 "Add Noise"           $PassData.add_noise
    Add-SimpleCopyFieldRow $section 206 "Denoise"             $PassData.denoise
    Add-SimpleCopyFieldRow $section 238 "Steps"               $PassData.steps
    Add-SimpleCopyFieldRow $section 270 "CFG"                 $PassData.cfg
    Add-SimpleCopyFieldRow $section 302 "Sampler / Scheduler" ((Normalize-DisplayText $PassData.sampler "") + " / " + (Normalize-DisplayText $PassData.scheduler ""))
    Add-SimpleCopyFieldRow $section 334 "Steps / Noise"       ("Start: " + (Normalize-DisplayText $PassData.start_at_step "") + " | End: " + (Normalize-DisplayText $PassData.end_at_step "") + " | Leftover: " + (Normalize-DisplayText $PassData.return_with_leftover_noise ""))

    return [int]($Y + 404)
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

    $form = New-Object System.Windows.Forms.Form

    $iconPath = Join-Path $AppDir "icons\info.ico"
    if (Test-Path -LiteralPath $iconPath) {
       $form.Icon = New-Object System.Drawing.Icon($iconPath)
       $form.ShowIcon = $true
    }

    $APP_VERSION = "1.1.0"
    $form.Text = "AI Metadata Inspector v$APP_VERSION"
    $form.StartPosition = "CenterScreen"
    $form.Size = New-Object System.Drawing.Size(1120, 1120)
    $form.MinimumSize = New-Object System.Drawing.Size(980, 820)
    $form.BackColor = [System.Drawing.Color]::FromArgb(245, 246, 248)
    $form.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $form.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::None

    $main = New-Object System.Windows.Forms.FlowLayoutPanel
    $main.Dock = "Fill"
    $main.FlowDirection = "TopDown"
    $main.WrapContents = $false
    $main.AutoScroll = $true
    $main.Padding = New-Object System.Windows.Forms.Padding(12)
    $main.BackColor = $form.BackColor
    $form.Controls.Add($main)

    $header = New-Card "File" 196

    $fileName = New-Object System.Windows.Forms.Label
    $fileName.Text = SafeText $data.file_name "(unknown file)"
    $fileName.Location = New-Object System.Drawing.Point(14, 58)
    $fileName.Size = New-Object System.Drawing.Size(790, 24)
    $fileName.Font = New-Object System.Drawing.Font("Segoe UI Semibold", 10)
    $fileName.ForeColor = [System.Drawing.Color]::Black
    $fileName.BackColor = [System.Drawing.Color]::White
    $header.Controls.Add($fileName)

    $filePathTitle = New-Object System.Windows.Forms.Label
    $filePathTitle.Text = "Path"
    $filePathTitle.Location = New-Object System.Drawing.Point(14, 90)
    $filePathTitle.Size = New-Object System.Drawing.Size(80, 20)
    $filePathTitle.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $filePathTitle.ForeColor = [System.Drawing.Color]::Black
    $filePathTitle.BackColor = [System.Drawing.Color]::White
    $header.Controls.Add($filePathTitle)

    $filePath = New-Object System.Windows.Forms.Label
    $filePath.Text = Normalize-DisplayText $data.file_path ""
    $filePath.Location = New-Object System.Drawing.Point(14, 112)
    $filePath.Size = New-Object System.Drawing.Size(790, 58)
    $filePath.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $filePath.ForeColor = [System.Drawing.Color]::DimGray
    $filePath.BackColor = [System.Drawing.Color]::White
    $filePath.TextAlign = [System.Drawing.ContentAlignment]::TopLeft
    $header.Controls.Add($filePath)

    $previewFrame = New-Object System.Windows.Forms.Panel
    $previewFrame.Location = New-Object System.Drawing.Point(830, 58)
    $previewFrame.Size = New-Object System.Drawing.Size(200, 112)
    $previewFrame.BackColor = [System.Drawing.Color]::FromArgb(248, 248, 248)
    $previewFrame.BorderStyle = "FixedSingle"
    $header.Controls.Add($previewFrame)

    $previewLabel = New-Object System.Windows.Forms.Label
    $previewLabel.Text = "Preview"
    $previewLabel.Location = New-Object System.Drawing.Point(0, 0)
    $previewLabel.Size = New-Object System.Drawing.Size(198, 24)
    $previewLabel.Font = New-Object System.Drawing.Font("Segoe UI", 8.5, [System.Drawing.FontStyle]::Bold)
    $previewLabel.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
    $previewLabel.ForeColor = [System.Drawing.Color]::Black
    $previewLabel.BackColor = [System.Drawing.Color]::FromArgb(240, 240, 240)
    $previewFrame.Controls.Add($previewLabel)

    $picture = New-Object System.Windows.Forms.PictureBox
    $picture.Location = New-Object System.Drawing.Point(6, 30)
    $picture.Size = New-Object System.Drawing.Size(186, 74)
    $picture.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::Zoom
    $picture.BackColor = [System.Drawing.Color]::White
    $previewFrame.Controls.Add($picture)

    $previewImage = $null
    try {
        $previewImage = Try-GetPreviewImage (SafeText $data.file_path "") 360 220
    } catch {
        $previewImage = $null
    }

    if ($previewImage -ne $null) {
        $picture.Image = $previewImage
    } else {
        $fallback = New-Object System.Windows.Forms.Label
        $fallback.Text = "Preview unavailable"
        $fallback.Location = New-Object System.Drawing.Point(6, 30)
        $fallback.Size = New-Object System.Drawing.Size(186, 74)
        $fallback.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
        $fallback.ForeColor = [System.Drawing.Color]::DimGray
        $fallback.BackColor = [System.Drawing.Color]::White
        $previewFrame.Controls.Add($fallback)
        $fallback.BringToFront()
    }

    $main.Controls.Add($header)

    $fileInfo = New-Card "FILE INFORMATION" 236
    Add-FieldRow $fileInfo 56  "Type"       $data.file_type
    Add-FieldRow $fileInfo 88  "MIME"       $data.mime
    Add-FieldRow $fileInfo 120 "File Size"  $data.file_size
    Add-FieldRow $fileInfo 152 "Duration"   $data.duration
    Add-FieldRow $fileInfo 184 "Media FPS"  $data.media_fps
    $main.Controls.Add($fileInfo)

    $positiveHeight = Get-AutoHeight $data.positive 891
    $positiveCard = New-Card "Positive Prompt" (56 + $positiveHeight + 20)
    $positiveBox = New-ReadOnlyTextBox 14 56 891 $positiveHeight $data.positive $true
    $positiveCard.Controls.Add($positiveBox)
    Add-CopyButton $positiveCard 920 56 100 30 $positiveBox "Copy" | Out-Null
    $main.Controls.Add($positiveCard)

    $negativeHeight = Get-AutoHeight $data.negative 891
    $negativeCard = New-Card "Negative Prompt" (56 + $negativeHeight + 20)
    $negativeBox = New-ReadOnlyTextBox 14 56 891 $negativeHeight $data.negative $true
    $negativeCard.Controls.Add($negativeBox)
    Add-CopyButton $negativeCard 920 56 100 30 $negativeBox "Copy" | Out-Null
    $main.Controls.Add($negativeCard)

    $gen = New-Card "GENERATION SETTINGS" 402
    Add-FieldRow $gen 56  "Seed"         $data.seed
    Add-FieldRow $gen 88  "Seed Source"  $data.seed_source
    Add-FieldRow $gen 120 "Noise Seed"   $data.noise_seed
    Add-FieldRow $gen 152 "Denoise"      $data.denoise
    Add-FieldRow $gen 184 "Add Noise"    $data.add_noise
    Add-FieldRow $gen 216 "Steps"        $data.steps
    Add-FieldRow $gen 248 "CFG"          $data.cfg
    Add-FieldRow $gen 280 "Sampler"      $data.sampler
    Add-FieldRow $gen 312 "Scheduler"    $data.scheduler
    Add-FieldRow $gen 344 "Source Tag"   $data.source_tag
    $main.Controls.Add($gen)

    $samplers = @()
    if ($data.samplers_details -is [System.Array]) {
        $samplers = $data.samplers_details
    } elseif ($null -ne $data.samplers_details) {
        $samplers = @($data.samplers_details)
    }

    if ($samplers.Count -gt 0) {
        $passesCardHeight = 56 + ($samplers.Count * 404) + 10
        $passesCard = New-Card "SAMPLER PASSES" $passesCardHeight
        $currentY = 56
        $i = 1
        foreach ($pass in $samplers) {
            $currentY = [int](Add-PassSection $passesCard $currentY $pass $i)
            $i++
        }
        $main.Controls.Add($passesCard)
    }

    $modelCard = New-Card "MODEL & OUTPUT" 306
    Add-FieldRow $modelCard 56  "Model"            $data.model
    Add-FieldRow $modelCard 88  "CLIP"             $data.clips
    Add-FieldRow $modelCard 120 "VAE"              $data.vae
    Add-FieldRow $modelCard 152 "Workflow Size"    $data.workflow_size
    Add-FieldRow $modelCard 184 "File Dimensions"  $data.file_dimensions
    Add-FieldRow $modelCard 216 "Length / Frames"  $data.length_frames
    Add-FieldRow $modelCard 248 "Workflow FPS"     $data.workflow_fps
    $main.Controls.Add($modelCard)

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

    $bottom = New-Card "Actions" 102

    $copyAll = New-Object System.Windows.Forms.Button
    $copyAll.Location = New-Object System.Drawing.Point(14, 56)
    $copyAll.Size = New-Object System.Drawing.Size(120, 30)
    $copyAll.Text = "Copy All"
    $copyAll.Add_Click({
        if (Copy-Text $data.copy_all) {
            Set-CopiedState $copyAll "Copy All"
        }
    })
    $bottom.Controls.Add($copyAll)

    $closeBtn = New-Object System.Windows.Forms.Button
    $closeBtn.Location = New-Object System.Drawing.Point(148, 56)
    $closeBtn.Size = New-Object System.Drawing.Size(120, 30)
    $closeBtn.Text = "Close"
    $closeBtn.Add_Click({ $form.Close() })
    $bottom.Controls.Add($closeBtn)

    $copyPrompts = New-Object System.Windows.Forms.Button
    $copyPrompts.Location = New-Object System.Drawing.Point(282, 56)
    $copyPrompts.Size = New-Object System.Drawing.Size(180, 30)
    $copyPrompts.Text = "Copy Prompts"
    $copyPrompts.Add_Click({
        $combined = (Normalize-DisplayText $positiveBox.Text "") + "`r`n`r`n" + (Normalize-DisplayText $negativeBox.Text "")
        if (Copy-Text $combined) {
            Set-CopiedState $copyPrompts "Copy Prompts"
        }
    })
    $bottom.Controls.Add($copyPrompts)

    $main.Controls.Add($bottom)

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