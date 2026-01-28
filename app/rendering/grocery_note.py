"""Render a structured grocery list to a monochrome Pillow Image."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from app.rendering.text_layout import measure, wrap_text

# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

_FONT_CACHE: dict[tuple[str, int], ImageFont.ImageFont] = {}


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Try to load DejaVuSans; fall back to Pillow default."""
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    key = (name, size)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = ImageFont.truetype(name, size)
        except Exception:
            try:
                _FONT_CACHE[key] = ImageFont.truetype("DejaVuSans-Bold.ttf", size)
            except Exception:
                _FONT_CACHE[key] = ImageFont.load_default(size)
    return _FONT_CACHE[key]


# ---------------------------------------------------------------------------
# Checkbox drawing
# ---------------------------------------------------------------------------

def _draw_checkbox(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int,
    checked: bool,
    font: ImageFont.ImageFont,
) -> int:
    """Draw a checkbox glyph and return its width (including trailing space)."""
    # Try Unicode glyphs first.
    glyph = "☑" if checked else "☐"
    glyph_w = measure(glyph, font, draw)
    # If the font actually renders the glyph (nonzero width and not a tofu box),
    # use it; otherwise fall back to manual drawing.
    if glyph_w > 0:
        draw.text((x, y), glyph, font=font, fill=0)
        return int(glyph_w) + 4

    # Manual box
    box_size = size - 4
    x0, y0 = x + 2, y + 2
    x1, y1 = x0 + box_size, y0 + box_size
    draw.rectangle([x0, y0, x1, y1], outline=0, width=1)
    if checked:
        draw.line([x0, y0, x1, y1], fill=0, width=1)
        draw.line([x0, y1, x1, y0], fill=0, width=1)
    return box_size + 6


# ---------------------------------------------------------------------------
# Public rendering function
# ---------------------------------------------------------------------------

def render_grocery_note(payload: dict) -> Image.Image:
    """Render *payload* to a 1-bit monochrome ``Image``.

    See module / project docs for the expected payload schema.
    """
    title: str = payload.get("title", "Grocery List")
    areas: list[dict] = payload.get("areas", [])
    opts: dict = payload.get("options", {})

    width_px: int = opts.get("width_px", 576)
    margin: int = opts.get("margin_px", 16)
    line_gap: int = opts.get("line_gap_px", 6)
    include_checked: bool = opts.get("include_checked", False)

    usable_w = width_px - 2 * margin

    # Fonts
    title_font = _load_font(28, bold=True)
    header_font = _load_font(22, bold=True)
    item_font = _load_font(20)

    # Column layout
    left_col_w = 110  # qty+unit column
    checkbox_size = 20
    right_col_x_offset = left_col_w + checkbox_size + 8
    right_col_w = usable_w - right_col_x_offset

    # --- First pass: compute height ---
    # We draw onto a scratch image just for measurement.
    scratch = Image.new("1", (width_px, 1), 1)
    sd = ImageDraw.Draw(scratch)

    y = margin
    # Title
    y += _text_block_height(title, title_font, sd, usable_w, line_gap)
    y += line_gap * 2  # extra space after title

    for area in areas:
        items = area.get("items", [])
        if not include_checked:
            items = [it for it in items if not it.get("checked", False)]
        if not items:
            continue

        # Area header
        y += _line_height(header_font) + 4  # header + underline
        y += line_gap

        for item in items:
            item_text = _item_label(item)
            wrapped = wrap_text(item_text, item_font, sd, right_col_w)
            row_h = max(_line_height(item_font), len(wrapped) * (_line_height(item_font) + line_gap) - line_gap)
            y += row_h + line_gap

        y += line_gap  # section gap

    height = y + margin

    # --- Second pass: draw ---
    img = Image.new("1", (width_px, height), 1)
    draw = ImageDraw.Draw(img)

    y = margin

    # Title
    for line in wrap_text(title, title_font, draw, usable_w):
        draw.text((margin, y), line, font=title_font, fill=0)
        y += _line_height(title_font) + line_gap
    y += line_gap  # extra space

    for area in areas:
        items = area.get("items", [])
        if not include_checked:
            items = [it for it in items if not it.get("checked", False)]
        if not items:
            continue

        # Area header (inverted bar)
        header_h = _line_height(header_font) + 4
        draw.rectangle(
            [margin, y, margin + usable_w, y + header_h],
            fill=0,
        )
        draw.text((margin + 4, y + 2), area.get("name", ""), font=header_font, fill=1)
        y += header_h + line_gap

        for item in items:
            checked = item.get("checked", False)
            qty_unit = f"{item.get('qty', '')} {item.get('unit', '')}".strip()

            # Right-align qty+unit in left column
            qty_w = measure(qty_unit, item_font, draw)
            qty_x = margin + left_col_w - qty_w
            draw.text((qty_x, y), qty_unit, font=item_font, fill=0)

            # Checkbox
            cb_x = margin + left_col_w + 2
            cb_w = _draw_checkbox(draw, cb_x, y, checkbox_size, checked, item_font)

            # Item text (wrapped)
            item_text = _item_label(item)
            text_x = margin + right_col_x_offset
            wrapped = wrap_text(item_text, item_font, draw, right_col_w)
            line_y = y
            for wl in wrapped:
                draw.text((text_x, line_y), wl, font=item_font, fill=0)
                line_y += _line_height(item_font) + line_gap

            row_h = max(
                _line_height(item_font),
                len(wrapped) * (_line_height(item_font) + line_gap) - line_gap,
            )
            y += row_h + line_gap

        y += line_gap  # section gap

    # Crop to actual content height
    img = img.crop((0, 0, width_px, y + margin))
    return img


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _line_height(font: ImageFont.ImageFont) -> int:
    bbox = font.getbbox("Ay")
    return bbox[3] - bbox[1]


def _text_block_height(
    text: str,
    font: ImageFont.ImageFont,
    draw: ImageDraw.ImageDraw,
    max_w: float,
    gap: int,
) -> int:
    lines = wrap_text(text, font, draw, max_w)
    lh = _line_height(font)
    return len(lines) * lh + (len(lines) - 1) * gap


def _item_label(item: dict) -> str:
    name = item.get("name", "")
    note = item.get("note", "")
    if note:
        return f"{name} ({note})"
    return name
