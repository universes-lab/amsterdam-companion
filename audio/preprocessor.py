import asyncio
import tempfile
import shlex
import time
from pathlib import Path
from config.settings import settings

async def preprocess_voice(audio_bytes: bytes) -> bytes:
    # Telegram voice OGG/Opus → 16kHz mono PCM (raw)
    
    # Create temp files but close them immediately so ffmpeg can open them
    f_in = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    f_in.write(audio_bytes)
    f_in.close()
    
    f_out = tempfile.NamedTemporaryFile(suffix=".pcm", delete=False)
    f_out.close()
    
    try:
        # Use ffmpeg path from settings
        cmd = f'"{settings.ffmpeg_path}" -i {shlex.quote(f_in.name)} -ar 16000 -ac 1 -f s16le {shlex.quote(f_out.name)} -y'
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await asyncio.wait_for(proc.wait(), timeout=10)
        
        pcm_data = Path(f_out.name).read_bytes()
        return pcm_data
    finally:
        # Robust cleanup
        for f in [f_in.name, f_out.name]:
            for _ in range(5):
                try:
                    if os.path.exists(f):
                        os.unlink(f)
                    break
                except PermissionError:
                    await asyncio.sleep(0.1)

async def preprocess(audio_bytes: bytes) -> bytes:
    """Audio preprocessing (ffmpeg wrapper)."""
    return await preprocess_voice(audio_bytes)
