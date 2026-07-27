from typing import Optional
from pathlib import Path
from llama_cpp import Llama
from companion.llm.base import SupervisorLLM
from companion.config.settings import MODEL_PATH, N_GPU_LAYERS, N_CTX, N_BATCH

class SupervisorQwen(SupervisorLLM):
    """Реализация SupervisorLLM через Qwen GGUF."""
    
    def __init__(self):
        self.llm = None
        self._loaded = False
    
    def load(self) -> None:
        if not self._loaded:
            self.llm = Llama(
                model_path=str(MODEL_PATH),
                n_gpu_layers=N_GPU_LAYERS,
                n_ctx=N_CTX,
                n_batch=N_BATCH,
                verbose=False
            )
            self._loaded = True
    
    def unload(self) -> None:
        if self._loaded:
            self.llm = None
            self._loaded = False
    
    def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._loaded:
            raise RuntimeError("Model not loaded")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
            top_p=0.9,
            stop=["\n\n\n", "```"]
        )
        
        return response['choices'][0]['message']['content']
