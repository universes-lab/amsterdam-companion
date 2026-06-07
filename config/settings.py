from pydantic_settings import BaseSettings
from pathlib import Path

# Absolute path to the project root, independent of CWD
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Absolute paths to all model directories
STT_MODEL_PATH = PROJECT_ROOT / "models" / "stt" / "sherpa-onnx-whisper-tiny"
TTS_MODEL_PATH = PROJECT_ROOT / "models" / "tts"
TRANSLATION_MODEL_PATH = PROJECT_ROOT / "models" / "translation" / "nllb-600m-int8"
LOGS_PATH = PROJECT_ROOT / "logs"
TEMP_PATH = PROJECT_ROOT / "temp_audio"

class Settings(BaseSettings):
    telegram_token: str
    models_dir: str = str(PROJECT_ROOT / "models")
    temp_dir: str = str(TEMP_PATH)
    ffmpeg_path: str = "ffmpeg"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
