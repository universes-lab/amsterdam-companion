# test_pipeline_standalone.py
import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt.sherpa_onnx_wrapper import STTEngine
from translation.nllb_wrapper import TranslationEngine
from tts.piper_wrapper import TTSEngine

async def test():
    print("Initializing STT...")
    stt = STTEngine()
    
    print("Initializing Translation...")
    tr = TranslationEngine()
    
    print("Initializing TTS...")
    tts = TTSEngine()
    
    print("All engines initialized.")
    
    # 1. STT
    wav_path = r"models/stt/sherpa-onnx-whisper-tiny/test_wavs/0.wav"
    print(f"Reading test wav: {wav_path}")
    import wave
    with wave.open(wav_path, "rb") as f:
        pcm_bytes = f.readframes(f.getnframes())
        
    print("Step 1: Transcribing...")
    text = await stt.transcribe(pcm_bytes, lang="nl")
    print(f"STT result: '{text}'")
    
    # 2. Translate
    print("Step 2: Translating...")
    translated = await tr.translate(text, src="nl", dst="ru")
    print(f"Translation result: '{translated}'")
    
    # 3. TTS
    print("Step 3: Speaking...")
    audio = await tts.speak(translated, lang="ru")
    print(f"TTS generated {len(audio)} bytes")
    
    # Save to file
    with open("test_pipeline_output.wav", "wb") as f:
        f.write(audio)
    print("Saved to test_pipeline_output.wav")
    print("PIPELINE TEST SUCCESS!")

if __name__ == "__main__":
    os.environ["FFMPEG_PATH"] = r"E:\pinokio\api\facefusion-pinokio.git\.env\Library\bin\ffmpeg.exe"
    # Prevent OpenMP conflict crashes on Windows if that is the issue
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    os.environ["OMP_NUM_THREADS"] = "1"
    asyncio.run(test())
