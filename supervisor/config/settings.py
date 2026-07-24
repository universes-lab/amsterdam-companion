# settings.py
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / "supervisor" / "models"

MODEL_PATH = MODELS_DIR / "Bonsai-27B-Q1_0.gguf"
N_GPU_LAYERS = -1
N_CTX = 2048
N_BATCH = 512
