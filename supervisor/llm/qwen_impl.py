from supervisor.llm.base import SupervisorLLM

class SupervisorQwen(SupervisorLLM):
    """Реализация SupervisorLLM через Qwen GGUF."""
    
    def load(self) -> None:
        raise NotImplementedError("Реализация будет в Phase 7A.5")
    
    def unload(self) -> None:
        raise NotImplementedError("Реализация будет в Phase 7A.5")
    
    def analyze(self, prompt: str) -> str:
        raise NotImplementedError("Реализация будет в Phase 7A.5")
