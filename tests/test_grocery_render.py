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


def test_save_artifact(tmp_path):
    """Save a rendered image for manual inspection (optional)."""
    img = render_grocery_note(SAMPLE_PAYLOAD)
    out = tmp_path / "grocery_test.png"
    img.save(str(out))
    assert out.exists()
