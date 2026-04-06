from __future__ import annotations


def iter_nodes(data):
    if not isinstance(data, dict):
        return []

    if "nodes" in data and isinstance(data["nodes"], list):
        return [n for n in data["nodes"] if isinstance(n, dict)]

    return [n for n in data.values() if isinstance(n, dict) and ("class_type" in n or "inputs" in n)]


def node_type(node):
    return str(node.get("class_type", "") or node.get("type", "") or "")


def node_title(node):
    meta = node.get("_meta", {}) or {}
    return str(meta.get("title", "") or node.get("title", "") or "")


def node_inputs(node):
    raw = node.get("inputs", {})
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return raw
    return {}


def node_widgets(node):
    raw = node.get("widgets_values", []) or []
    return raw if isinstance(raw, list) else []


def first_non_empty(values):
    for v in values:
        if v is None:
            continue
        if isinstance(v, str):
            if v.strip():
                return v.strip()
        else:
            return v
    return None


def _input_dict_get(inputs, key, default=None):
    if isinstance(inputs, dict):
        return inputs.get(key, default)
    return default


def _input_list_get(inputs, key, default=None):
    if not isinstance(inputs, list):
        return default

    key_lower = str(key).strip().lower()
    for item in inputs:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip().lower()
        if name == key_lower:
            if "widget" in item and isinstance(item["widget"], dict):
                widget_name = str(item["widget"].get("name", "")).strip().lower()
                if widget_name == key_lower:
                    return item.get("link", default)
            return item.get("link", default)
    return default


def input_value(inputs, key, default=None):
    if isinstance(inputs, dict):
        return inputs.get(key, default)

    if isinstance(inputs, list):
        found = _input_list_get(inputs, key, None)
        return default if found is None else found

    return default


def _coerce_display_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return str(value)


def _append_unique(target_list, value):
    disp = _coerce_display_value(value)
    if disp and disp not in target_list:
        target_list.append(disp)