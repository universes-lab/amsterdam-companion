import piper
import asyncio
import os
from pathlib import Path
from config.settings import TTS_MODEL_PATH

class TTSEngine:
    def __init__(self):
        self._voices = {}  # Cache of {lang: piper.Voice}
    
    def _get_voice_filename(self, lang: str) -> str:
        # Map languages to downloaded voice filenames
        mapping = {
            "nl": "nl_BE-nathalie-medium.onnx",
            "ru": "ru_RU-irina-medium.onnx",
            "en": "en_US-amy-medium.onnx"
        }
        return mapping.get(lang, "nl_BE-nathalie-medium.onnx")
    
    async def _ensure_loaded(self, lang: str):
        if lang not in self._voices:
            # Lazy-preload при первом использовании
            voice_file = self._get_voice_filename(lang)
            voice_path = TTS_MODEL_PATH / voice_file
            
            # Load the voice and cache it
            voice = await asyncio.to_thread(piper.Voice.load, str(voice_path))
            self._voices[lang] = voice
    
    async def speak(self, text: str, lang: str = "nl") -> bytes:
        await self._ensure_loaded(lang)
        return await asyncio.to_thread(self._sync_speak, text, lang)
    
    def _sync_speak(self, text, lang):
        import io
        output = io.BytesIO()
        voice = self._voices[lang]
        voice.session.synthesize(text, output)
        return output.getvalue()

    def is_loaded(self, lang="nl"):
        return lang in self._voices

# Lazy singleton helper
_tts_engine = None

def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine

async def speak(text: str, lang: str = "nl") -> bytes:
    """TTS Interface for Piper."""
    engine = get_tts_engine()
    return await engine.speak(text, lang)
