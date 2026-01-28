import base64
import io
import os

from flask import request, jsonify

from app import app
from app.config import config
from app.image import make_image_from_list
from app.printer import render_printable_bmp, print_image
from app.rendering.grocery_note import render_grocery_note
from app.printing.transport import send_png_to_printer


# ---- Legacy endpoint (deprecated, kept for backwards compat) ----

@app.route("/print/tasks", methods=["POST"])
def print_tasks():
    data = request.json
    tasks = data.get("tasks", [])

    if not tasks:
        return jsonify({"error": "No tasks provided."}), 400

    os.makedirs(config.TEMP_IMAGE_DIR, exist_ok=True)
    temp_png = os.path.join(config.TEMP_IMAGE_DIR, "tasks.png")
    temp_bmp = os.path.join(config.TEMP_IMAGE_DIR, "printable_note.bmp")

    make_image_from_list(tasks, temp_png)
    render_success = render_printable_bmp(temp_png, temp_bmp)
    if not render_success:
        return jsonify({"error": "Failed to render BMP image."}), 500

    success = print_image(temp_bmp)
    return jsonify({"status": "printed" if success else "failed"})


# ---- New structured grocery endpoint ----

@app.route("/print/grocery", methods=["POST"])
def print_grocery():
    payload = request.json
    if not payload or not payload.get("areas"):
        return jsonify({"error": "Payload must include 'areas'."}), 400

    os.makedirs(config.TEMP_IMAGE_DIR, exist_ok=True)

    # Render image
    img = render_grocery_note(payload)

    # Save PNG
    temp_png = os.path.join(config.TEMP_IMAGE_DIR, "grocery.png")
    img.save(temp_png)

    # Base64 preview
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    preview_b64 = base64.b64encode(buf.getvalue()).decode()

    # Print
    sent = False
    try:
        send_png_to_printer(temp_png)
        sent = True
    except Exception as exc:
        app.logger.warning("Printing failed: %s", exc)

    bmp_path = os.path.splitext(temp_png)[0] + ".bmp"
    return jsonify({
        "preview_png_base64": preview_b64,
        "sent_to_printer": sent,
        "saved_paths": {
            "png": temp_png,
            "bmp": bmp_path if os.path.exists(bmp_path) else None,
        },
    })
