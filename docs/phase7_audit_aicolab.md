# Phase 7: Аудит компонентов AIColab

## GptOssModel
### Переиспользование:
- `load_model()`: Использовать как основу для `SupervisorQwen.load()`.
  - Принимает `n_gpu_layers`, `n_ctx`, `n_batch`.
- `unload_model()`: Использовать как основу для `SupervisorQwen.unload()`.
  - Правильно выгружает модель, вызывает `gc.collect()`, `torch.cuda.empty_cache()` и `torch.cuda.synchronize()`.

### Не переиспользовать:
- Логика привязки к `GptOssAdapter`. `SupervisorQwen` должен быть независимым.
- Логика формирования промпта (нужно адаптировать под Supervisor).

### Рекомендации:
- Скопировать реализацию загрузки/выгрузки, убрав лишние зависимости и привязки.

## DoctorEngine
### Переиспользование:
- Паттерн `__init__` → `load` → `analyze` → `_call_model` → `_parse_response`.
- Логика извлечения JSON из ответа (`re.search(r'\{.*\}', response, re.DOTALL)`).

### Не переиспользовать:
- Бизнес-логика диагностики ("INTERVENE", "HR-ROTATION").

### Рекомендации:
- Использовать архитектурный паттерн для SupervisorEngine.

## CUDA_Scripts
### Работает:
- `install_llama_with_cuda.ps1`: Переустановка `llama-cpp-python` с поддержкой CUDA.
- `diagnose_gpu.py`: Проверка доступности GPU.

### Требования:
- NVIDIA GPU (compute capability ≥ 5.0).
- CUDA Toolkit 12.x.
- VS Build Tools.

## Итог
Компоненты AIColab пригодны для адаптации.

Рекомендации:
- Использовать `load_model`/`unload_model` из `GptOssModel`.
- Использовать архитектурный паттерн `DoctorEngine`.
- Не копировать бизнес-логику AIColab (роли, отделы, оркестрацию).
