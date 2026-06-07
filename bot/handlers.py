from aiogram import types, Router
from orchestrator.task_registry import TaskRegistry
from orchestrator.pipeline_manager import process_message
from diagnostics.healthcheck import healthcheck

router = Router()
task_registry = TaskRegistry()

@router.message(lambda msg: msg.text == "/status")
async def cmd_status(message: types.Message):
    status = await healthcheck.get_status()
    text = f"""
📊 **System Status**
Uptime: {status['uptime_seconds']:.0f}s
RAM: {status['ram_mb']:.0f} MB
Models: STT={'✅' if status['models']['stt'] else '❌'} | TR={'✅' if status['models']['translation'] else '❌'} | TTS={'✅' if status['models']['tts'] else '❌'}
Status: {status['status']}
"""
    await message.answer(text)

@router.message(lambda msg: msg.text and msg.text.startswith("/"))
async def cmd_handler(message: types.Message):
    user_id = str(message.from_user.id)
    # This now handles both text and potential voice if integrated
    response, _, _ = await process_message(user_id, message.text)
    await message.answer(response["text"], reply_markup=response.get("reply_markup"))

@router.message(lambda msg: msg.voice)
async def voice_handler(message: types.Message):
    user_id = str(message.from_user.id)
    file = await message.bot.get_file(message.voice.file_id)
    voice_bytes = await message.bot.download_file(file.file_path)
    
    # Process voice
    response, _, _ = await process_message(user_id, "/live", voice_bytes=voice_bytes.getvalue())
    
    if response.get("voice"):
        await message.answer_voice(types.BufferedInputFile(response["voice"], filename="response.ogg"))
    else:
        await message.answer(response["text"])

@router.message(lambda msg: msg.text)
async def text_handler(message: types.Message):
    user_id = str(message.from_user.id)
    response, _, _ = await process_message(user_id, message.text)
    await message.answer(response["text"], reply_markup=response.get("reply_markup"))
