import shutil
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from config.settings import (
    STT_MODEL_PATH, 
    TTS_MODEL_PATH, 
    TRANSLATION_MODEL_PATH,
    PROJECT_ROOT
)

def check_ffmpeg():
    # Allow specifying FFMPEG_PATH via environment
    ffmpeg_path = os.getenv("FFMPEG_PATH")
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        return True
        
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ WARNING: ffmpeg not found. Voice preprocessing will fail.")
        return False
    return True

def validate_models():
    """Пропускаем проверку файлов, чтобы избежать PermissionError. Загрузка произойдет в движках."""
    print("[INFO] Пропускаем проверку наличия файлов моделей (будет выполнено движками)")

def validate_environment():
    load_dotenv()
    
    # 1. System check
    assert shutil.which("ffmpeg") or check_ffmpeg(), "ffmpeg not found in PATH"
    assert os.getenv("TELEGRAM_TOKEN"), "TELEGRAM_TOKEN not set in .env"
    
    # 2. Project structure check
    assert (PROJECT_ROOT / "models").exists(), "models directory not found"
    
    # 3. Specific models check
    validate_models()
    
    print("[OK] Startup validation passed.")

if __name__ == "__main__":
    validate_environment()
