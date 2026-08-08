from __future__ import annotations

import ast
import math


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


def _resolve_math_expression(expr, a=None, b=None, c=None, variables=None):
    if not isinstance(expr, str):
        return None

    expression = expr.strip()
    if not expression or len(expression) > 512:
        return None

    values = {"a": a, "b": b, "c": c}
    if isinstance(variables, dict):
        values.update(variables)

    allowed_binary = {
        ast.Add: lambda left, right: left + right,
        ast.Sub: lambda left, right: left - right,
        ast.Mult: lambda left, right: left * right,
        ast.Div: lambda left, right: left / right,
        ast.FloorDiv: lambda left, right: left // right,
        ast.Mod: lambda left, right: left % right,
    }
    allowed_unary = {
        ast.UAdd: lambda value: +value,
        ast.USub: lambda value: -value,
    }
    allowed_calls = {
        "abs": abs,
        "ceil": math.ceil,
        "floor": math.floor,
        "max": max,
        "min": min,
        "round": round,
    }

    def evaluate(node, depth=0):
        if depth > 32:
            raise ValueError("expression too deep")

        if isinstance(node, ast.Expression):
            return evaluate(node.body, depth + 1)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return node.value
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("unsupported constant")

        if isinstance(node, ast.Name):
            value = values.get(node.id)
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return value
            raise ValueError("unknown variable")

        if isinstance(node, ast.BinOp) and type(node.op) in allowed_binary:
            left = evaluate(node.left, depth + 1)
            right = evaluate(node.right, depth + 1)
            return allowed_binary[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary:
            return allowed_unary[type(node.op)](evaluate(node.operand, depth + 1))

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func = allowed_calls.get(node.func.id)
            if func is None or node.keywords or len(node.args) > 8:
                raise ValueError("unsupported call")
            return func(*(evaluate(arg, depth + 1) for arg in node.args))

        raise ValueError("unsupported expression")

    try:
        parsed = ast.parse(expression, mode="eval")
        result = evaluate(parsed)
        if isinstance(result, float) and not math.isfinite(result):
            return None
        if isinstance(result, (int, float)) and abs(result) > 10**15:
            return None
        return result
    except (ArithmeticError, SyntaxError, TypeError, ValueError):
        return None


_RESOLUTION_CACHE: dict[tuple[int, str, str], object] = {}


def _cache_key(data, kind: str, ref):
    return (id(data), kind, repr(ref))


def _cache_get(data, kind: str, ref):
    return _RESOLUTION_CACHE.get(_cache_key(data, kind, ref), None)


def _cache_set(data, kind: str, ref, value):
    _RESOLUTION_CACHE[_cache_key(data, kind, ref)] = value
    return value


def _workflow_link_by_id(data, link_id):
    links_by_id = _build_workflow_links_by_id(data)
    if link_id in links_by_id:
        return links_by_id[link_id]

    wanted = str(link_id)
    for candidate_id, link in links_by_id.items():
        if str(candidate_id) == wanted:
            return link
    return None


def _resolve_reference_source(data, ref):
    """Return the source node and output slot without coercing its output."""
    if not isinstance(data, dict):
        return None, None

    if "nodes" not in data:
        if not isinstance(ref, list) or not ref:
            return None, None
        node = _build_prompt_dict_index(data).get(str(ref[0]))
        slot = ref[1] if len(ref) > 1 else 0
        return node, slot

    nodes_by_id = _build_workflow_index(data)

    if isinstance(ref, list) and ref:
        return nodes_by_id.get(str(ref[0])), ref[1] if len(ref) > 1 else 0

    link = _workflow_link_by_id(data, ref)
    if not isinstance(link, dict):
        return None, None

    origin_id = link.get("origin_id")
    if origin_id is None:
        return None, None
    origin_slot = link.get("origin_slot", 0)
    return nodes_by_id.get(str(origin_id)), origin_slot


def _resolve_input_source(data, node, input_name):
    """Resolve a named node input to its upstream node, preserving object outputs."""
    if not isinstance(node, dict):
        return None, None

    inputs = node.get("inputs", {}) or {}
    if isinstance(inputs, dict):
        return _resolve_reference_source(data, inputs.get(input_name))

    if isinstance(inputs, list):
        wanted = str(input_name).strip().lower()
        for item in inputs:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip().lower()
            if name == wanted:
                return _resolve_reference_source(data, item.get("link"))

    return None, None


def _prompt_math_variables(data, inputs, depth, visited):
    variables = {}
    if not isinstance(inputs, dict):
        return variables

    for key, raw_value in inputs.items():
        key_text = str(key).strip().lower()
        if key_text in ("a", "b", "c"):
            variable_name = key_text
        elif key_text.startswith("values.") and key_text[7:] in ("a", "b", "c"):
            variable_name = key_text[7:]
        else:
            continue

        variables[variable_name] = _resolve_prompt_dict_ref(
            data,
            raw_value,
            _depth=depth + 1,
            _visited=visited,
        )

    return variables


def _cast_math_output(ntype, slot, value):
    if value is None:
        return None
    if "comfymathexpression" not in ntype:
        return value
    if slot == 1:
        return int(value)
    if slot == 2:
        return bool(value)
    return value


def _resolve_prompt_dict_ref(data, ref, _depth=0, _visited=None):
    cached = _cache_get(data, "prompt_dict", ref)
    if cached is not None:
        return cached

    if _depth > 12:
        return _cache_set(data, "prompt_dict", ref, None)

    if _visited is None:
        _visited = set()
    visit_key = repr(ref)
    if visit_key in _visited:
        return _cache_set(data, "prompt_dict", ref, None)
    visited = set(_visited)
    visited.add(visit_key)

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

                if "mathexpression" in ntype or "math expression" in title:
                    expr = inputs.get("expression") if isinstance(inputs, dict) else None
                    variables = _prompt_math_variables(data, inputs, _depth, visited)
                    resolved_expr = _resolve_math_expression(expr, variables=variables)
                    result = _cast_math_output(ntype, ref[1] if len(ref) > 1 else 0, resolved_expr)

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
                ):
                    if result is not None:
                        break
                    if key in inputs:
                        val = inputs.get(key)
                        if isinstance(val, list):
                            nested = _resolve_prompt_dict_ref(data, val, _depth + 1, visited)
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
