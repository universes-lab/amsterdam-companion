#!/usr/bin/env python
"""
Верификация загрузки модели Bonsai и работы Supervisor Engine.
"""

import sys
import json
import time
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from companion.llm.qwen_impl import SupervisorQwen
from companion.engine.companion_engine import CompanionEngine
from companion.config.settings import MODEL_PATH, N_GPU_LAYERS, N_CTX, N_BATCH

def setup_test_memory():
    """Создаёт тестовый memory.json."""
    memory = {
        "version": "1.0",
        "period": {"from": "2026-07-01T00:00:00Z", "to": "2026-07-07T23:59:59Z"},
        "total_requests": 50,
        "live_mode_requests": 30,
        "learn_mode_requests": 20,
        "stt_failures": 1,
        "translation_failures": 0,
        "tts_failures": 0,
        "phrases_repeated": {
            "dank u wel": 5,
            "alstublieft": 3
        },
        "system_health": {
            "avg_latency_ms": 450,
            "uptime_hours": 24
        }
    }
    with open("supervisor/memory.json", "w", encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def main():
    print(f"--- Bonsai Verification ---")
    print(f"Model: {MODEL_PATH}")
    print(f"GPU Layers: {N_GPU_LAYERS}")
    
    if not MODEL_PATH.exists():
        print(f"❌ Error: Model file not found at {MODEL_PATH}")
        return 1

    setup_test_memory()
    
    # Используем реальную реализацию
    qwen = SupervisorQwen()
    engine = SupervisorEngine(qwen)
    
    print("Loading engine (this might take a while)...")
    start_load = time.time()
    try:
        engine.load()
        load_time = time.time() - start_load
        print(f"✅ Engine loaded in {load_time:.2f}s")
    except Exception as e:
        print(f"❌ Load failed: {e}")
        return 1
    
    print("Generating report using Bonsai...")
    start_gen = time.time()
    try:
        # We can bypass analyze_and_report to get raw output first
        prompt = engine._build_prompt(engine.memory_manager.load())
        print("Raw Prompt:")
        print(prompt)
        print("---")
        raw_response = engine._call_model(prompt)
        print("\n--- Raw Model Response ---")
        print(raw_response)
        print("--------------------------\n")
        
        report_path = engine.analyze_and_report("verification", profile="inspector")
        gen_time = time.time() - start_gen
        print(f"✅ Report generated in {gen_time:.2f}s")
        print(f"Report saved to: {report_path}")
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n--- Report preview ---")
            print(content[:1000])
            print("...\n")
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        # Печатаем больше инфо об ошибке
        import traceback
        traceback.print_exc()
        return 1
    finally:
        print("Unloading engine...")
        engine.unload()
    
    print("✅ Verification completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
