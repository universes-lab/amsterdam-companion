import shutil
import os
from pathlib import Path

def validate_environment():
    assert shutil.which("ffmpeg"), "ffmpeg not found in PATH"
    assert os.getenv("TELEGRAM_TOKEN"), "TELEGRAM_TOKEN not set in .env"
    
    # Check for models
    models_dir = Path("./models")
    assert (models_dir / "stt").exists(), "STT models directory not found"
    assert (models_dir / "tts").exists(), "TTS models directory not found"
    assert (models_dir / "translation" / "nllb-600m-int8" / "model.bin").exists(), "NLLB model not found"
    
    print("[OK] Startup validation passed.")
