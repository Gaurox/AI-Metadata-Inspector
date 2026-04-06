Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$script:ThumbnailCode = @"
using System;
using System.Drawing;
using System.Runtime.InteropServices;

public static class ShellThumbnail
{
    [ComImport]
    [Guid("bcc18b79-ba16-442f-80c4-8a59c30c463b")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IShellItemImageFactory
    {
        void GetImage(SIZE size, SIIGBF flags, out IntPtr phbm);
    }

    [StructLayout(LayoutKind.Sequential)]
    struct SIZE
    {
        public int cx;
        public int cy;
    }

    [Flags]
    enum SIIGBF
    {
        ResizeToFit = 0x00,
        BiggerSizeOk = 0x01,
        MemoryOnly = 0x02,
        IconOnly = 0x04,
        ThumbnailOnly = 0x08,
        InCacheOnly = 0x10,
        CropToSquare = 0x20,
        WideThumbnails = 0x40,
        IconBackground = 0x80,
        ScaleUp = 0x100
    }

    [DllImport("shell32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
    static extern void SHCreateItemFromParsingName(
        string pszPath,
        IntPtr pbc,
        [MarshalAs(UnmanagedType.LPStruct)] Guid riid,
        [MarshalAs(UnmanagedType.Interface)] out IShellItemImageFactory ppv
    );

    [DllImport("gdi32.dll")]
    static extern bool DeleteObject(IntPtr hObject);

    public static Bitmap GetThumbnail(string path, int width, int height, bool thumbnailOnly)
    {
        Guid iid = new Guid("bcc18b79-ba16-442f-80c4-8a59c30c463b");
        IShellItemImageFactory factory;
        SHCreateItemFromParsingName(path, IntPtr.Zero, iid, out factory);

        SIZE size = new SIZE { cx = width, cy = height };
        IntPtr hBitmap = IntPtr.Zero;

        SIIGBF flags = SIIGBF.BiggerSizeOk;
        if (thumbnailOnly)
            flags |= SIIGBF.ThumbnailOnly;

        factory.GetImage(size, flags, out hBitmap);

        if (hBitmap == IntPtr.Zero)
            return null;

        try
        {
            Bitmap bmp = Image.FromHbitmap(hBitmap);
            return bmp;
        }
        finally
        {
            DeleteObject(hBitmap);
        }
    }
}
"@

try {
    Add-Type -TypeDefinition $script:ThumbnailCode -ReferencedAssemblies System.Drawing | Out-Null
} catch {
}

[System.Windows.Forms.Application]::EnableVisualStyles()

function Normalize-DisplayText($value, $fallback = "") {
    if ($null -eq $value) { return $fallback }

    $text = [string]$value
    if ([string]::IsNullOrEmpty($text)) { return $fallback }

    $text = $text -replace "`r`n", "`n"
    $text = $text -replace "`r", "`n"
    $text = $text -replace "`n", [Environment]::NewLine

    return $text
}

function SafeText($value, $fallback = "") {
    if ($null -eq $value) { return $fallback }
    $text = [string]$value
    if ([string]::IsNullOrWhiteSpace($text)) { return $fallback }
    return $text
}

function Copy-Text($text) {
    $value = Normalize-DisplayText $text ""

    try {
        Set-Clipboard -Value $value
        return $true
    } catch {
        try {
            [System.Windows.Forms.Clipboard]::SetText($value)
            return $true
        } catch {
            return $false
        }
    }
}

function Set-CopiedState($button, $originalText) {
    if ($null -eq $button) { return }
    if (-not ($button -is [System.Windows.Forms.Button])) { return }
    if ($button.IsDisposed) { return }

    $button.Text = "Copied"

    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = 1100
    $timer.Tag = [pscustomobject]@{
        Button = $button
        OriginalText = [string]$originalText
    }

    $timer.Add_Tick({
        param($sender, $e)

        try {
            $sender.Stop()

            $state = $sender.Tag
            if ($null -ne $state -and $null -ne $state.Button) {
                $targetButton = $state.Button
                if (($targetButton -is [System.Windows.Forms.Button]) -and (-not $targetButton.IsDisposed)) {
                    $targetButton.Text = $state.OriginalText
                }
            }
        } catch {
        } finally {
            try { $sender.Dispose() } catch {}
        }
    })

    $timer.Start()
}

function Get-AutoHeight($text, $width) {
    $tmp = New-Object System.Windows.Forms.RichTextBox
    $tmp.Width = $width
    $tmp.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $tmp.Multiline = $true
    $tmp.WordWrap = $true
    $tmp.Text = Normalize-DisplayText $text ""

    $tmp.Height = 1
    $tmp.SelectAll()
    $tmp.SelectionFont = $tmp.Font

    $height = $tmp.GetPositionFromCharIndex($tmp.TextLength).Y + 30

    if ($height -lt 80) { $height = 80 }
    if ($height -gt 400) { $height = 400 }

    $tmp.Dispose()
    return $height
}

function Try-GetImagePreview($filePath) {
    try {
        if (-not [System.IO.File]::Exists($filePath)) {
            return $null
        }

        $fs = [System.IO.File]::Open($filePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
        try {
            $img = [System.Drawing.Image]::FromStream($fs)
            return [System.Drawing.Bitmap]::new($img)
        } finally {
            $fs.Dispose()
        }
    } catch {
        return $null
    }
}

function Try-GetShellThumbnail($filePath, [int]$width, [int]$height) {
    try {
        if (-not [System.IO.File]::Exists($filePath)) {
            return $null
        }

        try {
            $thumb = [ShellThumbnail]::GetThumbnail($filePath, $width, $height, $true)
            if ($thumb -ne $null) {
                return $thumb
            }
        } catch {
        }

        try {
            $thumb = [ShellThumbnail]::GetThumbnail($filePath, $width, $height, $false)
            if ($thumb -ne $null) {
                return $thumb
            }
        } catch {
        }
    } catch {
    }

    return $null
}

function Try-GetAssociatedIconBitmap($filePath, [int]$width, [int]$height) {
    try {
        if (-not [System.IO.File]::Exists($filePath)) {
            return $null
        }

        $icon = [System.Drawing.Icon]::ExtractAssociatedIcon($filePath)
        if ($icon -eq $null) {
            return $null
        }

        $bmp = New-Object System.Drawing.Bitmap $width, $height
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.Clear([System.Drawing.Color]::White)

        $iconSize = [Math]::Min($width, $height) - 24
        if ($iconSize -lt 24) { $iconSize = 24 }

        $x = [int](($width - $iconSize) / 2)
        $y = [int](($height - $iconSize) / 2)

        $g.DrawIcon($icon, $x, $y)
        $g.Dispose()
        $icon.Dispose()

        return $bmp
    } catch {
        return $null
    }
}

function Try-GetPreviewImage($filePath, [int]$width, [int]$height) {
    try {
        $ext = [System.IO.Path]::GetExtension($filePath).ToLowerInvariant()

        if ($ext -in @(".png", ".jpg", ".jpeg", ".bmp", ".gif")) {
            $img = Try-GetImagePreview $filePath
            if ($img -ne $null) {
                return $img
            }
        }

        $thumb = Try-GetShellThumbnail $filePath $width $height
        if ($thumb -ne $null) {
            return $thumb
        }

        $iconBmp = Try-GetAssociatedIconBitmap $filePath $width $height
        if ($iconBmp -ne $null) {
            return $iconBmp
        }
    } catch {
    }

    return $null
}

function New-Card($title, [int]$height = 120) {
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Width = 1060
    $panel.Height = $height
    $panel.BackColor = [System.Drawing.Color]::White
    $panel.BorderStyle = "FixedSingle"
    $panel.Margin = New-Object System.Windows.Forms.Padding(0, 0, 0, 12)

    $header = New-Object System.Windows.Forms.Panel
    $header.Location = New-Object System.Drawing.Point(0, 0)
    $header.Size = New-Object System.Drawing.Size(1058, 42)
    $header.BackColor = [System.Drawing.Color]::White
    $panel.Controls.Add($header)

    $label = New-Object System.Windows.Forms.Label
    $label.Text = $title
    $label.Location = New-Object System.Drawing.Point(14, 10)
    $label.Size = New-Object System.Drawing.Size(760, 22)
    $label.Font = New-Object System.Drawing.Font("Segoe UI Semibold", 11)
    $label.ForeColor = [System.Drawing.Color]::Black
    $label.BackColor = [System.Drawing.Color]::White
    $header.Controls.Add($label)

    $line = New-Object System.Windows.Forms.Panel
    $line.Location = New-Object System.Drawing.Point(12, 41)
    $line.Size = New-Object System.Drawing.Size(1032, 1)
    $line.BackColor = [System.Drawing.Color]::FromArgb(220, 220, 220)
    $panel.Controls.Add($line)

    return $panel
}

function New-ReadOnlyTextBox([int]$x, [int]$y, [int]$w, [int]$h, $text, [bool]$multiline = $false) {
    if ($multiline) {
        $tb = New-Object System.Windows.Forms.RichTextBox
        $tb.Location = New-Object System.Drawing.Point($x, $y)
        $tb.Size = New-Object System.Drawing.Size($w, $h)
        $tb.ReadOnly = $true
        $tb.BackColor = [System.Drawing.Color]::White
        $tb.BorderStyle = "FixedSingle"
        $tb.Font = New-Object System.Drawing.Font("Segoe UI", 9)
        $tb.ForeColor = [System.Drawing.Color]::Black
        $tb.ScrollBars = "Vertical"
        $tb.Multiline = $true
        $tb.WordWrap = $true
        $tb.DetectUrls = $false
        $tb.ShortcutsEnabled = $true
        $tb.Text = Normalize-DisplayText $text ""
        return $tb
    }

    $tb = New-Object System.Windows.Forms.TextBox
    $tb.Location = New-Object System.Drawing.Point($x, $y)
    $tb.Size = New-Object System.Drawing.Size($w, $h)
    $tb.Multiline = $false
    $tb.ReadOnly = $true
    $tb.BackColor = [System.Drawing.Color]::White
    $tb.ForeColor = [System.Drawing.Color]::Black
    $tb.Text = SafeText $text ""
    $tb.BorderStyle = "FixedSingle"
    return $tb
}

function Resolve-CopySourceText($copySource) {
    if ($null -eq $copySource) {
        return ""
    }

    if ($copySource -is [System.Windows.Forms.TextBoxBase]) {
        return Normalize-DisplayText $copySource.Text ""
    }

    if ($copySource -is [System.Windows.Forms.Control]) {
        return Normalize-DisplayText $copySource.Text ""
    }

    return Normalize-DisplayText $copySource ""
}

function Add-CopyButton($parent, [int]$x, [int]$y, [int]$w, [int]$h, $copySource, [string]$label = "Copy") {
    $btn = New-Object System.Windows.Forms.Button
    $btn.Location = New-Object System.Drawing.Point($x, $y)
    $btn.Size = New-Object System.Drawing.Size($w, $h)
    $btn.Text = $label
    $btn.FlatStyle = "System"
    $btn.Tag = [hashtable]@{
        CopySource = $copySource
        OriginalLabel = [string]$label
    }

    $btn.Add_Click({
        param($sender, $e)

        $state = $sender.Tag
        $valueToCopy = ""
        $originalLabel = "Copy"

        if ($null -ne $state) {
            if ($state.ContainsKey("CopySource")) {
                $valueToCopy = Resolve-CopySourceText $state["CopySource"]
            }
            if ($state.ContainsKey("OriginalLabel")) {
                $originalLabel = [string]$state["OriginalLabel"]
            }
        }

        if (Copy-Text $valueToCopy) {
            Set-CopiedState $sender $originalLabel
        } else {
            [System.Windows.Forms.MessageBox]::Show("Unable to copy to clipboard.", "AI Metadata Inspector")
        }
    })

    $parent.Controls.Add($btn)
    return $btn
}

function Add-FieldRow($parent, [int]$top, [string]$labelText, $value, [string]$copyLabel = "Copy") {
    $labelBox = New-Object System.Windows.Forms.Panel
    $labelBox.Location = New-Object System.Drawing.Point(14, $top)
    $labelBox.Size = New-Object System.Drawing.Size(155, 26)
    $labelBox.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)
    $labelBox.BorderStyle = "FixedSingle"
    $parent.Controls.Add($labelBox)

    $label = New-Object System.Windows.Forms.Label
    $label.Text = $labelText
    $label.Location = New-Object System.Drawing.Point(8, 4)
    $label.Size = New-Object System.Drawing.Size(138, 18)
    $label.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $label.ForeColor = [System.Drawing.Color]::Black
    $label.BackColor = [System.Drawing.Color]::Transparent
    $label.TextAlign = [System.Drawing.ContentAlignment]::MiddleLeft
    $label.AutoEllipsis = $true
    $labelBox.Controls.Add($label)

    $tb = New-ReadOnlyTextBox 182 $top 730 26 $value $false
    $parent.Controls.Add($tb)

    Add-CopyButton $parent 930 $top 100 26 $tb $copyLabel | Out-Null
}
