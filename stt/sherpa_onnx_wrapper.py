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
        # Path assumes models are in models/stt/whisper-tiny.en
        model_path = Path("models/stt/whisper-tiny.en")
        # Ensure path exists, if not, logic will fail gracefully or need setup
        self.recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(model_path / "encoder.onnx"),
            decoder=str(model_path / "decoder.onnx"),
            joiner=str(model_path / "joiner.onnx"),
            tokens=str(model_path / "tokens.txt"),
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
