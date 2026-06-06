import shutil
import os
import subprocess
from pathlib import Path

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ WARNING: ffmpeg not found. Voice preprocessing will fail.")
        return False
    return True

def validate_environment():
    assert shutil.which("ffmpeg") or check_ffmpeg(), "ffmpeg not found in PATH"
    assert os.getenv("TELEGRAM_TOKEN"), "TELEGRAM_TOKEN not set in .env"
    
    # Check for models
    models_dir = Path("./models")
    assert (models_dir / "stt").exists(), "STT models directory not found"
    assert (models_dir / "tts").exists(), "TTS models directory not found"
    assert (models_dir / "translation" / "nllb-600m-int8" / "model.bin").exists(), "NLLB model not found"
    
    print("[OK] Startup validation passed.")
