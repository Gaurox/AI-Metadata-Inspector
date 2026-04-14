from __future__ import annotations

import json
from pathlib import Path

from exif_reader import debug


DEFAULT_CONFIG = {
    "frame_extraction": {
        "mode": "next_to_video",
        "fixed_folder": "",
        "fixed_folder_behavior": "subfolder_per_video",
    }
}


def get_app_dir() -> Path:
    return Path(__file__).resolve().parent


def get_config_path() -> Path:
    return get_app_dir() / "config.json"


def _normalize_mode(value) -> str:
    text = str(value or "").strip().lower()
    if text == "fixed_folder":
        return "fixed_folder"
    return "next_to_video"


def _normalize_folder(value) -> str:
    return str(value or "").strip()


def _normalize_fixed_folder_behavior(value) -> str:
    text = str(value or "").strip().lower()
    if text == "single_shared_folder":
        return "single_shared_folder"
    return "subfolder_per_video"


def load_raw_config() -> dict:
    config_path = get_config_path()

    if not config_path.exists():
        debug(f"CONFIG NOT FOUND, USING DEFAULTS: {config_path}")
        return dict(DEFAULT_CONFIG)

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8", errors="replace"))
        if not isinstance(raw, dict):
            debug("CONFIG INVALID ROOT TYPE, USING DEFAULTS")
            return dict(DEFAULT_CONFIG)
        return raw
    except Exception as e:
        debug(f"CONFIG READ ERROR: {e}")
        return dict(DEFAULT_CONFIG)


def get_frame_extraction_config() -> dict:
    raw = load_raw_config()

    section = raw.get("frame_extraction", {})
    if not isinstance(section, dict):
        section = {}

    mode = _normalize_mode(section.get("mode"))
    fixed_folder = _normalize_folder(section.get("fixed_folder"))
    fixed_folder_behavior = _normalize_fixed_folder_behavior(
        section.get("fixed_folder_behavior")
    )

    if mode == "fixed_folder" and not fixed_folder:
        debug("FIXED_FOLDER MODE WITHOUT FOLDER, FALLBACK TO next_to_video")
        mode = "next_to_video"

    config = {
        "mode": mode,
        "fixed_folder": fixed_folder,
        "fixed_folder_behavior": fixed_folder_behavior,
    }

    debug(f"FRAME EXTRACTION CONFIG: {config}")
    return config