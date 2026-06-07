import sherpa_onnx
import asyncio
from pathlib import Path

class STTEngine:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        # Path assumes models are in models/stt/sherpa-onnx-whisper-tiny
        model_path = Path("models/stt/sherpa-onnx-whisper-tiny")
        self.recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=str(model_path / "tiny-encoder.int8.onnx"),
            decoder=str(model_path / "tiny-decoder.int8.onnx"),
            tokens=str(model_path / "tiny-tokens.txt"),
            language="nl",
            task="transcribe",
            num_threads=4,
        )
    
    async def transcribe(self, audio_bytes: bytes, lang: str = "nl") -> str:
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
        return stream.result.text

# Interface wrapper
stt_engine = STTEngine()

async def transcribe(audio_bytes: bytes, lang: str = "nl") -> str:
    """STT Interface for Sherpa-ONNX."""
    return await stt_engine.transcribe(audio_bytes, lang)
