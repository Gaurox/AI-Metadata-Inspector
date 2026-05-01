from __future__ import annotations


def _build_prompt_dict_index(data):
    if not isinstance(data, dict):
        return {}
    return {str(k): v for k, v in data.items() if isinstance(v, dict)}


def _build_workflow_index(data):
    nodes = data.get("nodes", []) if isinstance(data, dict) else []
    out = {}
    if isinstance(nodes, list):
        for node in nodes:
            if isinstance(node, dict) and node.get("id") is not None:
                out[str(node.get("id"))] = node
    return out


def _build_workflow_links_by_id(data):
    links = data.get("links", []) if isinstance(data, dict) else []
    out = {}
    if isinstance(links, list):
        for link in links:
            if isinstance(link, list) and len(link) >= 6:
                out[link[0]] = {
                    "origin_id": str(link[1]),
                    "origin_slot": link[2],
                    "target_id": str(link[3]),
                    "target_slot": link[4],
                    "type": link[5],
                }
            elif isinstance(link, dict) and "id" in link:
                out[link["id"]] = link
    return out


def _resolve_math_expression(expr, a=None, b=None, c=None):
    if not isinstance(expr, str):
        return None

    e = expr.strip().lower()
    if e == "a":
        return a
    if e == "b":
        return b
    if e == "c":
        return c
    if e == "a/2" and isinstance(a, (int, float)):
        return int(a / 2)
    if e == "a*2" and isinstance(a, (int, float)):
        return a * 2
    if e == "a+1" and isinstance(a, (int, float)):
        return a + 1
    if e == "a-1" and isinstance(a, (int, float)):
        return a - 1
    return None


_RESOLUTION_CACHE: dict[tuple[int, str, str], object] = {}


def _cache_key(data, kind: str, ref):
    return (id(data), kind, repr(ref))


def _cache_get(data, kind: str, ref):
    return _RESOLUTION_CACHE.get(_cache_key(data, kind, ref), None)


def _cache_set(data, kind: str, ref, value):
    _RESOLUTION_CACHE[_cache_key(data, kind, ref)] = value
    return value


def _resolve_prompt_dict_ref(data, ref):
    cached = _cache_get(data, "prompt_dict", ref)
    if cached is not None:
        return cached

    result = None

    if isinstance(data, dict):
        if isinstance(ref, (int, float)):
            result = ref
        elif isinstance(ref, str):
            result = ref
        elif isinstance(ref, list) and ref:
            ref_id = str(ref[0])
            node = data.get(ref_id)
            if isinstance(node, dict):
                inputs = node.get("inputs", {}) or {}
                widgets = node.get("widgets_values", []) or []
                ntype = str(node.get("class_type", "") or node.get("type", "") or "").lower()
                meta = node.get("_meta", {}) or {}
                title = str(meta.get("title", "") or node.get("title", "") or "").lower()

                for key in (
                    "value",
                    "text",
                    "prompt",
                    "width",
                    "height",
                    "length",
                    "frame_rate",
                    "fps",
                    "cfg",
                    "steps",
                    "noise_seed",
                    "seed",
                    "ckpt_name",
                    "clip_name",
                    "text_encoder",
                    "vae_name",
                    "model_name",
                    "lora_name",
                    "sampler_name",
                    "scheduler",
                    "sigmas",
                    "expression",
                ):
                    if key in inputs:
                        val = inputs.get(key)
                        if isinstance(val, list):
                            nested = _resolve_prompt_dict_ref(data, val)
                            if nested is not None:
                                result = nested
                                break
                        elif val is not None:
                            result = val
                            break

                if result is None and widgets:
                    slot = None
                    if len(ref) > 1 and isinstance(ref[1], int):
                        slot = ref[1]

                    if slot is not None and 0 <= slot < len(widgets):
                        result = widgets[slot]
                    else:
                        result = widgets[0]

                if result is None and ("math expression" in title or "mathexpression" in ntype):
                    expr = inputs.get("expression")
                    if isinstance(expr, str):
                        a = _resolve_prompt_dict_ref(data, inputs.get("a"))
                        if expr.strip().lower() == "a":
                            result = a
                        elif expr.strip().lower() == "a/2" and isinstance(a, (int, float)):
                            result = int(a / 2)
                        else:
                            result = expr

    return _cache_set(data, "prompt_dict", ref, result)


def _resolve_workflow_ref(data, ref, _depth=0):
    cached = _cache_get(data, "workflow", ref)
    if cached is not None:
        return cached

    if _depth > 12:
        return _cache_set(data, "workflow", ref, None)

    result = None

    if isinstance(data, dict):
        if isinstance(ref, (int, float, bool)):
            result = ref
        elif isinstance(ref, str):
            result = ref
        elif isinstance(ref, list) and ref:
            origin_id = str(ref[0])
            origin_slot = ref[1] if len(ref) > 1 else 0

            nodes_by_id = _build_workflow_index(data)
            node = nodes_by_id.get(origin_id)
            if isinstance(node, dict):
                inputs = node.get("inputs", {}) or []
                widgets = node.get("widgets_values", []) or []
                ntype = str(node.get("class_type", "") or node.get("type", "") or "").lower()
                meta = node.get("_meta", {}) or {}
                title = str(meta.get("title", "") or node.get("title", "") or "").lower()

                for key in (
                    "value",
                    "text",
                    "prompt",
                    "width",
                    "height",
                    "length",
                    "frame_rate",
                    "fps",
                    "cfg",
                    "steps",
                    "noise_seed",
                    "seed",
                    "ckpt_name",
                    "clip_name",
                    "text_encoder",
                    "vae_name",
                    "model_name",
                    "lora_name",
                    "sampler_name",
                    "scheduler",
                    "sigmas",
                    "expression",
                ):
                    if isinstance(inputs, dict) and key in inputs:
                        val = inputs.get(key)
                        if isinstance(val, list):
                            nested = _resolve_workflow_ref(data, val, _depth + 1)
                            if nested is not None:
                                result = nested
                                break
                        elif val is not None:
                            if key == "expression":
                                a = _resolve_workflow_ref(data, inputs.get("a"), _depth + 1) if isinstance(inputs, dict) else None
                                b = _resolve_workflow_ref(data, inputs.get("b"), _depth + 1) if isinstance(inputs, dict) else None
                                c = _resolve_workflow_ref(data, inputs.get("c"), _depth + 1) if isinstance(inputs, dict) else None
                                resolved_expr = _resolve_math_expression(val, a=a, b=b, c=c)
                                result = resolved_expr if resolved_expr is not None else val
                            else:
                                result = val
                            break

                if result is None and ("primitiveint" in ntype or "primitiveboolean" in ntype or "floatconstant" in ntype):
                    if widgets:
                        result = widgets[0]

                if result is None and ("math expression" in title or "mathexpression" in ntype):
                    expr = widgets[0] if widgets else (inputs.get("expression") if isinstance(inputs, dict) else None)
                    a = _resolve_workflow_ref(data, inputs.get("a"), _depth + 1) if isinstance(inputs, dict) else None
                    b = _resolve_workflow_ref(data, inputs.get("b"), _depth + 1) if isinstance(inputs, dict) else None
                    c = _resolve_workflow_ref(data, inputs.get("c"), _depth + 1) if isinstance(inputs, dict) else None
                    resolved_expr = _resolve_math_expression(expr, a=a, b=b, c=c)
                    result = resolved_expr if resolved_expr is not None else expr

                if result is None and "ksamplerselect" in ntype and widgets:
                    result = widgets[0]

                if result is None and "manualsigmas" in ntype and widgets:
                    result = widgets[0]

                if result is None and widgets:
                    if isinstance(origin_slot, int) and 0 <= origin_slot < len(widgets):
                        result = widgets[origin_slot]
                    else:
                        result = widgets[0]

    return _cache_set(data, "workflow", ref, result)


def _resolve_value(data, value):
    if isinstance(value, list):
        if isinstance(data, dict) and "nodes" in data:
            return _resolve_workflow_ref(data, value)
        return _resolve_prompt_dict_ref(data, value)
    return value
