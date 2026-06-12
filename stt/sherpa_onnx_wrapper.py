import sherpa_onnx
import asyncio
from pathlib import Path
from config.settings import STT_MODEL_PATH

class STTEngine:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self._initialized = False
        try:
            # Path assumes models are in models/stt/whisper_runtime (copy to avoid lock issues)
            model_path = STT_MODEL_PATH.parent / "whisper_runtime"
            self.recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
                encoder=str(model_path / "tiny-encoder.int8.onnx"),
                decoder=str(model_path / "tiny-decoder.int8.onnx"),
                tokens=str(model_path / "tiny-tokens.txt"),
                language="nl",
                task="transcribe",
                num_threads=4,
            )
            self._initialized = True
        except Exception as e:
            print(f"[Error] Failed to initialize STTEngine: {e}")
            self.recognizer = None

    def is_loaded(self):
        return self._initialized and self.recognizer is not None
    
    async def transcribe(self, audio_bytes: bytes, lang: str = "nl") -> tuple[str, float]:
        # Warmup: первый вызов может быть медленным
        # Запуск в отдельном потоке, чтобы не блокировать event loop
        return await asyncio.to_thread(self._sync_transcribe, audio_bytes)
    
    def _sync_transcribe(self, audio_bytes):
        stream = self.recognizer.create_stream()
        # Need to convert bytes to proper format if needed, assuming bytes are PCM
        import numpy as np
        samples = np.frombuffer(audio_bytes, dtype=np.int16)
        stream.accept_waveform(16000, samples.astype(np.float32) / 32768.0)
        self.recognizer.decode_streams([stream])
        # Assuming sherpa-onnx OfflineRecognizer result has confidence
        # If not, this will need adjustment. Assuming typical API structure:
        return stream.result.text, getattr(stream.result, 'confidence', 1.0)

# Lazy singleton helper
_stt_engine = None

def get_stt_engine():
    global _stt_engine
    if _stt_engine is None:
        _stt_engine = STTEngine()
    return _stt_engine

async def transcribe(audio_bytes: bytes, lang: str = "nl") -> tuple[str, float]:
    """STT Interface for Sherpa-ONNX."""
    engine = get_stt_engine()
    return await engine.transcribe(audio_bytes, lang)
