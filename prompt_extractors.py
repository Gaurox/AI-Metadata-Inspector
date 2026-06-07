from __future__ import annotations

import json
import re


FAST_JSON_TAGS = ("prompt", "workflow", "Prompt", "Workflow")
FAST_A1111_TAGS = ("Parameters", "Comment", "Description", "ImageDescription", "UserComment", "XPComment")
FAST_DIRECT_TEXT_TAGS = (
    "Prompt",
    "prompt",
    "XMP:Prompt",
    "QuickTime:Comment",
    "QuickTime:Description",
    "Comment",
    "Description",
    "ImageDescription",
    "UserComment",
    "XPComment",
    "Caption",
    "Lyrics",
    "ID3:Comment",
    "ID3:Lyrics",
    "QuickTime:Title",
    "ID3:Title",
    "Title",
    "Subject",
    "XMP:Description",
)
MAX_JSON_TEXT_CHARS = 2_000_000


def looks_like_json(text: str) -> bool:
    t = text.strip()
    return (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]"))


def safe_json_loads(text: str):
    if not isinstance(text, str):
        raise ValueError("JSON input must be text")
    if len(text) > MAX_JSON_TEXT_CHARS:
        raise ValueError("JSON input too large")
    return json.loads(text)


def extract_a1111_positive(text: str):
    if not text:
        return None
    clean = text.replace("\r", "").strip()
    if "Negative prompt:" in clean or "\nSteps:" in clean or clean.startswith("Steps:"):
        m = re.match(r"(?s)^(.*?)(?:\nNegative prompt:|\nSteps:|$)", clean)
        if m:
            val = m.group(1).strip()
            return val or None
    return None


def extract_a1111_negative(text: str):
    if not text:
        return None
    clean = text.replace("\r", "").strip()
    m = re.search(r"(?s)\nNegative prompt:\s*(.*?)(?:\nSteps:|$)", clean)
    if m:
        val = m.group(1).strip()
        return val or None
    return None


def extract_a1111_params(text: str):
    if not text:
        return {}

    clean = text.replace("\r", "").strip()
    out = {}

    m = re.search(r"(?:^|\n)Steps:\s*([^,\n]+)", clean, re.IGNORECASE)
    if m:
        out["steps"] = m.group(1).strip()

    m = re.search(r"(?:^|,\s*)Sampler:\s*([^,\n]+)", clean, re.IGNORECASE)
    if m:
        out["sampler"] = m.group(1).strip()

    m = re.search(r"(?:^|,\s*)CFG scale:\s*([^,\n]+)", clean, re.IGNORECASE)
    if m:
        out["cfg"] = m.group(1).strip()

    m = re.search(r"(?:^|,\s*)Seed:\s*([^,\n]+)", clean, re.IGNORECASE)
    if m:
        out["seed"] = m.group(1).strip()

    m = re.search(r"(?:^|,\s*)Denoising strength:\s*([^,\n]+)", clean, re.IGNORECASE)
    if m:
        out["denoise"] = m.group(1).strip()

    m = re.search(r"(?:^|,\s*)Size:\s*([^,\n]+)", clean, re.IGNORECASE)
    if m:
        out["size"] = m.group(1).strip()

    m = re.search(r"(?:^|,\s*)Model:\s*([^,\n]+)", clean, re.IGNORECASE)
    if m:
        out["model"] = m.group(1).strip()

    return out


def extract_text_from_prompt_node(node):
    if not isinstance(node, dict):
        return None

    inputs = node.get("inputs", {}) or {}

    for key in ("value", "text", "prompt"):
        val = inputs.get(key)
        if isinstance(val, str):
            val = val.strip()
            if val:
                return val

    widgets = node.get("widgets_values", []) or []
    if isinstance(widgets, list):
        for item in widgets:
            if isinstance(item, str):
                value = item.strip()
                if value:
                    return value

    return None


def resolve_prompt_dict_text(data, text_ref):
    if isinstance(text_ref, str):
        text_ref = text_ref.strip()
        return text_ref or None

    if isinstance(text_ref, list) and text_ref:
        ref_id = str(text_ref[0])
        ref_node = data.get(ref_id)
        resolved = extract_text_from_prompt_node(ref_node)
        if resolved is not None:
            return resolved

    return None


def resolve_workflow_text(data, node):
    if not isinstance(node, dict):
        return None

    direct = extract_text_from_prompt_node(node)
    if direct is not None:
        return direct

    inputs = node.get("inputs", []) or []
    links = data.get("links", []) or []
    nodes = data.get("nodes", []) or []
    node_by_id = {
        node_item.get("id"): node_item
        for node_item in nodes
        if isinstance(node_item, dict) and node_item.get("id") is not None
    }

    candidate_links = []
    for input_item in inputs:
        if not isinstance(input_item, dict):
            continue

        input_name = str(input_item.get("name", "")).strip().lower()
        if input_name in ("text", "prompt", "value"):
            candidate_links.append(input_item.get("link"))

    for wanted_link in candidate_links:
        if wanted_link is None:
            continue

        for link in links:
            if isinstance(link, list) and len(link) >= 6 and link[0] == wanted_link:
                src_node_id = link[1]
                src_node = node_by_id.get(src_node_id)
                resolved = extract_text_from_prompt_node(src_node)
                if resolved is not None:
                    return resolved

            if isinstance(link, dict) and link.get("id") == wanted_link:
                src_node_id = link.get("origin_id")
                src_node = node_by_id.get(src_node_id)
                resolved = extract_text_from_prompt_node(src_node)
                if resolved is not None:
                    return resolved

    return None


def _is_prompt_encoder(class_or_type: str) -> bool:
    s = str(class_or_type or "").strip().lower()
    if not s:
        return False

    return any(token in s for token in (
        "cliptextencode",
        "textencodeqwen",
        "textencode",
    ))


def _node_title_and_type(node, prompt_dict_mode=False):
    if prompt_dict_mode:
        class_type = str(node.get("class_type", "") or "")
        meta = node.get("_meta", {}) or {}
        title = str(meta.get("title", "") or node.get("title", "") or "")
        return class_type, title

    node_type = str(node.get("type", "") or "")
    title = str(node.get("title", "") or "")
    return node_type, title


def _extract_node_prompt(data, node, prompt_dict_mode=False):
    if not isinstance(node, dict):
        return None

    inputs = node.get("inputs", {}) or {}
    if prompt_dict_mode:
        for key in ("text", "prompt", "value"):
            resolved = resolve_prompt_dict_text(data, inputs.get(key))
            if resolved is not None:
                return resolved
        return extract_text_from_prompt_node(node)

    return resolve_workflow_text(data, node)


def extract_from_prompt_dict(data, mode="positive"):
    if not isinstance(data, dict):
        return None

    best = None

    for _, node in data.items():
        if not isinstance(node, dict):
            continue

        class_type, title = _node_title_and_type(node, prompt_dict_mode=True)
        title_lower = title.lower()
        class_lower = class_type.lower()

        if not _is_prompt_encoder(class_lower):
            continue

        text_value = _extract_node_prompt(data, node, prompt_dict_mode=True)

        is_negative = "negative" in title_lower
        is_positive = ("positive" in title_lower) or not is_negative

        if mode == "positive":
            if "positive" in title_lower and text_value:
                return text_value
            if best is None and is_positive and text_value:
                best = text_value

        elif mode == "negative":
            if "negative" in title_lower:
                return text_value or ""
            if best is None and is_negative:
                best = text_value or ""

    return best


def extract_from_workflow_nodes(data, mode="positive"):
    if not isinstance(data, dict):
        return None

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        return None

    best = None

    for node in nodes:
        if not isinstance(node, dict):
            continue

        node_type, title = _node_title_and_type(node, prompt_dict_mode=False)
        title_lower = title.lower()
        type_lower = node_type.lower()

        if not _is_prompt_encoder(type_lower):
            continue

        text_value = _extract_node_prompt(data, node, prompt_dict_mode=False)

        is_negative = "negative" in title_lower
        is_positive = ("positive" in title_lower) or not is_negative

        if mode == "positive":
            if "positive" in title_lower and text_value:
                return text_value
            if best is None and is_positive and text_value:
                best = text_value

        elif mode == "negative":
            if "negative" in title_lower:
                return text_value or ""
            if best is None and is_negative:
                best = text_value or ""

    return best


def extract_comfy_prompt(text: str, mode="positive"):
    if not text or not looks_like_json(text):
        return None

    data = safe_json_loads(text)

    val = extract_from_prompt_dict(data, mode=mode)
    if val is not None:
        return val

    val = extract_from_workflow_nodes(data, mode=mode)
    if val is not None:
        return val

    return None


def is_probable_prompt(text: str) -> bool:
    if not text:
        return False
    t = text.strip()
    if not t or looks_like_json(t) or len(t) < 8:
        return False

    lower = t.lower()
    junk = ["lavf", "isom", "mp42", "major_brand", "minor_version", "compatible_brands"]
    return not any(j in lower for j in junk)


def _iter_values_for_tags(found, preferred_tags):
    for preferred_tag in preferred_tags:
        for tag, value in found:
            if tag == preferred_tag:
                yield value


def _extract_json_prompt_from_found(found, mode="positive", preferred_tags=FAST_JSON_TAGS):
    for value in _iter_values_for_tags(found, preferred_tags):
        if not looks_like_json(value):
            continue
        try:
            extracted = extract_comfy_prompt(value, mode=mode)
        except Exception:
            extracted = None
        if extracted is not None:
            return extracted.strip() if isinstance(extracted, str) else extracted

    for _, value in found:
        if not looks_like_json(value):
            continue
        try:
            extracted = extract_comfy_prompt(value, mode=mode)
        except Exception:
            extracted = None
        if extracted is not None:
            return extracted.strip() if isinstance(extracted, str) else extracted

    return None


def _extract_a1111_from_found(found, mode="positive"):
    extractor = extract_a1111_positive if mode == "positive" else extract_a1111_negative

    for value in _iter_values_for_tags(found, FAST_A1111_TAGS):
        extracted = extractor(value)
        if extracted is not None:
            return extracted.strip() if isinstance(extracted, str) else extracted

    for _, value in found:
        extracted = extractor(value)
        if extracted is not None:
            return extracted.strip() if isinstance(extracted, str) else extracted

    return None


def _extract_direct_prompt_from_found(found):
    for value in _iter_values_for_tags(found, FAST_DIRECT_TEXT_TAGS):
        if is_probable_prompt(value):
            return value.strip()

    for _, value in found:
        if is_probable_prompt(value):
            return value.strip()

    return None


def extract_prompt_data_fast(found):
    positive = _extract_a1111_from_found(found, mode="positive")
    negative = _extract_a1111_from_found(found, mode="negative")
    a1111_params = {}

    if not a1111_params:
        for value in _iter_values_for_tags(found, FAST_A1111_TAGS):
            a1111_params = extract_a1111_params(value)
            if a1111_params:
                break
        if not a1111_params:
            for _, value in found:
                a1111_params = extract_a1111_params(value)
                if a1111_params:
                    break

    if positive is None:
        positive = _extract_direct_prompt_from_found(found)

    if positive is None:
        positive = _extract_json_prompt_from_found(found, mode="positive")

    if negative is None:
        negative = _extract_json_prompt_from_found(found, mode="negative")

    return {
        "positive": positive,
        "negative": negative,
        "a1111_params": a1111_params,
    }


def extract_prompt_data(found):
    positive = None
    negative = None
    a1111_params = {}

    for _, value in found:
        if positive is None:
            try:
                extracted = extract_comfy_prompt(value, mode="positive")
            except Exception:
                extracted = None
            if extracted is not None and extracted.strip():
                positive = extracted.strip()

        if negative is None:
            try:
                extracted = extract_comfy_prompt(value, mode="negative")
            except Exception:
                extracted = None
            if extracted is not None:
                negative = extracted.strip()

    for _, value in found:
        if positive is None:
            extracted = extract_a1111_positive(value)
            if extracted is not None and extracted.strip():
                positive = extracted.strip()

        if negative is None:
            extracted = extract_a1111_negative(value)
            if extracted is not None:
                negative = extracted.strip()

        if not a1111_params:
            a1111_params = extract_a1111_params(value)

    if positive is None:
        preferred_tags = [
            "Prompt", "prompt", "XMP:Prompt", "Parameters",
            "Comment", "Description", "ImageDescription", "UserComment",
            "XPComment", "Caption", "Lyrics",
            "XMP:Description", "QuickTime:Comment", "QuickTime:Description",
            "QuickTime:Title", "ID3:Comment", "ID3:Lyrics", "ID3:Title",
        ]

        for preferred_tag in preferred_tags:
            for tag, value in found:
                if tag == preferred_tag and is_probable_prompt(value):
                    positive = value.strip()
                    break
            if positive is not None:
                break

    return {
        "positive": positive,
        "negative": negative,
        "a1111_params": a1111_params,
    }
