from __future__ import annotations

import json

from prompt_extractors import looks_like_json
from workflow_extractors import collect_node_based_info, collect_prompt_info
from workflow_seed import collect_sampler_details, collect_seed_info, pick_primary_sampler_detail


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
        "noise_seed": None,
        "denoise": None,
        "add_noise": None,
        "steps": None,
        "cfg": None,
        "sampler": None,
        "scheduler": None,
        "width": None,
        "height": None,
        "length": None,
        "batch_size": None,
        "fps": None,
        "samplers_details": [],
        "source_tag": "comfy",
    }

    collect_node_based_info(data, info)

    seed_info = collect_seed_info(data)
    if seed_info.get("seed") is not None:
        info["seed"] = seed_info["seed"]
        info["seed_source"] = seed_info.get("seed_source")

    samplers_details = collect_sampler_details(data)
    info["samplers_details"] = samplers_details

    primary_sampler = pick_primary_sampler_detail(samplers_details)
    if primary_sampler:
        if primary_sampler.get("noise_seed") is not None:
            info["noise_seed"] = primary_sampler.get("noise_seed")
        if primary_sampler.get("denoise"):
            info["denoise"] = primary_sampler.get("denoise")
        if primary_sampler.get("add_noise"):
            info["add_noise"] = primary_sampler.get("add_noise")

        if info["steps"] is None and primary_sampler.get("steps"):
            info["steps"] = primary_sampler.get("steps")
        if info["cfg"] is None and primary_sampler.get("cfg"):
            info["cfg"] = primary_sampler.get("cfg")
        if info["sampler"] is None and primary_sampler.get("sampler"):
            info["sampler"] = primary_sampler.get("sampler")
        if info["scheduler"] is None and primary_sampler.get("scheduler"):
            info["scheduler"] = primary_sampler.get("scheduler")

    return info
