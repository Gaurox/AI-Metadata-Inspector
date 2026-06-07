# Security Policy

## Supported Versions

Only the latest release receives security fixes.

| Version | Supported |
| ------- | --------- |
| 1.3.x   | Yes       |
| < 1.3   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in AI Metadata Inspector, please **do not open a public GitHub issue**.

Instead, report it privately via one of the following channels:

- **GitHub Security Advisories**: open a [private advisory](https://github.com/Gaurox/AI-Metadata-Inspector/security/advisories/new) on this repository *(preferred)*.
- **Email**: send details to the repository owner through the contact shown on the GitHub profile.

### What to include

- A clear description of the vulnerability.
- Steps to reproduce it (proof of concept if possible).
- The version of AI Metadata Inspector affected.
- Any relevant environment details (Windows version, etc.).

### What to expect

- An acknowledgement within **72 hours**.
- A status update within **7 days** (accepted, rejected, or in progress).
- A fix and coordinated disclosure within **30 days** for confirmed issues when feasible.

## Scope

This tool runs locally on the user's machine and does **not** communicate over the network. The primary attack surfaces are:

- Maliciously crafted image or video metadata parsed by ExifTool.
- Metadata parsed by the Python extractors (JSON, regex).
- PowerShell scripts executed during frame extraction or the info window.
- The Windows context menu entries (VBScript launcher).

## Third-Party Components

Known security advisories for bundled components are tracked manually:

- **ExifTool** — check [https://exiftool.org/history.html](https://exiftool.org/history.html)
- **FFmpeg** — check [https://ffmpeg.org/security.html](https://ffmpeg.org/security.html)
- **Python** — check [https://www.python.org/news/security/](https://www.python.org/news/security/)

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for bundled component versions.
