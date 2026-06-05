import asyncio
from aiogram import types, Router
from orchestrator.task_registry import TaskRegistry
from orchestrator.pipeline_manager import process_live_voice

router = Router()
task_registry = TaskRegistry()

@router.message(lambda msg: msg.text == "/live")
async def cmd_live(message: types.Message):
    user_id = str(message.from_user.id)
    task = asyncio.create_task(process_live_voice(user_id))
    task_registry.register(user_id, task)
    await message.answer("Live mode started.")

@router.message(lambda msg: msg.text == "/learn")
async def cmd_learn(message: types.Message):
    await message.answer("Learn mode not implemented yet.")

@router.message(lambda msg: msg.text == "/status")
async def cmd_status(message: types.Message):
    await message.answer("RAM: 0 Mb, Models: Not loaded")
