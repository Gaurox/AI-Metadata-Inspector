# Third-Party Notices

AI Metadata Inspector bundles the following third-party components. Each is governed by its own license, reproduced or referenced below.

---

## FFmpeg

**Version:** 8.1-essentials_build  
**Source:** https://www.gyan.dev/ffmpeg/builds/ (Gyan Doshi's Windows builds)  
**Upstream:** https://ffmpeg.org/  
**License:** GNU General Public License v3.0 or later (GPLv3+)

This build was compiled with `--enable-gpl --enable-version3`, which makes the binary subject to the GNU General Public License version 3.

> FFmpeg is free software; you can redistribute it and/or modify it under the
> terms of the GNU General Public License as published by the Free Software
> Foundation; either version 3 of the License, or (at your option) any later
> version.
>
> FFmpeg is distributed in the hope that it will be useful, but WITHOUT ANY
> WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
> A PARTICULAR PURPOSE. See the GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License along with
> FFmpeg; if not, write to the Free Software Foundation, Inc., 51 Franklin
> Street, Fifth Floor, Boston, MA 02110-1301 USA.

The full text of the GPLv3 is available at: https://www.gnu.org/licenses/gpl-3.0.html

Source code for the bundled FFmpeg binary can be obtained from the build provider at https://www.gyan.dev/ffmpeg/builds/, or directly from the FFmpeg project at https://ffmpeg.org/download.html.

---

## ExifTool

**Version:** 13.54  
**Source:** https://exiftool.org/  
**Author:** Phil Harvey  
**License:** Perl Artistic License or GNU General Public License (dual-licensed)

ExifTool is available for use and distribution under the terms of either:
- the Perl Artistic License (https://dev.perl.org/licenses/artistic.html), or
- the GNU General Public License version 1 or later (https://www.gnu.org/licenses/old-licenses/gpl-1.0.html)

at your option.

The bundled ExifTool Perl library files are located in the `exiftool_files/` directory. See `exiftool_files/LICENSE` for the full license text.

---

## Python

**Version:** 3.12.10  
**Source:** https://www.python.org/  
**License:** Python Software Foundation License Version 2 (PSF-2.0)

> Copyright (c) 2001-present Python Software Foundation; All Rights Reserved.

The PSF License is a permissive license compatible with the MIT License under which AI Metadata Inspector itself is distributed. The full PSF License is available at https://docs.python.org/3/license.html.

The embedded Python runtime (`python_embeded/`) also includes:

- **OpenSSL 3.0.16** — Apache License 2.0 (see https://openssl.org/source/license.html)
- **Tcl/Tk** — Tcl/Tk License (permissive, see https://www.tcl.tk/software/tcltk/license.html) — *only if Tkinter is present*

---

## Strawberry Perl (bundled with ExifTool)

Portions of the Perl runtime bundled for ExifTool are from Strawberry Perl (https://strawberryperl.com/).  
See `exiftool_files/Licenses_Strawberry_Perl.zip` for applicable license texts.

---

*AI Metadata Inspector itself is distributed under the MIT License. See [LICENSE](LICENSE).*
