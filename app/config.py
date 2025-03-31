import os

def get_required_env(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {var_name}")
    return value

class Config:
    PRINTER_IP = get_required_env("PRINTER_IP")
    PRINTER_PORT = get_required_env("PRINTER_PORT")
    TEMP_IMAGE_DIR = get_required_env("TEMP_IMAGE_DIR")

config = Config()
