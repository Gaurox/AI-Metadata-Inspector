from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any


def _safe_text(value: Any, empty_text: str = "(not found)") -> str:
    if value is None:
        return empty_text
    text = str(value).strip()
    return text if text else empty_text


def _multiline_to_lines(value: Any) -> list[str]:
    text = str(value or "").replace("\r", "")
    return [line for line in text.split("\n") if line.strip()]


def _copy_text(root: tk.Tk, text: Any) -> None:
    root.clipboard_clear()
    root.clipboard_append("" if text is None else str(text))
    root.update_idletasks()


class _ScrollableFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Enter>", self._bind_mousewheel)
        self.inner.bind("<Leave>", self._unbind_mousewheel)

    def _on_inner_configure(self, _event: tk.Event[Any]) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event[Any]) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event: tk.Event[Any]) -> None:
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _unbind_mousewheel(self, _event: tk.Event[Any]) -> None:
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event: tk.Event[Any]) -> None:
        delta = getattr(event, "delta", 0)
        if delta:
            self.canvas.yview_scroll(int(-delta / 120), "units")

    def _on_mousewheel_linux(self, event: tk.Event[Any]) -> None:
        num = getattr(event, "num", None)
        if num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif num == 5:
            self.canvas.yview_scroll(1, "units")


def _add_section_title(parent: ttk.Frame, title: str, row: int) -> int:
    label = ttk.Label(parent, text=title, style="SectionTitle.TLabel")
    label.grid(row=row, column=0, sticky="w", padx=12, pady=(16 if row else 8, 6))
    return row + 1


def _add_kv_rows(parent: ttk.Frame, row: int, items: list[tuple[str, Any]], wrap: int = 720) -> int:
    for label_text, value in items:
        ttk.Label(parent, text=f"{label_text}:", style="FieldLabel.TLabel").grid(
            row=row, column=0, sticky="nw", padx=(20, 8), pady=2
        )
        ttk.Label(
            parent,
            text=_safe_text(value),
            style="FieldValue.TLabel",
            wraplength=wrap,
            justify="left",
        ).grid(row=row, column=1, sticky="nw", padx=(0, 12), pady=2)
        row += 1
    return row


def _add_summary(parent: ttk.Frame, row: int, items: list[tuple[str, Any]]) -> int:
    row = _add_section_title(parent, "SUMMARY", row)

    summary = ttk.Frame(parent, style="Card.TFrame")
    summary.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))

    for index, (label_text, value) in enumerate(items):
        col = index % 4
        item_row = (index // 4) * 2
        summary.grid_columnconfigure(col, weight=1, uniform="summary")

        ttk.Label(summary, text=label_text, style="FieldLabel.TLabel").grid(
            row=item_row,
            column=col,
            sticky="w",
            padx=8,
            pady=(8, 0),
        )
        ttk.Label(
            summary,
            text=_safe_text(value),
            style="FieldValue.TLabel",
            wraplength=170,
            justify="left",
        ).grid(row=item_row + 1, column=col, sticky="nw", padx=8, pady=(0, 8))

    return row + 1


def _add_text_block(
    parent: ttk.Frame,
    root: tk.Tk,
    row: int,
    title: str,
    text: Any,
    copy_label: str,
    height: int = 8,
) -> int:
    row = _add_section_title(parent, title, row)

    block = ttk.Frame(parent, style="Card.TFrame")
    block.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12)
    block.grid_columnconfigure(0, weight=1)

    text_widget = tk.Text(
        block,
        wrap="word",
        height=height,
        relief="solid",
        borderwidth=1,
        padx=8,
        pady=6,
    )
    text_widget.insert("1.0", _safe_text(text, empty_text=""))
    text_widget.configure(state="disabled")
    text_widget.grid(row=0, column=0, sticky="ew", padx=(8, 8), pady=(8, 6))

    button_bar = ttk.Frame(block)
    button_bar.grid(row=1, column=0, sticky="e", padx=8, pady=(0, 8))
    ttk.Button(button_bar, text=copy_label, command=lambda: _copy_text(root, text)).grid(row=0, column=0)

    return row + 1


def _add_simple_list(parent: ttk.Frame, row: int, title: str, lines: list[str]) -> int:
    row = _add_section_title(parent, title, row)
    if not lines:
        lines = ["(none found)"]

    for line in lines:
        ttk.Label(
            parent,
            text=f"• {line}",
            style="FieldValue.TLabel",
            wraplength=760,
            justify="left",
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=(20, 12), pady=2)
        row += 1
    return row


def _add_sampler_passes(parent: ttk.Frame, row: int, samplers: list[dict[str, Any]]) -> int:
    row = _add_section_title(parent, "SAMPLER PASSES", row)
    if not samplers:
        ttk.Label(parent, text="(none found)", style="FieldValue.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", padx=(20, 12), pady=2
        )
        return row + 1

    for sampler in samplers:
        card = ttk.Frame(parent, style="Card.TFrame")
        card.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        card.grid_columnconfigure(1, weight=1)

        ttk.Label(
            card,
            text=_safe_text(sampler.get("label"), "Sampler Pass"),
            style="SubTitle.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 6))

        details = [
            ("Node ID", sampler.get("node_id")),
            ("Type", sampler.get("node_type")),
            ("Seed", sampler.get("seed")),
            ("Noise Seed", sampler.get("noise_seed")),
            ("Add Noise", sampler.get("add_noise")),
            ("Denoise", sampler.get("denoise")),
            ("Steps", sampler.get("steps")),
            ("CFG", sampler.get("cfg")),
            ("Sampler", sampler.get("sampler")),
            ("Scheduler", sampler.get("scheduler")),
            ("Start Step", sampler.get("start_at_step")),
            ("End Step", sampler.get("end_at_step")),
            ("Leftover Noise", sampler.get("return_with_leftover_noise")),
        ]
        _ = _add_kv_rows(card, 1, details, wrap=700)
        row += 1

    return row


def _is_video_payload(payload: dict[str, Any]) -> bool:
    file_type = str(payload.get("file_type", "") or "").upper()
    mime = str(payload.get("mime", "") or "").lower()
    return mime.startswith("video/") or any(token in file_type for token in ("MP4", "MOV", "AVI", "MKV", "WEBM", "M4V", "VIDEO"))


def _is_clean_number(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        float(text)
        return True
    except Exception:
        return False


def show_info_window_py(payload: dict[str, Any]) -> bool:
    root = tk.Tk()
    root.title("AI Metadata Inspector v1.3.3")
    icon_path = Path(__file__).resolve().parent / "icons" / "app.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except Exception:
            pass
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    width = min(860, max(760, screen_w - 80))
    height = min(900, max(640, screen_h - 100))
    root.geometry(f"{width}x{height}")
    root.minsize(760, 640)

    style = ttk.Style(root)
    try:
        style.theme_use("vista")
    except Exception:
        try:
            style.theme_use("clam")
        except Exception:
            pass

    style.configure("SectionTitle.TLabel", font=("Segoe UI", 11, "bold"))
    style.configure("SubTitle.TLabel", font=("Segoe UI", 10, "bold"))
    style.configure("FieldLabel.TLabel", font=("Segoe UI", 9, "bold"))
    style.configure("FieldValue.TLabel", font=("Segoe UI", 9))
    style.configure("Card.TFrame", relief="solid", borderwidth=1)

    outer = ttk.Frame(root, padding=8)
    outer.pack(fill="both", expand=True)
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(1, weight=1)

    header = ttk.Frame(outer)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    header.grid_columnconfigure(0, weight=1)

    ttk.Label(header, text="AI Metadata Inspector", style="SectionTitle.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Label(header, text=_safe_text(payload.get("file_name"), "(unknown file)"), style="FieldValue.TLabel").grid(
        row=1, column=0, sticky="w", pady=(2, 0)
    )
    ttk.Label(
        header,
        text=_safe_text(payload.get("file_path"), ""),
        style="FieldValue.TLabel",
        wraplength=620,
        justify="left",
    ).grid(row=2, column=0, sticky="w", pady=(2, 0))

    button_bar = ttk.Frame(header)
    button_bar.grid(row=3, column=0, sticky="w", pady=(8, 0))
    ttk.Button(button_bar, text="Copy Positive", command=lambda: _copy_text(root, payload.get("positive", ""))).grid(row=0, column=0, padx=(0, 6))
    ttk.Button(button_bar, text="Copy Negative", command=lambda: _copy_text(root, payload.get("negative", ""))).grid(row=0, column=1, padx=(0, 6))
    ttk.Button(button_bar, text="Copy Seed", command=lambda: _copy_text(root, payload.get("seed", ""))).grid(row=0, column=2, padx=(0, 6))
    ttk.Button(button_bar, text="Copy All", command=lambda: _copy_text(root, payload.get("copy_all", ""))).grid(row=0, column=3, padx=(0, 6))
    ttk.Button(button_bar, text="Close", command=root.destroy).grid(row=0, column=4)

    scrollable = _ScrollableFrame(outer)
    scrollable.grid(row=1, column=0, sticky="nsew")
    content = scrollable.inner
    content.grid_columnconfigure(1, weight=1)

    row = 0
    row = _add_section_title(content, "FILE", row)
    file_rows = [
        ("Path", payload.get("file_path")),
        ("Name", payload.get("file_name")),
        ("Extension", payload.get("extension")),
        ("File type", payload.get("file_type")),
        ("File size", payload.get("file_size")),
        ("Bitrate", payload.get("bitrate")),
    ]
    is_video = _is_video_payload(payload)
    if is_video:
        file_rows.append(("Duration", payload.get("duration")))
    if is_video and str(payload.get("media_fps", "") or "").strip():
        file_rows.append(("Media FPS", payload.get("media_fps")))

    row = _add_kv_rows(
        content,
        row,
        file_rows,
    )

    model_lines: list[str] = []
    for label, key in (
        ("UNET / main model", "model"),
        ("CLIP", "clips"),
        ("VAE", "vae"),
        ("LoRAs", "loras"),
        ("Upscale models", "upscale_models"),
        ("Sigmas", "sigmas"),
    ):
        value = str(payload.get(key, "") or "").strip()
        if value:
            for part in _multiline_to_lines(value.replace(" | ", "\n")):
                model_lines.append(f"{label}: {part}")
        else:
            model_lines.append(f"{label}: (none found)")
    row = _add_simple_list(content, row, "MODELS", model_lines)

    row = _add_text_block(content, root, row, "POSITIVE PROMPT", payload.get("positive"), "Copy Positive", height=10)
    row = _add_text_block(content, root, row, "NEGATIVE PROMPT", payload.get("negative"), "Copy Negative", height=7)

    row = _add_section_title(content, "GENERATION SETTINGS", row)
    generation_rows = [
        ("Seed", payload.get("seed")),
        ("Seed source", payload.get("seed_source")),
        ("Noise seed", payload.get("noise_seed")),
        ("Denoise", payload.get("denoise")),
        ("Add noise", payload.get("add_noise")),
        ("Steps", payload.get("steps")),
        ("CFG", payload.get("cfg")),
        ("Sampler", payload.get("sampler")),
        ("Scheduler", payload.get("scheduler")),
        ("File dimensions", payload.get("file_dimensions")),
        ("Batch size", payload.get("batch_size")),
    ]
    if is_video:
        generation_rows.append(("Length / frames", payload.get("length_frames")))
    if _is_clean_number(payload.get("workflow_fps")):
        generation_rows.append(("Workflow FPS", payload.get("workflow_fps")))
    generation_rows.extend(
        [
            ("Prompt source", payload.get("prompt_source")),
            ("Confidence", payload.get("confidence")),
        ]
    )
    row = _add_kv_rows(content, row, generation_rows)

    row = _add_sampler_passes(content, row, payload.get("samplers_details") or [])

    source_lines = _multiline_to_lines(payload.get("found_tags", ""))
    row = _add_simple_list(content, row, "METADATA SOURCES", source_lines or ["No metadata source detected"])

    root.after(0, lambda: scrollable.canvas.yview_moveto(0.0))
    root.mainloop()
    return True
