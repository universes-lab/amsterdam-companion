#!/usr/bin/env python
"""
Тест загрузки и работы модели Qwen GGUF (без интеграции с ботом).

Запуск:
    python supervisor/tests/test_model.py

Требования:
    - Модель в supervisor/models/Qwen2.5-1.5B-VibeThinker-heretic-uncensored-abliterated.Q5_K_M.gguf
    - Установлен llama-cpp-python[cuda]
"""

import sys
import time
from pathlib import Path

# Добавляем корень проекта в sys.path для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def test_model():
    """Тестирует загрузку, генерацию и выгрузку модели."""
    
    # Путь к модели (Q5_K_M, если не найден — пробуем Q4_K_M)
    models_dir = Path("supervisor/models")
    model_path_q5 = models_dir / "Qwen2.5-1.5B-VibeThinker-heretic-uncensored-abliterated.Q5_K_M.gguf"
    model_path_q4 = models_dir / "Qwen2.5-1.5B-VibeThinker-heretic-uncensored-abliterated.Q4_K_M.gguf"
    
    if model_path_q5.exists():
        model_path = model_path_q5
        logger.info(f"Using Q5_K_M model: {model_path}")
    elif model_path_q4.exists():
        model_path = model_path_q4
        logger.info(f"Using Q4_K_M model (fallback): {model_path}")
    else:
        logger.error("No model found in supervisor/models/")
        return False
    
    try:
        from llama_cpp import Llama
    except ImportError as e:
        logger.error(f"llama-cpp-python not installed: {e}")
        logger.info("Run: pip install llama-cpp-python[cuda]")
        return False
    
    # Загрузка модели
    logger.info("Loading model...")
    start_load = time.time()
    
    try:
        llm = Llama(
            model_path=str(model_path),
            n_ctx=2048,           # Контекст 2K (достаточно для анализа отчётов)
            n_gpu_layers=-1,      # Все слои на GPU
            n_batch=512,          # Размер батча
            verbose=False,
        )
        load_time = time.time() - start_load
        logger.info(f"Model loaded in {load_time:.2f}s")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False
    
    # Тестовый промпт
    prompt = "Привет! Ты работаешь?"
    logger.info(f"Sending prompt: {prompt}")
    start_infer = time.time()
    
    try:
        response = llm(
            prompt,
            max_tokens=50,
            temperature=0.7,
            stop=["\n\n", "User:", "Human:"],
            echo=False
        )
        infer_time = time.time() - start_infer
        answer = response['choices'][0]['text'].strip()
        logger.info(f"Response received in {infer_time:.2f}s")
        logger.info(f"Answer: {answer[:200]}..." if len(answer) > 200 else f"Answer: {answer}")
        
        # Простая проверка: ответ не должен быть пустым
        if not answer:
            logger.error("Empty response from model")
            return False
            
        logger.info("✅ Model test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate response: {e}")
        return False
    
    finally:
        # Выгрузка модели (освобождение памяти)
        logger.info("Unloading model...")
        del llm
        import gc
        gc.collect()
        
        # Очистка CUDA кэша (если доступен)
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("CUDA cache cleared")
        except ImportError:
            pass
        
        logger.info("Model unloaded")


if __name__ == "__main__":
    success = test_model()
    sys.exit(0 if success else 1)
