import os
import sys

# Ensure the project root is on sys.path so `app` is importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set required env vars if not already present (tests don't need a real printer).
os.environ.setdefault("PRINTER_IP", "127.0.0.1")
os.environ.setdefault("PRINTER_PORT", "631")
os.environ.setdefault("TEMP_IMAGE_DIR", "/tmp/sticky-test")
