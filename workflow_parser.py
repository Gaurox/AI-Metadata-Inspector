from __future__ import annotations

import json

from prompt_extractors import looks_like_json
from workflow_extractors import collect_node_based_info, collect_prompt_info
from workflow_seed import collect_seed_info


def find_json_data(found):
    for tag, value in found:
        if tag.lower() == "prompt" and looks_like_json(value):
            try:
                return json.loads(value), tag
            except Exception:
                pass

    for tag, value in found:
        if tag.lower() == "workflow" and looks_like_json(value):
            try:
                return json.loads(value), tag
            except Exception:
                pass

    for tag, value in found:
        if looks_like_json(value):
            try:
                return json.loads(value), tag
            except Exception:
                pass

    return None, None


def collect_comfy_info(data):
    prompt_info = collect_prompt_info(data)

    info = {
        "positive": prompt_info.get("positive"),
        "negative": prompt_info.get("negative"),
        "models": [],
        "clips": [],
        "vaes": [],
        "loras": [],
        "upscale_models": [],
        "sigmas": [],
        "seed": None,
        "seed_source": None,
        "steps": None,
        "cfg": None,
        "sampler": None,
        "scheduler": None,
        "width": None,
        "height": None,
        "length": None,
        "batch_size": None,
        "fps": None,
        "source_tag": "comfy",
    }

    collect_node_based_info(data, info)

    seed_info = collect_seed_info(data)
    if seed_info.get("seed") is not None:
        info["seed"] = seed_info["seed"]
        info["seed_source"] = seed_info.get("seed_source")

    return info
