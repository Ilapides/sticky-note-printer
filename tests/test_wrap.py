"""Tests for text_layout: wrap_text and ellipsize."""

import pytest
from PIL import Image, ImageDraw, ImageFont

from app.rendering.text_layout import measure, wrap_text, ellipsize


@pytest.fixture
def draw():
    img = Image.new("1", (800, 100), 1)
    return ImageDraw.Draw(img)


@pytest.fixture
def font():
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except Exception:
        return ImageFont.load_default(20)


class TestWrapText:
    def test_no_line_exceeds_max_width(self, font, draw):
        text = "The quick brown fox jumps over the lazy dog and keeps on running"
        max_w = 200
        lines = wrap_text(text, font, draw, max_w)
        for line in lines:
            assert measure(line, font, draw) <= max_w, f"Line too wide: {line!r}"

    def test_single_long_word_is_hard_broken(self, font, draw):
        text = "Supercalifragilisticexpialidocious"
        max_w = 80
        lines = wrap_text(text, font, draw, max_w)
        assert len(lines) > 1
        for line in lines:
            assert measure(line, font, draw) <= max_w

    def test_short_text_stays_on_one_line(self, font, draw):
        text = "Milk"
        lines = wrap_text(text, font, draw, 400)
        assert lines == ["Milk"]

    def test_empty_string(self, font, draw):
        lines = wrap_text("", font, draw, 200)
        assert lines == [""]

    def test_multiple_spaces(self, font, draw):
        text = "a b c d e f g h i j k l"
        max_w = 100
        lines = wrap_text(text, font, draw, max_w)
        for line in lines:
            assert measure(line, font, draw) <= max_w


class TestEllipsize:
    def test_short_text_unchanged(self, font, draw):
        assert ellipsize("Hi", font, draw, 400) == "Hi"

    def test_long_text_fits_after_ellipsis(self, font, draw):
        text = "This is a very long piece of text that should be truncated"
        max_w = 150
        result = ellipsize(text, font, draw, max_w)
        assert measure(result, font, draw) <= max_w
        assert result.endswith("…") or result.endswith("...")

    def test_result_is_shorter(self, font, draw):
        text = "Something rather lengthy indeed"
        max_w = 100
        result = ellipsize(text, font, draw, max_w)
        assert len(result) < len(text)
