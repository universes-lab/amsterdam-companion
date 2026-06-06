import asyncio
import time
from pathlib import Path
from orchestrator import pipeline_manager

async def benchmark():
    # Загрузка тестового аудиофайла (создать заглушку если нет)
    test_file = Path("tests/sample_nl.ogg")
    if not test_file.exists():
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_bytes(b"mock_audio")
        
    test_audio = test_file.read_bytes()
    
    # Замер полного пайплайна
    start = time.perf_counter()
    result = await pipeline_manager.run_pipeline(test_audio, "test_user")
    total_ms = (time.perf_counter() - start) * 1000
    
    print(f"Total pipeline latency: {total_ms:.0f}ms")
    
    # Проверка метрик
    assert total_ms < 5000, f"Latency too high: {total_ms:.0f}ms"
    return total_ms

if __name__ == "__main__":
    asyncio.run(benchmark())
