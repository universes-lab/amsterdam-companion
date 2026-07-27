import logging
from pathlib import Path
from typing import Optional, Dict, Any

from companion.llm.base import SupervisorLLM

logger = logging.getLogger(__name__)

class CompanionEngine:
    """Situation Companion: описывает окружающую обстановку."""
    
    def __init__(self, llm: SupervisorLLM):
        self.llm = llm
        self.system_prompt = self._load_system_prompt()
        self._loaded = False

    def _load_system_prompt(self) -> str:
        """Загружает системный промпт."""
        prompt_path = Path("companion/prompts/system_prompt.yaml")
        if not prompt_path.exists():
            return "You are a Situation Companion. Describe the surroundings and support the user."
        
        # Минимальная загрузка YAML
        import yaml
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_config = yaml.safe_load(f)
        return str(prompt_config)

    def load(self) -> None:
        logger.info("Loading CompanionEngine...")
        self.llm.load()
        self._loaded = True
        logger.info("CompanionEngine ready")
    
    def unload(self) -> None:
        if self._loaded:
            self.llm.unload()
            self._loaded = False
            logger.info("CompanionEngine unloaded")
    
    def chat(self, user_input: str) -> str:
        """Основной метод общения."""
        if not self._loaded:
            raise RuntimeError("Engine not loaded. Call load() first.")
        
        return self.llm.analyze(user_input, system_prompt=self.system_prompt)
