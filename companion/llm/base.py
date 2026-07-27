from abc import ABC, abstractmethod
from typing import Optional

class SupervisorLLM(ABC):
    """Абстрактный интерфейс для LLM Supervisor'а."""
    
    @abstractmethod
    def load(self) -> None:
        """Загружает модель в память."""
        pass
    
    @abstractmethod
    def unload(self) -> None:
        """Выгружает модель из памяти."""
        pass
    
    @abstractmethod
    def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Анализирует данные и возвращает JSON-строку.
        
        Args:
            prompt: Данные для анализа
            system_prompt: Системный промпт (опционально)
            
        Returns:
            JSON-строка с результатами анализа
        """
        pass
