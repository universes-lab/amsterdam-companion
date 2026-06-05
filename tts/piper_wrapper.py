import piper
import asyncio
import os

class TTSEngine:
    def __init__(self):
        self._voice = None
        self._session = None
    
    async def _ensure_loaded(self):
        if self._session is None:
            # Lazy-preload при первом использовании
            # Path assumes models are in models/tts/nl_NL-mls-medium
            self._voice = piper.Voice.load("models/tts/nl_NL-mls-medium")
            self._session = self._voice.session
    
    async def speak(self, text: str, lang: str = "nl") -> bytes:
        await self._ensure_loaded()
        return await asyncio.to_thread(self._sync_speak, text)
    
    def _sync_speak(self, text):
        # Piper returns WAV bytes
        import io
        output = io.BytesIO()
        self._session.synthesize(text, output)
        return output.getvalue()

# Interface wrapper
tts_engine = TTSEngine()

async def speak(text: str, lang: str = "nl") -> bytes:
    """TTS Interface for Piper."""
    return await tts_engine.speak(text, lang)
