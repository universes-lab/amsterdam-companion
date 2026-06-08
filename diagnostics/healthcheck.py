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
    
    async def check_models(self):
        # проверка инициализации через глобальные переменные синглтонов
        status = {
            "stt": "unloaded",
            "translation": "unloaded",
            "tts": "unloaded"
        }
        
        if stt_singleton is not None and stt_singleton.is_loaded():
            status["stt"] = "loaded"
        
        if translation_singleton is not None and translation_singleton.is_loaded():
            status["translation"] = "loaded"
            
        if tts_singleton is not None and tts_singleton.is_loaded("nl"):
            status["tts"] = "loaded"
            
        return status
    
    async def get_ram_usage(self):
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    async def get_status(self):
        models = await self.check_models()
        # Статус healthy, если все модели либо загружены, либо ещё не вызывались (unloaded)
        is_healthy = True
        return {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "ram_mb": await self.get_ram_usage(),
            "models": models,
            "status": "healthy" if is_healthy else "degraded"
        }

healthcheck = HealthChecker()
