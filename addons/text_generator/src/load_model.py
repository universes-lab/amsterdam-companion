from llama_cpp import Llama
from src.config import MODEL_PATH, DEFAULT_PARAMS
import os

_model = None

def get_model():
    global _model
    if _model is None:
        model_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), MODEL_PATH)
        print(f"Loading model from: {model_full_path}")
        _model = Llama(
            model_path=model_full_path,
            n_gpu_layers=DEFAULT_PARAMS["n_gpu_layers"],
            verbose=False
        )
    return _model
