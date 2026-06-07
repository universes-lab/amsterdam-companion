import psutil
import asyncio
from datetime import datetime
import sys

# Import engines without forcing load
from stt.sherpa_onnx_wrapper import _stt_engine as stt_singleton
from translation.nllb_wrapper import _translation_engine as translation_singleton
from tts.piper_wrapper import _tts_engine as tts_singleton

class HealthChecker:
    def __init__(self):
        self.start_time = datetime.now()
        self.model_status = {
            "stt": False,
            "translation": False,
            "tts": False
        }
    
    async def check_models(self):
        # проверка инициализации через глобальные переменные синглтонов
        try:
            self.model_status["stt"] = stt_singleton is not None and stt_singleton.is_loaded()
            self.model_status["translation"] = translation_singleton is not None and translation_singleton.is_loaded()
            self.model_status["tts"] = tts_singleton is not None and tts_singleton.is_loaded("nl")
        except Exception as e:
            print(f"[HealthCheck] Error checking models: {e}")
            
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
