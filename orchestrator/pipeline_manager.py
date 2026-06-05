import asyncio
from audio.preprocessor import preprocess
from stt.sherpa_onnx_wrapper import transcribe
from translation.nllb_wrapper import translate
from tts.piper_wrapper import speak

async def process_live_voice(user_id: str):
    print(f"[Pipeline] Processing live voice for {user_id}")
    
    # Example flow
    audio_data = b"raw_audio_from_telegram"
    
    # Wrappping in timeout as per safety requirements
    try:
        await asyncio.wait_for(
            run_pipeline(audio_data, user_id),
            timeout=60
        )
    except asyncio.TimeoutError:
        print(f"[Pipeline] Task timed out for {user_id}")

async def run_pipeline(audio_bytes: bytes, user_id: str):
    # This is a mock pipeline
    processed_audio = b"processed_audio"
    text = await transcribe(processed_audio, "nl")
    translated_text = await translate(text, "nl", "en")
    audio_response = await speak(translated_text, "en")
    
    print(f"[Pipeline] Finished for {user_id}. Mock result generated.")
