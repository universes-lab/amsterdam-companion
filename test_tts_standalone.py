# test_tts_standalone.py
import asyncio
import os
import sys

# Ensure project root is in sys.path to handle imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts.piper_wrapper import TTSEngine

async def test():
    tts = TTSEngine()
    print("TTS engine created")
    
    # Простой тест
    text = "Hallo, dit is een test."
    print(f"Translating (TTS): {text}")
    
    try:
        audio = await tts.speak(text, lang="nl")
        print(f"Got {len(audio)} bytes")
        
        # Сохрани в файл для проверки
        with open("test_output.wav", "wb") as f:
            f.write(audio)
        print("Saved to test_output.wav")
    except Exception as e:
        print(f"ERROR: TTS failed with: {e}")

if __name__ == "__main__":
    # Ensure FFMPEG is visible if needed (though tts might not need it, good practice)
    os.environ["FFMPEG_PATH"] = r"E:\pinokio\api\facefusion-pinokio.git\.env\Library\bin\ffmpeg.exe"
    asyncio.run(test())
