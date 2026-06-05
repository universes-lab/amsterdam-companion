import asyncio
from audio.preprocessor import preprocess
from stt.sherpa_onnx_wrapper import transcribe
from translation.nllb_wrapper import translate
from tts.piper_wrapper import speak

async def process_live_voice(audio_bytes: bytes, user_id: str) -> bytes:
    print(f"[Pipeline] Processing live voice for {user_id}")
    
    # Wrapping in timeout as per safety requirements
    try:
        return await asyncio.wait_for(
            run_pipeline(audio_bytes, user_id),
            timeout=60
        )
    except asyncio.TimeoutError:
        print(f"[Pipeline] Task timed out for {user_id}")
        return b""

async def run_pipeline(audio_bytes: bytes, user_id: str) -> bytes:
    # Preprocess audio
    preprocessed_audio = await preprocess(audio_bytes)
    
    # Transcribe
    text = await transcribe(preprocessed_audio, lang="nl")
    
    # Translate
    translated_text = await translate(text, src="nl", dst="ru")
    
    # Speak
    audio_response = await speak(translated_text, lang="ru")
    
    print(f"[Pipeline] Finished for {user_id}.")
    return audio_response
