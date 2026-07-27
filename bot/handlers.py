from aiogram import types, Router
from aiogram.filters import Command
from orchestrator.task_registry import TaskRegistry
from orchestrator.pipeline_manager import process_message, _log_supervisor_event
from diagnostics.healthcheck import healthcheck
import subprocess
import json
import asyncio
from pathlib import Path
from datetime import datetime

router = Router()
task_registry = TaskRegistry()

SUPERVISOR_MEMORY_FILE = Path("companion/memory.json")
SUPERVISOR_REPORTS_DIR = Path("companion/reports")
SUPERVISOR_RUN_SCRIPT = Path("companion/run.py")
SUPERVISOR_ENGINE_SCRIPT = Path("companion/tests/test_engine.py")

def get_supervisor_status() -> dict:
    """Возвращает статус Companion (читает memory.json)."""
    if not SUPERVISOR_MEMORY_FILE.exists():
        return {"status": "NOT_INITIALIZED", "last_report": None, "errors": 0}
    
    try:
        with open(SUPERVISOR_MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        last_report = None
        if SUPERVISOR_REPORTS_DIR.exists():
            reports = list(SUPERVISOR_REPORTS_DIR.glob("*.md"))
            if reports:
                last_report = max(reports, key=lambda p: p.stat().st_mtime).name
        
        return {
            "status": "READY",
            "last_analysis": memory.get("period", {}).get("to"),
            "last_report": last_report,
            "errors": 0
        }
    except Exception as e:
        return {"status": "ERROR", "last_report": None, "errors": 1, "error": str(e)}

def get_stats_summary() -> str:
    """Формирует краткую сводку из memory.json."""
    if not SUPERVISOR_MEMORY_FILE.exists():
        return "📊 Статистика пока недоступна. Отправьте несколько запросов боту."
    
    try:
        with open(SUPERVISOR_MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        period = memory.get("period", {})
        total = memory.get("total_requests", 0)
        live = memory.get("live_mode_requests", 0)
        learn = memory.get("learn_mode_requests", 0)
        
        lines = [
            f"📊 Статистика за период",
            f"📅 {period.get('from', 'N/A')[:10]} — {period.get('to', 'N/A')[:10]}",
            "",
            f"**Всего запросов:** {total}",
            f"- LIVE Mode: {live} ({round(live/max(total,1)*100)}%)",
            f"- LEARNING Mode: {learn} ({round(learn/max(total,1)*100)}%)",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Ошибка чтения статистики: {e}"

@router.message(Command("companion_report"))
async def cmd_supervisor_report(message: types.Message):
    """Генерирует еженедельный отчёт."""
    status_msg = await message.answer("🔄 Генерация отчёта... Пожалуйста, подождите.")
    try:
        process = await asyncio.create_subprocess_exec(
            "python", str(SUPERVISOR_ENGINE_SCRIPT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        if process.returncode != 0:
            await status_msg.edit_text(f"❌ Ошибка генерации отчёта:\n```\n{stderr.decode()[:500]}\n```")
            return
        
        reports = list(SUPERVISOR_REPORTS_DIR.glob("*.md"))
        if not reports:
            await status_msg.edit_text("❌ Отчёт не найден.")
            return
        
        latest_report = max(reports, key=lambda p: p.stat().st_mtime)
        with open(latest_report, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        if len(report_content) > 4000:
            report_content = report_content[:3500] + "\n\n... (отчёт обрезан)"
        await status_msg.edit_text(report_content)
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {e}")

@router.message(Command("companion_stats"))
async def cmd_supervisor_stats(message: types.Message):
    stats = get_stats_summary()
    await message.answer(stats)

@router.message(Command("companion_analyze"))
async def cmd_supervisor_analyze(message: types.Message):
    status_msg = await message.answer("🔄 Обновление статистики...")
    try:
        process = await asyncio.create_subprocess_exec(
            "python", str(SUPERVISOR_RUN_SCRIPT), "--update-memory",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(process.communicate(), timeout=60)
        await status_msg.edit_text("✅ Статистика обновлена!")
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {e}")

@router.message(lambda msg: msg.text == "/status")
async def cmd_status(message: types.Message):
    status = await healthcheck.get_status()
    sup_status = get_supervisor_status()
    text = f"""
📊 **System Status**
Uptime: {status['uptime_seconds']:.0f}s
RAM: {status['ram_mb']:.0f} MB
Status: {status['status']}

🤖 **Companion Status**
- Статус: {sup_status.get('status', 'UNKNOWN')}
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
    print(f"[HANDLER] Voice received: {len(voice_bytes.getvalue())} bytes")
    response, _, _ = await process_message(user_id, "/live", voice_bytes=voice_bytes.getvalue())
    print(f"[HANDLER] Response voice size: {len(response.get('voice')) if response.get('voice') else 0} bytes")
    
    if response.get("voice"):
        await message.answer_voice(types.BufferedInputFile(response["voice"], filename="response.ogg"))
        print("[HANDLER] Voice sent successfully")
    else:
        print("[HANDLER] No voice to send - pipeline returned empty")
        await message.answer(response["text"])

@router.message(lambda msg: msg.text)
async def text_handler(message: types.Message):
    user_id = str(message.from_user.id)
    response, _, _ = await process_message(user_id, message.text)
    await message.answer(response["text"], reply_markup=response.get("reply_markup"))
