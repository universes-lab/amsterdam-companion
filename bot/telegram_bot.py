import asyncio
import logging
import sys
import os

# Prevent OpenMP conflict crashes on Windows (PyTorch + ONNXRuntime)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.handlers import router
from config.settings import settings
from diagnostics.startup_validator import validate_environment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Run validation before start
    validate_environment()
    
    bot = Bot(token=settings.telegram_token)
    dp = Dispatcher()
    dp.include_router(router)
    
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Import inside to ensure path adjustment
    from aiogram import Bot, Dispatcher
    asyncio.run(main())
