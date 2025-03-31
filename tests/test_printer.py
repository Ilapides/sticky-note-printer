import os
from app.image import make_image_from_list
from app.printer import render_printable_bmp, print_image
from app.config import config

def test_full_print_flow():
    tasks = ["Test A", "Test B"]
    os.makedirs(config.TEMP_IMAGE_DIR, exist_ok=True)
    img_path = os.path.join(config.TEMP_IMAGE_DIR, "test.png")
    bmp_path = os.path.join(config.TEMP_IMAGE_DIR, "test.bmp")

    make_image_from_list(tasks, img_path)
    assert os.path.exists(img_path)

    assert render_printable_bmp(img_path, bmp_path)
    assert os.path.exists(bmp_path)

    result = print_image(bmp_path)
    assert isinstance(result, bool)