import asyncio
import tempfile
import shlex
from pathlib import Path

async def preprocess_voice(audio_bytes: bytes) -> bytes:
    # Telegram voice OGG/Opus → 16kHz mono PCM (raw)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f_in:
        f_in.write(audio_bytes)
        f_in.flush()
        
        with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as f_out:
            # Assuming ffmpeg is available in path as per startup_validator
            cmd = f"ffmpeg -i {shlex.quote(f_in.name)} -ar 16000 -ac 1 -f s16le {shlex.quote(f_out.name)} -y"
            proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await asyncio.wait_for(proc.wait(), timeout=5)
            
            pcm_data = Path(f_out.name).read_bytes()
            Path(f_in.name).unlink()
            Path(f_out.name).unlink()
            return pcm_data

async def preprocess(audio_bytes: bytes) -> bytes:
    """Audio preprocessing (ffmpeg wrapper)."""
    return await preprocess_voice(audio_bytes)
