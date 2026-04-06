from __future__ import annotations

from workflow_resolver import _resolve_value
from workflow_utils import _input_dict_get, iter_nodes, node_inputs, node_title, node_type, node_widgets


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


def collect_seed_info(data):
    nodes = iter_nodes(data)

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
