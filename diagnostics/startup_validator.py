import shutil
import os

def validate_environment():
    assert shutil.which("ffmpeg"), "ffmpeg not found in PATH"
    assert os.getenv("TELEGRAM_TOKEN"), "TELEGRAM_TOKEN not set in .env"
    print("[OK] Startup validation passed.")
