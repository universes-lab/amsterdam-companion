import psutil
import asyncio
from datetime import datetime
from stt.sherpa_onnx_wrapper import STTEngine
from translation.nllb_wrapper import TranslationEngine
from tts.piper_wrapper import TTSEngine

class HealthChecker:
    def __init__(self):
        self.start_time = datetime.now()
        self.model_status = {
            "stt": False,
            "translation": False,
            "tts": False
        }
    
    async def check_models(self):
        # проверка загрузки моделей через их движки
        self.model_status["stt"] = STTEngine._instance is not None
        self.model_status["translation"] = TranslationEngine._instance is not None
        self.model_status["tts"] = TTSEngine._instance is not None
        return self.model_status
    
    async def get_ram_usage(self):
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    async def get_status(self):
        models = await self.check_models()
        return {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "ram_mb": await self.get_ram_usage(),
            "models": models,
            "status": "healthy" if all(models.values()) else "degraded"
        }

healthcheck = HealthChecker()
