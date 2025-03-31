import subprocess
import os
from app.config import config

def render_printable_bmp(input_image_path, output_bmp_path):
    cmd = [
        "convert", input_image_path,
        "-resize", "576x",
        "-monochrome",
        "-depth", "1",
        "-flip",
        f"BMP3:{output_bmp_path}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ImageMagick conversion failed:", result.stderr)
        return False
    return True

def print_image(file_path):
    uri = f"ipp://{config.PRINTER_IP}:{config.PRINTER_PORT}/ipp/print"
    cmd = [
        "ipptool", "-tv", "-f", file_path,
        uri,
        "-d", "fileType=image/reverse-encoding-bmp",
        "print-job.test"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("IPP print failed:", result.stderr)
        return False
    return True