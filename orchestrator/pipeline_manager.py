import asyncio
import time
from audio.preprocessor import preprocess
from stt.sherpa_onnx_wrapper import transcribe
from translation.nllb_wrapper import translate
from tts.piper_wrapper import speak
from router.deterministic_router import route
from orchestrator.response_builder import build_response
from session.session_manager import SessionManager

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

async def process_message(user_id: str, message_text: str, voice_bytes: bytes = None):
    session = SessionManager(user_id)
    
    # Measure router latency
    start_router = time.time()
    mode, params = route(message_text, session.get_mode())
    router_latency = (time.time() - start_router) * 1000
    
    if voice_bytes:
        # голосовой перевод (LIVE)
        preprocessed = await preprocess(voice_bytes)
        text = await transcribe(preprocessed)
        translated = await translate(text, src="nl", dst="ru")
        tts_audio = await speak(translated)
        
        # Measure response builder latency
        start_rb = time.time()
        response = build_response("live", translated, tts_audio)
        rb_latency = (time.time() - start_rb) * 1000
    else:
        # текстовый запрос (LEARN)
        if mode == "learn":
            # простая эмуляция ответа на текстовый запрос
            explanation = await translate(message_text, src="ru", dst="nl")
            translated = message_text  # без перевода
            
            # Measure response builder latency
            start_rb = time.time()
            response = build_response("learn", translated, None, explanation)
            rb_latency = (time.time() - start_rb) * 1000
        else:
            response = {"text": f"Unsupported mode: {mode}"}
            rb_latency = 0
            
    print(f"[Metrics] Router latency: {router_latency:.2f}ms, Response Builder latency: {rb_latency:.2f}ms")
    return response, router_latency, rb_latency
