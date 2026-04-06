from __future__ import annotations

from prompt_extractors import (
    extract_from_prompt_dict,
    extract_from_workflow_nodes,
    resolve_prompt_dict_text,
    resolve_workflow_text,
)
from workflow_resolver import _resolve_value, _resolve_workflow_ref
from workflow_utils import (
    _append_unique,
    _coerce_display_value,
    _input_dict_get,
    first_non_empty,
    input_value,
    iter_nodes,
    node_inputs,
    node_title,
    node_type,
    node_widgets,
)

def _normalize_flag_text(value):
    disp = _coerce_display_value(value)
    if disp is None:
        return None
    lower = str(disp).strip().lower()
    mapping = {
        "true": "true",
        "false": "false",
        "yes": "yes",
        "no": "no",
        "enable": "enable",
        "enabled": "enable",
        "disable": "disable",
        "disabled": "disable",
        "on": "on",
        "off": "off",
    }
    return mapping.get(lower, str(disp).strip())


def _set_first(info, key, value, normalizer=None):
    if info.get(key) is not None:
        return
    val = normalizer(value) if normalizer else _coerce_display_value(value)
    if val is not None:
        info[key] = val


def collect_prompt_info(data):
    positive_prompt = extract_from_prompt_dict(data, mode="positive") or extract_from_workflow_nodes(data, mode="positive")
    negative_from_prompt = extract_from_prompt_dict(data, mode="negative")
    negative_prompt = negative_from_prompt if negative_from_prompt is not None else extract_from_workflow_nodes(data, mode="negative")

    return {
        "positive": positive_prompt,
        "negative": negative_prompt,
    }


def collect_node_based_info(data, info):
    nodes = iter_nodes(data)

    for node in nodes:
        ntype = node_type(node).lower()
        title = node_title(node).lower()
        inputs = node_inputs(node)
        widgets = node_widgets(node)

        if any(token in ntype for token in ("cliptextencode", "textencodeqwen", "textencode")):
            text_value = None
            if "nodes" in data:
                text_value = resolve_workflow_text(data, node)
            else:
                text_value = (
                    resolve_prompt_dict_text(data, input_value(inputs, "text"))
                    or resolve_prompt_dict_text(data, input_value(inputs, "prompt"))
                    or resolve_prompt_dict_text(data, input_value(inputs, "value"))
                )

            if text_value is None:
                direct_prompt = _input_dict_get(inputs, "prompt")
                if isinstance(direct_prompt, str) and direct_prompt.strip():
                    text_value = direct_prompt.strip()

            if text_value is None:
                direct_text = _input_dict_get(inputs, "text")
                if isinstance(direct_text, str) and direct_text.strip():
                    text_value = direct_text.strip()

            if "negative" in title:
                if info["negative"] is None:
                    info["negative"] = text_value if text_value is not None else ""
            else:
                if info["positive"] is None and text_value:
                    info["positive"] = text_value

        if ntype == "unetloader":
            val = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "unet_name"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            _append_unique(info["models"], val)

        if ntype == "checkpointloadersimple":
            ckpt = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "ckpt_name"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            _append_unique(info["models"], ckpt)
            if ckpt:
                _append_unique(info["vaes"], f"{ckpt} (checkpoint VAE)")

        if ntype == "cliploader":
            val = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "clip_name"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            _append_unique(info["clips"], val)

        if "textencoderloader" in ntype or "ltxavtextencoderloader" in ntype:
            text_encoder = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "text_encoder"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            _append_unique(info["clips"], text_encoder)

            ckpt = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "ckpt_name"))),
                widgets[1] if len(widgets) > 1 else None,
            ])
            _append_unique(info["models"], ckpt)

        if ntype == "vaeloader":
            val = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "vae_name"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            _append_unique(info["vaes"], val)

        if "audiovaeloader" in ntype:
            ckpt = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "ckpt_name"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            if ckpt:
                _append_unique(info["vaes"], f"{ckpt} (audio VAE)")
                _append_unique(info["models"], ckpt)

        if "latentupscalemodelloader" in ntype:
            model_name = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "model_name"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            _append_unique(info["upscale_models"], model_name)

        if "loraloader" in ntype:
            name = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "lora_name"))),
                widgets[0] if len(widgets) > 0 else None,
            ])
            strength = first_non_empty([
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "strength_model"))),
                widgets[1] if len(widgets) > 1 else None,
            ])
            if name:
                item = str(name)
                if strength is not None:
                    item = f"{item} (strength: {strength})"
                _append_unique(info["loras"], item)

        if ntype in (
            "ksampleradvanced",
            "ksampler",
            "samplercustomadvanced",
            "cfgguider",
            "flux2scheduler",
            "ksamplerselect",
            "ltxvscheduler",
            "manualsigmas",
            "ltxvconditioning",
            "createvideo",
        ):
            steps_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "steps")))
            cfg_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "cfg")))
            sampler_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "sampler_name")))
            scheduler_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "scheduler")))
            fps_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "fps")))
            frame_rate_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "frame_rate")))
            sigmas_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "sigmas")))
            denoise_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "denoise")))
            add_noise_val = _normalize_flag_text(_resolve_value(data, _input_dict_get(inputs, "add_noise")))
            noise_seed_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "noise_seed")))

            _set_first(info, "denoise", denoise_val)
            _set_first(info, "add_noise", add_noise_val, normalizer=_normalize_flag_text)
            if noise_seed_val is not None and str(noise_seed_val).strip() != "":
                _set_first(info, "noise_seed", noise_seed_val)

            if info["steps"] is None and steps_val is not None:
                info["steps"] = steps_val
            if info["cfg"] is None and cfg_val is not None:
                info["cfg"] = cfg_val
            if info["sampler"] is None and sampler_val is not None:
                info["sampler"] = sampler_val
            if info["scheduler"] is None and scheduler_val is not None:
                info["scheduler"] = scheduler_val
            if info["fps"] is None:
                info["fps"] = fps_val or frame_rate_val

            if sigmas_val:
                _append_unique(info["sigmas"], sigmas_val)

            if ntype == "ksampleradvanced":
                if info["add_noise"] is None and len(widgets) > 0:
                    info["add_noise"] = _normalize_flag_text(widgets[0])
                if info["noise_seed"] is None and len(widgets) > 1:
                    info["noise_seed"] = _coerce_display_value(widgets[1])
                if info["steps"] is None and len(widgets) > 3:
                    info["steps"] = _coerce_display_value(widgets[3])
                if info["cfg"] is None and len(widgets) > 4:
                    info["cfg"] = _coerce_display_value(widgets[4])
                if info["sampler"] is None and len(widgets) > 5:
                    info["sampler"] = _coerce_display_value(widgets[5])
                if info["scheduler"] is None and len(widgets) > 6:
                    info["scheduler"] = _coerce_display_value(widgets[6])
                if info["denoise"] is None and len(widgets) > 7:
                    info["denoise"] = _coerce_display_value(widgets[7])

            if ntype == "cfgguider" and info["cfg"] is None and len(widgets) > 0:
                info["cfg"] = _coerce_display_value(widgets[0])

            if ntype == "ksamplerselect" and info["sampler"] is None and len(widgets) > 0:
                info["sampler"] = _coerce_display_value(widgets[0])

            if ntype == "ksampler":
                if info["noise_seed"] is None and len(widgets) > 0:
                    info["noise_seed"] = _coerce_display_value(widgets[0])
                if info["steps"] is None and len(widgets) > 1:
                    info["steps"] = _coerce_display_value(widgets[1])
                if info["cfg"] is None and len(widgets) > 2:
                    info["cfg"] = _coerce_display_value(widgets[2])
                if info["sampler"] is None and len(widgets) > 3:
                    info["sampler"] = _coerce_display_value(widgets[3])
                if info["scheduler"] is None and len(widgets) > 4:
                    info["scheduler"] = _coerce_display_value(widgets[4])
                if info["denoise"] is None and len(widgets) > 5:
                    info["denoise"] = _coerce_display_value(widgets[5])

            if ntype == "flux2scheduler":
                width_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "width")))
                height_val = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "height")))

                if info["width"] is None and width_val is not None:
                    info["width"] = width_val
                if info["height"] is None and height_val is not None:
                    info["height"] = height_val

                if info["steps"] is None and len(widgets) > 0:
                    info["steps"] = _coerce_display_value(widgets[0])
                if info["width"] is None and len(widgets) > 1:
                    info["width"] = _coerce_display_value(widgets[1])
                if info["height"] is None and len(widgets) > 2:
                    info["height"] = _coerce_display_value(widgets[2])

            if ntype == "ltxvscheduler":
                if info["steps"] is None:
                    info["steps"] = _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "steps")))
                if info["scheduler"] is None:
                    info["scheduler"] = "LTXVScheduler"

            if ntype == "manualsigmas" and len(widgets) > 0:
                _append_unique(info["sigmas"], widgets[0])

            if ntype == "ltxvconditioning":
                if info["fps"] is None:
                    info["fps"] = frame_rate_val or (widgets[0] if len(widgets) > 0 else None)

            if ntype == "createvideo":
                if info["fps"] is None:
                    info["fps"] = fps_val or (widgets[0] if len(widgets) > 0 else None)

        if ntype in (
            "wanfirstlastframetovideo",
            "emptylatentimage",
            "emptyflux2latentimage",
            "emptyhunyuanlatentvideo",
            "emptyltxvlatentvideo",
            "ltxvemptylatentaudio",
            "createvideo",
            "loadimage",
            "getimagesize",
            "primitiveint",
            "mathexpression|pysssss",
        ):
            width_candidates = [
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "width"))),
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "resize_type.width"))),
            ]
            height_candidates = [
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "height"))),
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "resize_type.height"))),
            ]
            length_candidates = [
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "length"))),
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "frames_number"))),
            ]
            batch_candidates = [
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "batch_size"))),
            ]
            fps_candidates = [
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "fps"))),
                _coerce_display_value(_resolve_value(data, _input_dict_get(inputs, "frame_rate"))),
            ]

            if info["width"] is None:
                v = first_non_empty(width_candidates)
                if v is not None:
                    info["width"] = str(v)

            if info["height"] is None:
                v = first_non_empty(height_candidates)
                if v is not None:
                    info["height"] = str(v)

            if info["length"] is None:
                v = first_non_empty(length_candidates)
                if v is not None:
                    info["length"] = str(v)

            if info["batch_size"] is None:
                v = first_non_empty(batch_candidates)
                if v is not None:
                    info["batch_size"] = str(v)

            if info["fps"] is None:
                v = first_non_empty(fps_candidates)
                if v is not None:
                    info["fps"] = str(v)

            if ntype == "wanfirstlastframetovideo":
                if info["length"] is None and len(widgets) > 2:
                    info["length"] = _coerce_display_value(widgets[2])

            if ntype == "emptyhunyuanlatentvideo":
                if info["length"] is None and len(widgets) > 2:
                    info["length"] = _coerce_display_value(widgets[2])

            if ntype == "emptyltxvlatentvideo":
                if info["width"] is None and len(widgets) > 0:
                    info["width"] = _coerce_display_value(widgets[0])
                if info["height"] is None and len(widgets) > 1:
                    info["height"] = _coerce_display_value(widgets[1])
                if info["length"] is None and len(widgets) > 2:
                    info["length"] = _coerce_display_value(widgets[2])
                if info["batch_size"] is None and len(widgets) > 3:
                    info["batch_size"] = _coerce_display_value(widgets[3])

            if ntype == "ltxvemptylatentaudio":
                if info["length"] is None and len(widgets) > 0:
                    info["length"] = _coerce_display_value(widgets[0])
                if info["fps"] is None and len(widgets) > 1:
                    info["fps"] = _coerce_display_value(widgets[1])
                if info["batch_size"] is None and len(widgets) > 2:
                    info["batch_size"] = _coerce_display_value(widgets[2])

            if ntype == "createvideo":
                if info["fps"] is None and len(widgets) > 0:
                    info["fps"] = _coerce_display_value(widgets[0])

            if ntype == "primitiveint":
                primitive_title = title.strip().lower()
                if len(widgets) > 0:
                    primitive_val = _coerce_display_value(widgets[0])
                    if primitive_title == "width" and info["width"] is None:
                        info["width"] = primitive_val
                    elif primitive_title == "height" and info["height"] is None:
                        info["height"] = primitive_val
                    elif primitive_title == "length" and info["length"] is None:
                        info["length"] = primitive_val
                    elif primitive_title == "frame rate" and info["fps"] is None:
                        info["fps"] = primitive_val

            if ntype == "mathexpression|pysssss":
                expr = widgets[0] if widgets else None
                resolved_val = _resolve_workflow_ref(data, [str(node.get("id")), 0])
                if expr == "a/2" and resolved_val is not None:
                    pass

    if info["steps"] is None and info["sigmas"]:
        first_sigmas = info["sigmas"][0]
        if isinstance(first_sigmas, str):
            count = len([x for x in first_sigmas.split(",") if x.strip()])
            if count > 0:
                info["steps"] = str(count)

    if info["scheduler"] is None and info["sigmas"]:
        info["scheduler"] = "ManualSigmas"

    return info