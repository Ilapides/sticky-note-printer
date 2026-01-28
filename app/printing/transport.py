"""Printing transport: PNG → BMP conversion and IPP send."""

import subprocess

from app.config import config


def png_to_printer_bmp(png_path: str, bmp_path: str) -> None:
    """Convert a PNG to a printer-compatible BMP3 using ImageMagick."""
    cmd = [
        "convert",
        png_path,
        "-resize",
        "576x",
        "-monochrome",
        "-depth",
        "1",
        "-flip",
        f"BMP3:{bmp_path}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ImageMagick conversion failed: {result.stderr}")


def send_bmp_to_printer(bmp_path: str) -> None:
    """Send a BMP file to the printer via IPP."""
    uri = f"ipp://{config.PRINTER_IP}:{config.PRINTER_PORT}/ipp/print"
    cmd = [
        "ipptool",
        "-tv",
        "-f",
        bmp_path,
        uri,
        "-d",
        "fileType=image/reverse-encoding-bmp",
        "print-job.test",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"IPP print failed: {result.stderr}")


def send_png_to_printer(png_path: str) -> None:
    """Convenience: convert PNG to BMP then send to printer."""
    import os

    bmp_path = os.path.splitext(png_path)[0] + ".bmp"
    png_to_printer_bmp(png_path, bmp_path)
    send_bmp_to_printer(bmp_path)
