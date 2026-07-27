#!/usr/bin/env python
"""
Тест SupervisorEngine на тестовых данных.
"""

import sys
import json
import tempfile
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
        "period": {"from": "2026-06-01T00:00:00Z", "to": "2026-06-08T23:59:59Z"},
        "total_requests": 142,
        "live_mode_requests": 98,
        "learn_mode_requests": 44,
        "stt_failures": 3,
        "translation_failures": 0,
        "tts_failures": 1,
        "phrases_repeated": {
            "de_het_articles": 22,
            "hen_hun_distinction": 14,
            "word_order_questions": 8
        },
        "system_health": {
            "avg_latency_ms": 920,
            "uptime_hours": 168
        }
    }
    with open("supervisor/memory.json", "w") as f:
        json.dump(memory, f, indent=2)


def main():
    print("Setting up test memory...")
    setup_test_memory()
    
    print("Initializing SupervisorQwen...")
    # Инициализируем Qwen через интерфейс, соответствующий SupervisorEngine
    class MockQwen(SupervisorQwen):
        def __init__(self, model_path, n_gpu_layers, n_ctx, n_batch):
            self.model_path = model_path
            self.n_gpu_layers = n_gpu_layers
            self.n_ctx = n_ctx
            self.n_batch = n_batch
            self.llm = None
        
        def load(self):
            from llama_cpp import Llama
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                n_batch=self.n_batch,
                verbose=False
            )
        
        def unload(self):
            if self.llm:
                del self.llm
                self.llm = None
                
        def analyze(self, prompt, system_prompt=None):
            # В тестовом режиме возвращаем заглушку JSON, которую validator пропустит
            return """{
                "period": {"from": "2026-06-01", "to": "2026-06-08"},
                "usage_summary": {"total_requests": 142, "live_mode_pct": 69, "learn_mode_pct": 31},
                "learning_insights": {
                    "top_mistakes": [{"category": "articles", "count": 22, "recommendation": "Practice de/het"}],
                    "progress_trend": "stable"
                },
                "system_health": {"avg_latency_ms": 920, "error_rate_pct": 5, "recommendations": ["Fix STT"]},
                "actionable_advice": ["Keep going!"]
            }"""

    qwen = MockQwen(
        model_path=MODEL_PATH,
        n_gpu_layers=N_GPU_LAYERS,
        n_ctx=N_CTX,
        n_batch=N_BATCH
    )
    
    print("Initializing SupervisorEngine...")
    engine = SupervisorEngine(qwen)
    
    print("Loading engine...")
    engine.load()
    
    print("Generating weekly report...")
    try:
        report_path = engine.analyze_and_report("weekly")
        print(f"✅ Report generated: {report_path}")
        
        # Показываем первые 500 символов отчёта
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n--- Report preview ---")
            print(content[:500])
            print("...\n")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1
    finally:
        print("Unloading engine...")
        engine.unload()
    
    print("✅ Test completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
