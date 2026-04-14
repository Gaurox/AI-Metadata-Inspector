# AI Metadata Inspector

Portable Windows tool to extract AI generation metadata and reuse prompts from image and video files directly from the right-click menu.

\---

## Version

Current version: 1.2.0

\---

## Overview

AI Metadata Inspector allows you to quickly access prompts and generation data embedded in files without opening ComfyUI or any other tool.

It is designed to be fast, silent, and easy to use directly from Windows Explorer.

\---

## Features

Right-click actions:

* AI - Copy positive prompt
* AI - Copy negative prompt
* AI - Metadata Info
* AI - Extract Frames (MP4 only)

Supported formats:

* PNG
* MP4

Supported metadata:

* ComfyUI workflows (JSON)
* A1111-style metadata (partial)
* Various embedded metadata formats

\---

## Extracted data

The tool can extract:

* Positive and negative prompts
* Seed (including correct handling of 0)
* Noise seed
* Steps
* CFG
* Sampler and scheduler
* Denoise and add\_noise
* Resolution and dimensions
* FPS and length (video workflows)

\---

## Multi-pass workflows

Advanced workflows are supported:

* Multiple sampler passes detected
* Each pass is displayed independently
* Compatible with WAN and img2vid pipelines

\---

## Frame extraction

For MP4 files:

* Extracts all frames as PNG (lossless)
* Uses FFmpeg (included in the installer)
* Output options:

  * folder next to the video
  * or predefined folder

Frames are named consistently to avoid uncontrolled folder growth.
Partial extraction is automatically cleaned if cancelled.

\---

## Installation

Download the latest release:

https://github.com/Gaurox/AI-Metadata-Inspector/releases

Run the installer.

No additional dependencies are required.

\---

## Run from source

If you do not want to use the executable, you can run the tool directly.

### Requirements

* Windows 10 or 11
* Python 3.x

### Usage

python main.py "your\_file.png" info

Other modes:

python main.py "your\_file.png" positive
python main.py "your\_file.png" negative
python main.py "your\_file.mp4" extract\_frames

\---

## Build the installer

The installer is built using Inno Setup.

### Requirements

* Inno Setup

### Build command

iscc AI\_Metadata\_Inspector.iss

The installer will be generated in the Output folder.

\---

## What is included

The installer contains:

* Python (embedded, portable)
* ExifTool
* All Python scripts
* PowerShell GUI
* VBS launcher (silent execution)
* Context menu integration
* FFmpeg (for frame extraction)

No external downloads are required.

\---

## Project structure

Main files:

* main.py: CLI entry point
* exif\_reader.py: metadata extraction via ExifTool
* prompt\_extractors.py: prompt extraction logic
* workflow\_parser.py: workflow parsing
* workflow\_seed.py: seed and sampler logic
* info\_builder.py: structured output
* info\_window.py: GUI launcher

\---

## Security and transparency

This project is open source.

If you do not trust the executable:

* you can run the tool from source
* you can build the installer yourself
* you can inspect all scripts before running anything

There is no network communication and no external dependency.

\---

## Limitations

* Optimized for ComfyUI workflows
* Partial compatibility with other tools
* Metadata depends on how the file was generated

\---

## License

MIT License

\---

## Author

Gaurox

