# AI Metadata Inspector

## v1.2.0

* Added MP4 frame extraction with cancel UI
* Multi-sampler improvements and better seed handling

Portable Windows tool to extract AI generation metadata and instantly reuse prompts from image and video files via right-click.

\---

## Quick Access (Right-click)

Access everything instantly from Windows Explorer:

!\[Right Click](screenshots/right-click.png)

* Copy positive prompt
* Copy negative prompt
* Open full AI metadata window
* Extract frames from MP4

No need to open ComfyUI or dig through workflows

\---

## AI Info Window

Clean and fast overview of prompts and generation settings:

!\[AI Info](screenshots/AI-Info.png)

\---

## Detailed Generation Data

Full breakdown including seed logic and sampler configuration:

!\[AI Info 2](screenshots/AI-Info2.png)

\---

## Advanced Workflow Support

Multi-pass workflows are fully supported and clearly displayed:

!\[AI Info 3](screenshots/AI-Info3.png)

\---

## Frame Extraction (NEW in V1.2.0)

* Extract all frames from MP4 as PNG (lossless)
* Uses bundled FFmpeg (no dependency)
* Configurable output:

  * next to video
  * fixed folder
* Smart cleanup (no folder spam)
* Cancel anytime via GUI

\---

## Features

* Extract metadata from **PNG and MP4**
* Works with:

  * ComfyUI workflows
  * WAN / img2vid pipelines
  * A1111-style metadata (partial)
* Instant prompt copy via right-click
* Clean UI (no node graph mess)

### Generation Data

* Seed (robust detection, including `0`)
* Noise seed
* Add noise / denoise
* Steps / CFG / sampler / scheduler
* Workflow resolution, FPS, length

### Multi-Sampler Support

* Detects multiple sampler passes automatically
* Works with advanced workflows

\---

## Why this tool?

* No need to launch ComfyUI
* Works directly from Explorer
* Much faster when browsing folders
* Clear summary instead of complex graphs

Think of it like **MediaInfo for AI-generated content**

\---

## Installation

Download the latest installer:

https://github.com/Gaurox/AI-Metadata-Inspector/releases

\---

## Supported Formats

### PNG

* ComfyUI prompt JSON
* A1111 metadata

### MP4

* ComfyUI workflow JSON
* Multi-sampler workflows

\---

## License

MIT License

\---

## Author

Gaurox

