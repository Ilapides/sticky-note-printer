"""Tests for grocery_note rendering."""

import os
import tempfile

import pytest
from PIL import Image

from app.rendering.grocery_note import render_grocery_note


SAMPLE_PAYLOAD = {
    "title": "Weekly Groceries",
    "areas": [
        {
            "name": "Produce",
            "items": [
                {"qty": "2", "unit": "lb", "name": "onions", "note": "yellow", "checked": False},
                {"qty": "1", "unit": "bunch", "name": "cilantro", "checked": False},
                {"qty": "3", "unit": "", "name": "avocados", "checked": True},
            ],
        },
        {
            "name": "Dairy",
            "items": [
                {"qty": "1", "unit": "gal", "name": "milk", "note": "whole", "checked": False},
            ],
        },
    ],
    "options": {
        "width_px": 576,
        "margin_px": 16,
        "line_gap_px": 6,
        "include_checked": False,
    },
}


def test_image_width_matches_requested():
    img = render_grocery_note(SAMPLE_PAYLOAD)
    assert img.width == 576


def test_image_is_monochrome():
    img = render_grocery_note(SAMPLE_PAYLOAD)
    assert img.mode == "1"


def test_image_has_content():
    img = render_grocery_note(SAMPLE_PAYLOAD)
    # At least some black pixels should exist (content was drawn).
    pixels = list(img.tobytes())
    assert 0 in pixels


def test_checked_items_excluded_by_default():
    """With include_checked=False the checked avocado should not appear."""
    img_without = render_grocery_note(SAMPLE_PAYLOAD)

    payload_with = {**SAMPLE_PAYLOAD, "options": {**SAMPLE_PAYLOAD["options"], "include_checked": True}}
    img_with = render_grocery_note(payload_with)

    # Including checked items should produce a taller image.
    assert img_with.height > img_without.height


def test_width_384():
    payload = {**SAMPLE_PAYLOAD, "options": {**SAMPLE_PAYLOAD["options"], "width_px": 384}}
    img = render_grocery_note(payload)
    assert img.width == 384


MARGIN_PAYLOAD = {
    "title": "Thanksgiving Grocery Run With Extra Long Title That Should Wrap",
    "areas": [
        {
            "name": "Produce & Fresh Vegetables Section",
            "items": [
                {
                    "qty": "2",
                    "unit": "lb",
                    "name": "extraordinarily large butternut squash",
                    "note": "organic from the farmers market if possible",
                    "checked": False,
                },
                {
                    "qty": "12",
                    "unit": "oz",
                    "name": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                    "note": "single-word-that-is-extremely-long-and-must-hard-break",
                    "checked": False,
                },
                {
                    "qty": "100",
                    "unit": "grams",
                    "name": "cilantro bunch with roots attached",
                    "note": "very fresh only",
                    "checked": False,
                },
            ],
        },
        {
            "name": "Dairy",
            "items": [
                {
                    "qty": "1",
                    "unit": "gal",
                    "name": "whole milk",
                    "note": "not ultra-pasteurized please get the good kind",
                    "checked": False,
                },
            ],
        },
    ],
}


def _assert_no_ink_in_right_margin(width_px, margin_px):
    """Render with the given dimensions and assert no ink in the right margin strip."""
    payload = {
        **MARGIN_PAYLOAD,
        "options": {
            "width_px": width_px,
            "margin_px": margin_px,
            "line_gap_px": 6,
            "include_checked": True,
        },
    }
    img = render_grocery_note(payload)
    assert img.width == width_px

    # Convert to grayscale and threshold: ink = pixel < 128
    gray = img.convert("L")
    right_limit = width_px - margin_px
    strip = gray.crop((right_limit, 0, width_px, img.height))

    # Invert so ink becomes white (255) and background becomes black (0),
    # then getbbox() returns None if there are no non-zero (i.e. no ink) pixels.
    from PIL import ImageOps

    inverted = ImageOps.invert(strip)
    # After invert: former-ink pixels (dark, <128) become >128 (bright).
    # Threshold at 128 to isolate them.
    ink_mask = inverted.point(lambda p: 255 if p > 127 else 0)
    bbox = ink_mask.getbbox()
    assert bbox is None, (
        f"Ink detected in the right margin strip (x={right_limit}..{width_px}) "
        f"at bounding box {bbox}"
    )


def test_no_ink_in_right_margin_384():
    _assert_no_ink_in_right_margin(384, 16)


def test_no_ink_in_right_margin_576():
    _assert_no_ink_in_right_margin(576, 16)


def test_footer_increases_height():
    """A payload with a footer string should produce a taller image."""
    img_no_footer = render_grocery_note(SAMPLE_PAYLOAD)
    payload_with_footer = {**SAMPLE_PAYLOAD, "footer": "Food Ops — List #3"}
    img_with_footer = render_grocery_note(payload_with_footer)
    assert img_with_footer.height > img_no_footer.height


def test_no_footer_still_has_timestamp():
    """Even without a footer field, the timestamp line is rendered (image has content)."""
    img = render_grocery_note(SAMPLE_PAYLOAD)
    assert img.height > 0
    pixels = list(img.tobytes())
    assert 0 in pixels


def test_save_artifact(tmp_path):
    """Save a rendered image for manual inspection (optional)."""
    img = render_grocery_note(SAMPLE_PAYLOAD)
    out = tmp_path / "grocery_test.png"
    img.save(str(out))
    assert out.exists()
