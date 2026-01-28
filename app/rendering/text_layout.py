"""Pixel-based text measurement, wrapping, and ellipsizing."""

from PIL import ImageDraw, ImageFont


def measure(text: str, font: ImageFont.ImageFont, draw: ImageDraw.ImageDraw) -> float:
    """Return the pixel width of *text* rendered with *font*."""
    return draw.textlength(text, font=font)


def wrap_text(
    text: str,
    font: ImageFont.ImageFont,
    draw: ImageDraw.ImageDraw,
    max_width_px: float,
) -> list[str]:
    """Word-wrap *text* so no line exceeds *max_width_px*.

    - Wraps on spaces.
    - If a single word is wider than *max_width_px* it is hard-broken
      character-by-character.
    """
    if not text:
        return [""]

    words = text.split(" ")
    lines: list[str] = []
    current = ""

    for word in words:
        # Hard-break words that are too wide on their own.
        if measure(word, font, draw) > max_width_px:
            # Flush anything accumulated first.
            if current:
                lines.append(current)
                current = ""
            lines.extend(_hard_break(word, font, draw, max_width_px))
            continue

        candidate = f"{current} {word}" if current else word
        if measure(candidate, font, draw) <= max_width_px:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines if lines else [""]


def _hard_break(
    word: str,
    font: ImageFont.ImageFont,
    draw: ImageDraw.ImageDraw,
    max_width_px: float,
) -> list[str]:
    """Break a single word into lines that each fit within *max_width_px*."""
    lines: list[str] = []
    buf = ""
    for ch in word:
        candidate = buf + ch
        if measure(candidate, font, draw) > max_width_px:
            if buf:
                lines.append(buf)
            buf = ch
        else:
            buf = candidate
    if buf:
        lines.append(buf)
    return lines


def ellipsize(
    text: str,
    font: ImageFont.ImageFont,
    draw: ImageDraw.ImageDraw,
    max_width_px: float,
) -> str:
    """Return *text* truncated with an ellipsis suffix if it exceeds *max_width_px*."""
    if measure(text, font, draw) <= max_width_px:
        return text

    # Pick ellipsis glyph – fall back to "..." if font can't render "…".
    ellipsis_char = "…"
    try:
        if measure(ellipsis_char, font, draw) == 0:
            ellipsis_char = "..."
    except Exception:
        ellipsis_char = "..."

    for end in range(len(text), 0, -1):
        candidate = text[:end] + ellipsis_char
        if measure(candidate, font, draw) <= max_width_px:
            return candidate

    return ellipsis_char
