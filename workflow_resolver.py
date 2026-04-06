from __future__ import annotations

from workflow_utils import node_inputs, node_title, node_type, node_widgets


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


def _resolve_prompt_dict_ref(data, ref):
    if not isinstance(data, dict):
        return None

    if isinstance(ref, (int, float)):
        return ref

    if isinstance(ref, str):
        return ref

    if isinstance(ref, list) and ref:
        ref_id = str(ref[0])
        node = data.get(ref_id)
        if not isinstance(node, dict):
            return None

        inputs = node.get("inputs", {}) or {}
        widgets = node.get("widgets_values", []) or []
        ntype = node_type(node).lower()
        title = node_title(node).lower()

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
                        return nested
                elif val is not None:
                    return val

        if widgets:
            slot = None
            if len(ref) > 1 and isinstance(ref[1], int):
                slot = ref[1]

            if slot is not None and 0 <= slot < len(widgets):
                return widgets[slot]

            return widgets[0]

        if "math expression" in title or "mathexpression" in ntype:
            expr = inputs.get("expression")
            if isinstance(expr, str):
                a = _resolve_prompt_dict_ref(data, inputs.get("a"))
                if expr.strip().lower() == "a":
                    return a
                if expr.strip().lower() == "a/2" and isinstance(a, (int, float)):
                    return int(a / 2)
                return expr

        return None

    return None


def _resolve_workflow_ref(data, ref, _depth=0):
    if _depth > 12:
        return None

    if not isinstance(data, dict):
        return None

    if isinstance(ref, (int, float, bool)):
        return ref

    if isinstance(ref, str):
        return ref

    if not isinstance(ref, list) or not ref:
        return None

    origin_id = str(ref[0])
    origin_slot = ref[1] if len(ref) > 1 else 0

    nodes_by_id = _build_workflow_index(data)
    node = nodes_by_id.get(origin_id)
    if not isinstance(node, dict):
        return None

    inputs = node_inputs(node)
    widgets = node_widgets(node)
    ntype = node_type(node).lower()
    title = node_title(node).lower()

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
                    return nested
            elif val is not None:
                if key == "expression":
                    a = _resolve_workflow_ref(data, inputs.get("a"), _depth + 1) if isinstance(inputs, dict) else None
                    b = _resolve_workflow_ref(data, inputs.get("b"), _depth + 1) if isinstance(inputs, dict) else None
                    c = _resolve_workflow_ref(data, inputs.get("c"), _depth + 1) if isinstance(inputs, dict) else None
                    resolved_expr = _resolve_math_expression(val, a=a, b=b, c=c)
                    return resolved_expr if resolved_expr is not None else val
                return val

    if "primitiveint" in ntype or "primitiveboolean" in ntype or "floatconstant" in ntype:
        if widgets:
            return widgets[0]

    if "math expression" in title or "mathexpression" in ntype:
        expr = widgets[0] if widgets else (inputs.get("expression") if isinstance(inputs, dict) else None)
        a = _resolve_workflow_ref(data, inputs.get("a"), _depth + 1) if isinstance(inputs, dict) else None
        b = _resolve_workflow_ref(data, inputs.get("b"), _depth + 1) if isinstance(inputs, dict) else None
        c = _resolve_workflow_ref(data, inputs.get("c"), _depth + 1) if isinstance(inputs, dict) else None
        resolved_expr = _resolve_math_expression(expr, a=a, b=b, c=c)
        return resolved_expr if resolved_expr is not None else expr

    if "ksamplerselect" in ntype and widgets:
        return widgets[0]

    if "manualsigmas" in ntype and widgets:
        return widgets[0]

    if widgets:
        if isinstance(origin_slot, int) and 0 <= origin_slot < len(widgets):
            return widgets[origin_slot]
        return widgets[0]

    return None


def _resolve_value(data, value):
    if isinstance(value, list):
        if isinstance(data, dict) and "nodes" in data:
            return _resolve_workflow_ref(data, value)
        return _resolve_prompt_dict_ref(data, value)
    return value