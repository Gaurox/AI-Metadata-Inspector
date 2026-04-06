from __future__ import annotations

from workflow_resolver import _resolve_value
from workflow_utils import _input_dict_get, node_inputs, node_title, node_type, node_widgets


SAMPLER_EXCLUDE_TOKENS = (
    "ksamplerselect",
    "manualsigmas",
    "cfgguider",
    "flux2scheduler",
    "ltxvscheduler",
)


def _normalize_seed_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return None if value < 0 else str(value)
    if isinstance(value, float):
        if value < 0:
            return None
        if value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        if s.isdigit():
            return s
    return None


def _normalize_text_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, str):
        s = value.strip()
        return s if s else None
    return str(value)


def _iter_nodes_with_ids(data):
    if not isinstance(data, dict):
        return []

    if "nodes" in data and isinstance(data["nodes"], list):
        return [n for n in data["nodes"] if isinstance(n, dict)]

    out = []
    for node_id, node in data.items():
        if isinstance(node, dict) and ("class_type" in node or "inputs" in node):
            enriched = dict(node)
            if enriched.get("id") is None:
                enriched["_node_id"] = str(node_id)
            out.append(enriched)
    return out


def _is_sampler_execution_node(ntype: str) -> bool:
    s = str(ntype or "").strip().lower()
    if not s:
        return False
    if any(token in s for token in SAMPLER_EXCLUDE_TOKENS):
        return False
    return ("ksampler" in s) or ("samplercustomadvanced" in s) or ("samplercustom" in s)


def _safe_label(ntype: str, title: str, index: int) -> str:
    preferred = (title or "").strip() or (ntype or "").strip() or "Sampler"
    return f"{preferred} #{index}"


def _pick_first(*values, normalizer=_normalize_text_value):
    for value in values:
        normalized = normalizer(value)
        if normalized is not None:
            return normalized
    return None


def _get_node_id_value(node):
    node_id = node.get("id")
    if node_id is None:
        node_id = node.get("_node_id")
    if node_id is None:
        return ""
    return str(node_id)


def _extract_sampler_detail(data, node, index: int):
    ntype = node_type(node)
    title = node_title(node)
    ntype_lower = ntype.lower()
    inputs = node_inputs(node)
    widgets = node_widgets(node)

    seed = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "seed")),
        widgets[0] if ntype_lower == "ksampler" and len(widgets) > 0 else None,
        normalizer=_normalize_seed_value,
    )

    noise_seed = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "noise_seed")),
        widgets[1] if "ksampleradvanced" in ntype_lower and len(widgets) > 1 else None,
        widgets[0] if ("samplercustomadvanced" in ntype_lower or "samplercustom" in ntype_lower) and len(widgets) > 0 else None,
        normalizer=_normalize_seed_value,
    )

    add_noise = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "add_noise")),
        widgets[0] if "ksampleradvanced" in ntype_lower and len(widgets) > 0 else None,
    )

    denoise = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "denoise")),
        _resolve_value(data, _input_dict_get(inputs, "denoise_strength")),
        _resolve_value(data, _input_dict_get(inputs, "strength")),
        widgets[6] if ntype_lower == "ksampler" and len(widgets) > 6 else None,
    )

    steps = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "steps")),
        widgets[3] if "ksampleradvanced" in ntype_lower and len(widgets) > 3 else None,
        widgets[2] if ntype_lower == "ksampler" and len(widgets) > 2 else None,
    )

    cfg = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "cfg")),
        widgets[4] if "ksampleradvanced" in ntype_lower and len(widgets) > 4 else None,
        widgets[3] if ntype_lower == "ksampler" and len(widgets) > 3 else None,
    )

    sampler_name = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "sampler_name")),
        widgets[5] if "ksampleradvanced" in ntype_lower and len(widgets) > 5 else None,
        widgets[4] if ntype_lower == "ksampler" and len(widgets) > 4 else None,
    )

    scheduler = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "scheduler")),
        widgets[6] if "ksampleradvanced" in ntype_lower and len(widgets) > 6 else None,
        widgets[5] if ntype_lower == "ksampler" and len(widgets) > 5 else None,
    )

    start_at_step = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "start_at_step")),
        widgets[7] if "ksampleradvanced" in ntype_lower and len(widgets) > 7 else None,
    )

    end_at_step = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "end_at_step")),
        widgets[8] if "ksampleradvanced" in ntype_lower and len(widgets) > 8 else None,
    )

    return_with_leftover_noise = _pick_first(
        _resolve_value(data, _input_dict_get(inputs, "return_with_leftover_noise")),
        widgets[9] if "ksampleradvanced" in ntype_lower and len(widgets) > 9 else None,
    )

    if noise_seed is None and seed is not None and str(add_noise or "").strip().lower() == "enable":
        noise_seed = seed

    if seed is None and noise_seed is not None:
        seed = noise_seed

    return {
        "label": _safe_label(ntype, title, index),
        "node_id": _get_node_id_value(node),
        "node_type": ntype or "",
        "node_title": title or "",
        "seed": seed or "",
        "noise_seed": noise_seed or "",
        "add_noise": add_noise or "",
        "denoise": denoise or "",
        "steps": steps or "",
        "cfg": cfg or "",
        "sampler": sampler_name or "",
        "scheduler": scheduler or "",
        "start_at_step": start_at_step or "",
        "end_at_step": end_at_step or "",
        "return_with_leftover_noise": return_with_leftover_noise or "",
    }


def collect_sampler_details(data):
    nodes = _iter_nodes_with_ids(data)
    out = []
    idx = 1

    for node in nodes:
        ntype = node_type(node).lower()
        if not _is_sampler_execution_node(ntype):
            continue

        detail = _extract_sampler_detail(data, node, idx)

        interesting = any(
            detail.get(key) != ""
            for key in (
                "seed",
                "noise_seed",
                "add_noise",
                "denoise",
                "steps",
                "cfg",
                "sampler",
                "scheduler",
                "start_at_step",
                "end_at_step",
            )
        )
        if interesting:
            out.append(detail)
            idx += 1

    return out


def pick_primary_sampler_detail(details):
    if not details:
        return None

    def has_non_zero(value):
        s = str(value or "").strip()
        return bool(s) and s != "0"

    for detail in details:
        if str(detail.get("add_noise") or "").strip().lower() == "enable" and has_non_zero(detail.get("noise_seed")):
            return detail

    for detail in details:
        if has_non_zero(detail.get("noise_seed")):
            return detail

    for detail in details:
        if has_non_zero(detail.get("seed")):
            return detail

    return details[0]


def collect_seed_info(data):
    nodes = _iter_nodes_with_ids(data)

    info = {
        "seed": None,
        "seed_source": None,
    }

    def try_set(seed_value, source_label):
        if seed_value and seed_value != "0":
            info["seed"] = seed_value
            info["seed_source"] = source_label
            return True
        return False

    def fallback_set(seed_value, source_label):
        if seed_value is not None:
            info["seed"] = seed_value
            info["seed_source"] = source_label
            return True
        return False

    # priority 1: explicit seed node
    for node in nodes:
        ntype = node_type(node).lower()
        title = node_title(node).lower()
        inputs = node_inputs(node)
        widgets = node_widgets(node)

        if "seed" in ntype or "seed" in title:
            for candidate in (
                _resolve_value(data, _input_dict_get(inputs, "seed")),
                _resolve_value(data, _input_dict_get(inputs, "noise_seed")),
                widgets[0] if len(widgets) > 0 else None,
            ):
                normalized = _normalize_seed_value(candidate)
                if try_set(normalized, ntype or title or "seed node"):
                    return info

    # priority 2: random noise node
    for node in nodes:
        ntype = node_type(node).lower()
        inputs = node_inputs(node)
        widgets = node_widgets(node)

        if "randomnoise" in ntype or ntype == "randomnoise":
            for candidate in (
                _resolve_value(data, _input_dict_get(inputs, "noise_seed")),
                _resolve_value(data, _input_dict_get(inputs, "seed")),
                widgets[0] if len(widgets) > 0 else None,
            ):
                normalized = _normalize_seed_value(candidate)
                if try_set(normalized, "RandomNoise"):
                    return info

    # priority 3: KSamplerAdvanced with add_noise=enable
    for node in nodes:
        ntype = node_type(node).lower()
        inputs = node_inputs(node)
        widgets = node_widgets(node)

        if "ksampleradvanced" in ntype:
            add_noise = str(_resolve_value(data, _input_dict_get(inputs, "add_noise", ""))).strip().lower()
            candidate = _normalize_seed_value(_resolve_value(data, _input_dict_get(inputs, "noise_seed")))

            if candidate is None and len(widgets) > 1:
                candidate = _normalize_seed_value(widgets[1])

            if add_noise == "enable" and try_set(candidate, "KSamplerAdvanced(add_noise=enable)"):
                return info

    # priority 4: any non-zero sampler seed
    for node in nodes:
        ntype = node_type(node).lower()
        inputs = node_inputs(node)
        widgets = node_widgets(node)

        if "ksampler" in ntype or "sampler" in ntype:
            candidates = [
                _resolve_value(data, _input_dict_get(inputs, "noise_seed")),
                _resolve_value(data, _input_dict_get(inputs, "seed")),
            ]

            if len(widgets) > 1:
                candidates.append(widgets[1])
            if len(widgets) > 0:
                candidates.append(widgets[0])

            for candidate in candidates:
                normalized = _normalize_seed_value(candidate)
                if try_set(normalized, ntype or "sampler"):
                    return info

    # priority 5: last fallback, even 0
    for node in nodes:
        ntype = node_type(node).lower()
        title = node_title(node).lower()
        inputs = node_inputs(node)
        widgets = node_widgets(node)

        if "seed" in ntype or "ksampler" in ntype or "sampler" in ntype or "randomnoise" in ntype:
            candidates = [
                _resolve_value(data, _input_dict_get(inputs, "noise_seed")),
                _resolve_value(data, _input_dict_get(inputs, "seed")),
            ]

            if len(widgets) > 1:
                candidates.append(widgets[1])
            if len(widgets) > 0:
                candidates.append(widgets[0])

            for candidate in candidates:
                normalized = _normalize_seed_value(candidate)
                if fallback_set(normalized, ntype or title or "fallback"):
                    return info

    return info
