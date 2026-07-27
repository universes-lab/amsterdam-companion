# Amsterdam Companion

Telegram bot for learning Dutch.

## Supervisor Layer (Phase 7A)

AI Supervisor для анализа статистики и генерации отчётов.

### Статус
🟢 **Phase 7A.0** — инфраструктура создана (ожидание реализации)

### Структура
supervisor/
├── engine/ # Логика анализа и отчётов
├── reports/ # Сгенерированные отчёты
├── archive/ # Архив старых memory.json
├── recommendations/ # Рекомендации Advisor (Phase 7B)
├── models/ # GGUF модели (отдельно от MVP!)
├── tests/ # Тесты Supervisor
├── events.jsonl # События от MVP (append-only)
├── memory.json # Агрегированная статистика
└── supervisor.log # Логи Supervisor

### Команды (после реализации)
- `/supervisor report` — еженедельный отчёт
- `/supervisor stats` — краткая сводка
- `/supervisor analyze` — внеочередной анализ

## Setup

1. Copy `.env.example` to `.env` and fill in the values.
2. Install dependencies: `pip install -r requirements.txt`
3. **Important:** Convert translation model once:
   `python scripts/convert_nllb_ct2.py --model facebook/nllb-200-distilled-600M`
4. Run startup validation: `python -c "from diagnostics.startup_validator import validate_environment; validate_environment()"`

## Troubleshooting

- **ffmpeg not found:** Ensure `ffmpeg` is installed and in your system PATH.
- **Model not found:** Make sure you have run the conversion script in Step 3.


🎌 ДИПСИК:

Проект amsterdam-companion официально завершён. Все цепочки рассуждений по нему сворачиваются.
✅ ФИНАЛЬНЫЙ СТАТУС ПРОЕКТА
yaml

Project: amsterdam-companion
Status: COMPLETED ✅
Final_Version: Phase 7B.2
Repository: https://github.com/universes-lab/amsterdam-companion

Итоговые возможности:
  - LIVE Mode: Голосовой перевод RU ↔ NL
  - LEARNING Mode: Помощь в изучении нидерландского
  - Supervisor (Observer): Анализ статистики, отчёты, фильтрация мусора
  - Стабильность: Подтверждена, бот работает

Известные ограничения (приняты):
  - STT: Whisper-tiny (достаточно для базового использования)
  - Supervisor: Observer mode (без автономных действий)