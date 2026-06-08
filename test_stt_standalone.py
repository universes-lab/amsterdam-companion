# test_stt_standalone.py
import asyncio
import os
import sys
import wave

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt.sherpa_onnx_wrapper import STTEngine

async def test():
    stt = STTEngine()
    print("STT engine created")
    
    # Path to test wav
    wav_path = r"models/stt/sherpa-onnx-whisper-tiny/test_wavs/0.wav"
    print(f"Reading test wav: {wav_path}")
    
    with wave.open(wav_path, "rb") as f:
        # Read raw PCM bytes (assuming 16kHz mono 16bit)
        params = f.getparams()
        print(f"Wav params: {params}")
        pcm_bytes = f.readframes(f.getnframes())
        
    print(f"Got {len(pcm_bytes)} PCM bytes. Transcribing...")
    
    try:
        text = await stt.transcribe(pcm_bytes, lang="nl")
        print(f"Transcription result: '{text}'")
    except Exception as e:
        print(f"ERROR: STT failed with: {e}")

if __name__ == "__main__":
    asyncio.run(test())
