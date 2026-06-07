import psutil
import asyncio
from datetime import datetime
import sys

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
            from stt.sherpa_onnx_wrapper import _stt_engine
            from translation.nllb_wrapper import _translation_engine
            from tts.piper_wrapper import _tts_engine
            
            self.model_status["stt"] = _stt_engine is not None
            self.model_status["translation"] = _translation_engine is not None and _translation_engine._initialized
            self.model_status["tts"] = _tts_engine is not None
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
