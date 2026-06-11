import asyncio
import time
import json
from pathlib import Path
from datetime import datetime
from audio.preprocessor import preprocess
from stt.sherpa_onnx_wrapper import transcribe
from translation.nllb_wrapper import translate
from tts.piper_wrapper import speak
from router.deterministic_router import route
from orchestrator.response_builder import build_response
from session.session_manager import SessionManager
from config.settings import LOGS_PATH

SUPERVISOR_EVENTS_FILE = Path("supervisor/events.jsonl")

def _log_supervisor_event(event_type: str, **kwargs):
    """Записывает событие в events.jsonl для Supervisor."""
    try:
        SUPERVISOR_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": event_type,
            **kwargs
        }
        with open(SUPERVISOR_EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Failed to log supervisor event: {e}")

LATENCY_LOG = LOGS_PATH / "latency.log"
LATENCY_LOG.parent.mkdir(parents=True, exist_ok=True)

async def log_latency(step: str, duration_ms: float):
    with open(LATENCY_LOG, "a") as f:
        f.write(f"{time.time()},{step},{duration_ms:.2f}\n")

async def process_live_voice(audio_bytes: bytes, user_id: str) -> bytes:
    print(f"[Pipeline] Processing live voice for {user_id}")
    
    # Wrapping in timeout as per safety requirements
    try:
        start_time = time.perf_counter()
        result = await asyncio.wait_for(
            run_pipeline(audio_bytes, user_id),
            timeout=60
        )
        total_ms = (time.perf_counter() - start_time) * 1000
        await log_latency("total_pipeline", total_ms)
        return result
    except asyncio.TimeoutError:
        print(f"[Pipeline] Task timed out for {user_id}")
        return b""

async def run_pipeline(audio_bytes: bytes, user_id: str) -> bytes:
    # Preprocess audio
    start = time.perf_counter()
    preprocessed_audio = await preprocess(audio_bytes)
    await log_latency("preprocess", (time.perf_counter() - start) * 1000)
    
    # Transcribe
    start = time.perf_counter()
    text = await transcribe(preprocessed_audio, lang="nl")
    await log_latency("transcribe", (time.perf_counter() - start) * 1000)
    
    # Translate
    start = time.perf_counter()
    translated_text = await translate(text, src="nl", dst="ru")
    await log_latency("translate", (time.perf_counter() - start) * 1000)
    
    # Speak
    start = time.perf_counter()
    audio_response = await speak(translated_text, lang="ru")
    await log_latency("speak", (time.perf_counter() - start) * 1000)
    
    print(f"[Pipeline] Finished for {user_id}.")
    return audio_response

async def process_message(user_id: str, message_text: str, voice_bytes: bytes = None):
    session = SessionManager(user_id)
    
    # Measure router latency
    start_router = time.time()
    mode, params = route(message_text, session.get_mode())
    router_latency = (time.time() - start_router) * 1000
    
    # Update session mode if changed by command
    if message_text and message_text.startswith("/"):
        session.set_mode(mode)
    
    rb_latency = 0.0 # Initialize variable
    
    if voice_bytes:
        # голосовой перевод (LIVE)
        print(f"[PIPELINE] 1. Received {len(voice_bytes)} bytes")
        try:
            preprocessed = await preprocess(voice_bytes)
            print(f"[PIPELINE] 2. Preprocessed: {len(preprocessed)} bytes PCM")
        except Exception as e:
            print(f"[PIPELINE] Preprocess failed: {e}")
            raise
            
        try:
            text = await transcribe(preprocessed, lang="nl")
            print(f"[PIPELINE] 3. STT result: '{text}'")
        except Exception as e:
            print(f"[PIPELINE] STT failed: {e}")
            raise
            
        try:
            translated = await translate(text, src="nl", dst="ru")
            print(f"[PIPELINE] 4. Translation result: '{translated}'")
        except Exception as e:
            print(f"[PIPELINE] Translation failed: {e}")
            raise
            
        try:
            tts_audio = await speak(translated, lang="ru")
            print(f"[PIPELINE] 5. TTS generated {len(tts_audio)} bytes")
        except Exception as e:
            print(f"[PIPELINE] TTS failed: {e}")
            raise
        
        # Measure response builder latency
        start_rb = time.time()
        response = build_response("live", translated, tts_audio)
        rb_latency = (time.time() - start_rb) * 1000
        _log_supervisor_event("live_request", direction="ru→nl", latency_ms=rb_latency)
    else:
        # текстовый запрос
        if mode == "live":
            # Если это просто команда переключения в live
            if message_text == "/live":
                 response = build_response("live", "Режим Live активирован. Присылай голосовые сообщения!", None)
            else:
                 # Текстовый перевод в режиме live
                 translated = await translate(message_text, src="ru", dst="nl")
                 response = build_response("live", translated, None)
                 _log_supervisor_event("live_request", direction="ru→nl", latency_ms=0)
            rb_latency = 0
        elif mode == "learn":
            # Если это просто команда переключения в learn
            if message_text == "/learn":
                 response = build_response("learn", "Режим обучения активирован. Присылай фразу для перевода!", None)
            else:
                # простая эмуляция ответа на текстовый запрос
                explanation = await translate(message_text, src="ru", dst="nl")
                translated = message_text  # без перевода
                
                # Measure response builder latency
                start_rb = time.time()
                response = build_response("learn", translated, None, explanation)
                rb_latency = (time.time() - start_rb) * 1000
                _log_supervisor_event("learn_request", action="repeat", phrase_category="general")
        elif mode == "help":
            response = {"text": "Доступные команды:\n/live - Режим перевода\n/learn - Режим обучения\n/status - Статус системы\n/lang ru→nl - Перевод с RU на NL\n/help - Помощь\n/list - Список возможностей"}
            rb_latency = 0
        elif mode == "list":
            response = {"text": "Возможности:\n1. Голосовой перевод (Live)\n2. Изучение слов (Learn)\n3. Настройка языков"}
            rb_latency = 0
        else:
            response = {"text": f"Unsupported mode: {mode}"}
            rb_latency = 0
            
    print(f"[Metrics] Router latency: {router_latency:.2f}ms, Response Builder latency: {rb_latency:.2f}ms")
    return response, router_latency, rb_latency
