from __future__ import annotations

from pathlib import Path

from exif_reader import collect_media_info
from prompt_extractors import extract_prompt_data, looks_like_json
from workflow_parser import collect_comfy_info, find_json_data


def _safe_text(value, empty_text="(not found)"):
    if value is None:
        return empty_text
    if isinstance(value, str):
        value = value.strip()
        return value if value else empty_text
    return str(value)


def _describe_metadata_tag(tag: str, value: str) -> str:
    tag_name = str(tag).strip() or "Unknown"

    if looks_like_json(value):
        lowered = tag_name.lower()
        if lowered == "prompt":
            return f"{tag_name}: JSON metadata detected"
        if lowered == "workflow":
            return f"{tag_name}: Full workflow JSON detected"
        return f"{tag_name}: JSON metadata detected"

    text_len = len((value or "").strip())
    if text_len > 0:
        return f"{tag_name}: Text metadata detected"

    return f"{tag_name}: Metadata detected"


def _build_info_context(file_path, found, media=None):
    path_obj = Path(file_path)
    media = media if media is not None else collect_media_info(file_path)

    data, source_tag = find_json_data(found)
    comfy = collect_comfy_info(data) if data else None
    prompt_data = extract_prompt_data(found)

    positive = prompt_data["positive"]
    negative = prompt_data["negative"]
    a1111_params = prompt_data["a1111_params"]

    if comfy:
        if positive is None:
            positive = comfy.get("positive")
        if negative is None:
            negative = comfy.get("negative")

    workflow_size = ""
    if comfy and comfy.get("width") and comfy.get("height"):
        workflow_size = f'{comfy["width"]} x {comfy["height"]}'

    file_dimensions = ""
    img_w = media.get("ImageWidth") or media.get("SourceImageWidth")
    img_h = media.get("ImageHeight") or media.get("SourceImageHeight")
    if img_w and img_h:
        file_dimensions = f"{img_w} x {img_h}"

    models = []
    clips = []
    vaes = []
    loras = []
    upscale_models = []
    sigmas = []
    seed = ""
    seed_source = ""
    steps = ""
    cfg = ""
    sampler = ""
    scheduler = ""
    model_display = ""
    length_frames = ""
    batch_size = ""
    workflow_fps = ""
    confidence = "medium"
    prompt_source = source_tag or ""

    if comfy:
        models = comfy.get("models", []) or []
        clips = comfy.get("clips", []) or []
        vaes = comfy.get("vaes", []) or []
        loras = comfy.get("loras", []) or []
        upscale_models = comfy.get("upscale_models", []) or []
        sigmas = comfy.get("sigmas", []) or []
        seed = comfy.get("seed") or ""
        seed_source = comfy.get("seed_source") or ""
        steps = comfy.get("steps") or ""
        cfg = comfy.get("cfg") or ""
        sampler = comfy.get("sampler") or ""
        scheduler = comfy.get("scheduler") or ""
        model_display = " | ".join(models) if models else ""
        length_frames = comfy.get("length") or ""
        batch_size = comfy.get("batch_size") or ""
        workflow_fps = comfy.get("fps") or ""
        confidence = "high" if positive and seed else "medium"
        prompt_source = source_tag or "comfy"
    else:
        model_display = a1111_params.get("model") or ""
        seed = a1111_params.get("seed") or ""
        steps = a1111_params.get("steps") or ""
        cfg = a1111_params.get("cfg") or ""
        sampler = a1111_params.get("sampler") or ""
        seed_source = "A1111 parameters" if seed else ""
        confidence = "medium" if positive else "low"
        if positive and not prompt_source:
            prompt_source = "text tag fallback"

    metadata_sources_lines = []
    for tag, value in found:
        metadata_sources_lines.append(_describe_metadata_tag(tag, value))

    debug_info = {
        "json_detected": bool(data),
        "source_tag": source_tag or "",
        "has_comfy": comfy is not None,
        "positive_found": bool(positive),
        "negative_found": bool(negative),
        "seed_found": bool(seed),
        "model_found": bool(model_display),
        "confidence": confidence,
        "prompt_source": prompt_source,
        "seed_source": seed_source,
    }

    return {
        "path_obj": path_obj,
        "media": media,
        "source_tag": source_tag or "",
        "comfy": comfy,
        "positive": positive or "",
        "negative": negative or "",
        "a1111_params": a1111_params,
        "models": models,
        "clips": clips,
        "vaes": vaes,
        "loras": loras,
        "upscale_models": upscale_models,
        "sigmas": sigmas,
        "seed": seed,
        "seed_source": seed_source,
        "steps": steps,
        "cfg": cfg,
        "sampler": sampler,
        "scheduler": scheduler,
        "model_display": model_display,
        "workflow_size": workflow_size,
        "file_dimensions": file_dimensions,
        "length_frames": length_frames,
        "batch_size": batch_size,
        "workflow_fps": workflow_fps,
        "prompt_source": prompt_source,
        "confidence": confidence,
        "metadata_sources_lines": metadata_sources_lines,
        "debug_info": debug_info,
    }


def build_info_text(file_path, found, media=None):
    ctx = _build_info_context(file_path, found, media=media)
    path_obj = ctx["path_obj"]
    media = ctx["media"]
    comfy = ctx["comfy"]
    a1111_params = ctx["a1111_params"]

    lines = []

    def add_line(text=""):
        lines.append(text)

    def add_kv(label, value):
        lines.append(f"{label}: {value}")

    def add_big_title(title):
        if lines:
            lines.extend(["", "", ""])
        lines.append(f"=== {title} ===")
        lines.append("")

    add_big_title("AI INFO")
    add_kv("File", str(path_obj))
    add_kv("Name", path_obj.name)
    add_kv("Extension", path_obj.suffix.lower() or "(none)")
    add_kv("File type", _safe_text(media.get("FileType")))
    add_kv("MIME", _safe_text(media.get("MIMEType")))
    add_kv("File size", _safe_text(media.get("FileSize")))
    add_kv("Duration", _safe_text(media.get("Duration")))
    add_kv("Media FPS", _safe_text(media.get("VideoFrameRate")))
    add_kv("Bitrate", _safe_text(media.get("AvgBitrate")))

    add_big_title("POSITIVE PROMPT")
    add_line(_safe_text(ctx["positive"], "Positive prompt not found"))

    add_big_title("NEGATIVE PROMPT")
    add_line(_safe_text(ctx["negative"], "Negative prompt empty or not found"))

    add_big_title("GENERATION")
    add_kv("Seed", _safe_text(ctx["seed"]))
    add_kv("Seed source", _safe_text(ctx["seed_source"]))
    add_kv("Steps", _safe_text(ctx["steps"] if comfy else a1111_params.get("steps")))
    add_kv("CFG", _safe_text(ctx["cfg"] if comfy else a1111_params.get("cfg")))
    add_kv("Sampler", _safe_text(ctx["sampler"] if comfy else a1111_params.get("sampler")))
    add_kv("Scheduler", _safe_text(ctx["scheduler"]))
    add_kv("Prompt source", _safe_text(ctx["prompt_source"]))
    add_kv("Confidence", _safe_text(ctx["confidence"]))

    if comfy:
        add_big_title("MODELS")
        add_kv("UNET / main model", " | ".join(ctx["models"]) if ctx["models"] else "(not found)")
        add_kv("CLIP", " | ".join(ctx["clips"]) if ctx["clips"] else "(not found)")
        add_kv("VAE", " | ".join(ctx["vaes"]) if ctx["vaes"] else "(not found)")
        add_kv("Upscale models", " | ".join(ctx["upscale_models"]) if ctx["upscale_models"] else "(none found)")
        add_kv("Sigmas", " | ".join(ctx["sigmas"]) if ctx["sigmas"] else "(none found)")

        if ctx["loras"]:
            add_line("LoRAs:")
            for lora in ctx["loras"]:
                add_line(f"  - {lora}")
        else:
            add_kv("LoRAs", "(none found)")

        add_big_title("OUTPUT / DIMENSIONS")
        add_kv("Workflow size", _safe_text(ctx["workflow_size"]))
        add_kv("File dimensions", _safe_text(ctx["file_dimensions"]))
        add_kv("Length / frames", _safe_text(ctx["length_frames"]))
        add_kv("Batch size", _safe_text(ctx["batch_size"]))
        add_kv("Workflow FPS", _safe_text(ctx["workflow_fps"]))

        add_big_title("SOURCE")
        add_kv("Metadata source", _safe_text(ctx["source_tag"]))
    else:
        add_big_title("MODEL / A1111")
        add_kv("Model", _safe_text(a1111_params.get("model")))
        add_kv("Declared size", _safe_text(a1111_params.get("size")))

    add_big_title("DEBUG")
    for key, value in ctx["debug_info"].items():
        add_kv(key, value)

    add_big_title("METADATA SOURCES")
    if ctx["metadata_sources_lines"]:
        for entry in ctx["metadata_sources_lines"]:
            add_line(f"- {entry}")
    else:
        add_line("- No metadata source detected")

    add_line("")
    return "\n".join(lines)


def build_info_payload(file_path, found):
    media = collect_media_info(file_path)
    ctx = _build_info_context(file_path, found, media=media)
    path_obj = ctx["path_obj"]

    payload = {
        "file_path": str(path_obj),
        "file_name": path_obj.name,
        "extension": path_obj.suffix.lower() or "",
        "file_type": media.get("FileType", ""),
        "mime": media.get("MIMEType", ""),
        "file_size": media.get("FileSize", ""),
        "duration": media.get("Duration", ""),
        "media_fps": media.get("VideoFrameRate", ""),
        "bitrate": media.get("AvgBitrate", ""),
        "positive": ctx["positive"],
        "negative": ctx["negative"],
        "seed": ctx["seed"],
        "seed_source": ctx["seed_source"],
        "steps": ctx["steps"],
        "cfg": ctx["cfg"],
        "sampler": ctx["sampler"],
        "scheduler": ctx["scheduler"],
        "model": ctx["model_display"],
        "clips": " | ".join(ctx["clips"]) if ctx["clips"] else "",
        "vae": " | ".join(ctx["vaes"]) if ctx["vaes"] else "",
        "workflow_size": ctx["workflow_size"],
        "file_dimensions": ctx["file_dimensions"],
        "length_frames": ctx["length_frames"],
        "batch_size": ctx["batch_size"],
        "workflow_fps": ctx["workflow_fps"],
        "loras": "\n".join(ctx["loras"]) if ctx["loras"] else "",
        "upscale_models": " | ".join(ctx["upscale_models"]) if ctx["upscale_models"] else "",
        "sigmas": " | ".join(ctx["sigmas"]) if ctx["sigmas"] else "",
        "source_tag": ctx["source_tag"],
        "prompt_source": ctx["prompt_source"],
        "confidence": ctx["confidence"],
        "found_tags": "\n".join(ctx["metadata_sources_lines"]) if ctx["metadata_sources_lines"] else "No metadata source detected",
        "debug_info": ctx["debug_info"],
        "copy_all": build_info_text(file_path, found, media=media),
    }
    return payload