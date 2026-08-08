# Release traceability — v1.3.3

This document records the component baseline for the local **v1.3.3** Security
& Hardening release preparation and the minimum release evidence required for
every future release. It supplements, but does not replace, the third-party
license notices. No tag or remote publication is created by this workflow.

## Local v1.3.3 build artifact

| Field | Value |
|---|---|
| Setup | `Output/AI_Metadata_Inspector_Setup.exe` |
| Setup SHA-256 | `5091c09677ed7f72114f8d2a8c032aaaf0e339f7d4d69087c7ebfa85b09fea58` |
| Setup file/product version | `1.3.3` |
| Machine-readable manifest | `Output/AI_Metadata_Inspector_release_manifest.json` |
| Checksum sidecar | `Output/AI_Metadata_Inspector_Setup.exe.sha256` |
| Source commit recorded | `589438705873e5e3e42e445ebf1a2f037e66b956` |
| Source tree status | Dirty: local release preparation has not yet been committed/tagged. |

The generated JSON manifest and `.sha256` sidecar were checked against this
exact setup binary. Regenerate all three files after any packaged-input change.

## Current bundled-component baseline

| Component | Version | Provenance | SHA-256 |
|---|---|---|---|
| FFmpeg | `8.1.2-essentials_build-www.gyan.dev` | `https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-8.1.2-essentials_build.zip` | executable: `1326dde4c84ff1f96fe6b8916c5bed29e163e9b5dccf995f6f3db069d143ec5e`; verified archive: `db580001caa24ac104c8cb856cd113a87b0a443f7bdf47d8c12b1d740584a2ec` |
| ExifTool | `13.54` | `https://exiftool.org/` | `exiftool.exe`: `3b7bc604426fa3e4ce430a5c4f4c1c1d8ca1221abd0b643aa41c74a4d61998a8` |
| Embedded Python | `3.12.10` | `https://www.python.org/` | `python.exe`: `4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a`; `pythonw.exe`: `d72294fb338bc2fc8896d25a7395a4db466425427e1559e77185d5135a830681` |

The FFmpeg source package checksum above is published by the build provider.
Its upstream 8.1.2 release contains the security fixes required by DEP-01.

## Required evidence for a release

1. Build only from a clean, exact commit, then create an immutable tag for that commit.
2. Run the relevant validation suite and build the installer.
3. Generate the machine-readable manifest with:

   ```powershell
   .\tools\generate_release_manifest.ps1 -Version <release-version>
   ```

4. Generate the installer checksum with `tools\generate_checksum.ps1`.
5. Publish the installer, its `.sha256` sidecar and the generated JSON manifest
   together; record the tag/commit and do not replace an already published asset.

Authenticode signing, SBOM generation and CI enforcement are intentionally not
claimed here; they remain follow-up work tracked under REL-03.
