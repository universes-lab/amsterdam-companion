from abc import ABC, abstractmethod

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
    def analyze(self, prompt: str) -> str:
        """
        Анализирует данные и возвращает JSON-строку.
        
        Args:
            prompt: Системный промпт + данные для анализа
            
        Returns:
            JSON-строка с результатами анализа
        """
        pass
