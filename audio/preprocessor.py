import asyncio
import tempfile
import subprocess
import shlex
from pathlib import Path
from config.settings import settings

async def preprocess_voice(audio_bytes: bytes) -> bytes:
    """
    Конвертирует Telegram OGG/Opus в 16kHz mono PCM.
    Запускает ffmpeg СИНХРОННО в отдельном потоке, чтобы не ломать event loop.
    Это решает проблему с Access Violation на Windows 10.
    """
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f_in:
        f_in.write(audio_bytes)
        f_in.flush()
        input_path = f_in.name

    output_path = tempfile.mktemp(suffix=".pcm")

    # Используем путь к ffmpeg из настроек
    cmd = f'"{settings.ffmpeg_path}" -i {shlex.quote(input_path)} -ar 16000 -ac 1 -f s16le {shlex.quote(output_path)} -y'

    try:
        # ЗАМЕНА: вызов в отдельном потоке, НЕ асинхронный subprocess
        process = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            shell=True,
            timeout=10  # Жесткий таймаут 10 секунд
        )

        if process.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {process.stderr}")

        # Читаем PCM данные (синхронно, быстро)
        pcm_data = Path(output_path).read_bytes()
        return pcm_data

    finally:
        # Очистка временных файлов (ДАЖЕ при ошибке)
        for path in [input_path, output_path]:
            try:
                p = Path(path)
                if p.exists():
                    p.unlink()
            except OSError:
                pass

async def preprocess(audio_bytes: bytes) -> bytes:
    """Audio preprocessing (ffmpeg wrapper)."""
    return await preprocess_voice(audio_bytes)
