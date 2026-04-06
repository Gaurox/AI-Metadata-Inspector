AI Metadata Inspector
Version: 1.0.0

Description
AI Metadata Inspector is a portable Windows utility for extracting AI generation data from image and video files.
It integrates into the Windows context menu and runs silently without opening console windows.

Features
- Extract positive and negative prompts
- Retrieve generation parameters (seed, steps, CFG, sampler, scheduler, models, LoRAs, VAE, and related metadata)
- Support both prompt-based and workflow-based metadata
- Copy extracted data directly to the clipboard
- Display complete metadata details in a lightweight inspection window

Supported Formats
- PNG — embedded prompt metadata
- MP4 — embedded workflow metadata

Usage
After installation, right-click a supported file and use one of the following actions:
- Copy positive prompt
- Copy negative prompt
- Metadata Info

Installation
Run the installer.
It will:
- Install all required files (embedded Python + ExifTool)
- Add Windows context menu entries
- Configure icons and uninstall support

No additional setup is required.

Architecture
- Python (embedded, no external dependencies)
- ExifTool (metadata extraction)
- PowerShell (WinForms GUI)
- VBS launcher (silent execution)
- Inno Setup (installer)

Compatibility
- Windows 10 / 11
- Fully portable
- No external dependencies

Limitations
- Optimized for ComfyUI-style metadata
- Compatibility depends on how metadata is embedded
- Some non-standard workflows or third-party formats may not be fully parsed

Third-Party Components
This project includes ExifTool, licensed under the Artistic License 2.0.
https://exiftool.org/

License
MIT License

Copyright (c) 2026 Gaurox
