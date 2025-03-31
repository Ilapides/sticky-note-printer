from flask import request, jsonify
from app import app
from app.image import make_image_from_list
from app.printer import render_printable_bmp, print_image
from app.config import config
import os

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