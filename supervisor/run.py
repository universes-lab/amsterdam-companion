#!/usr/bin/env python
"""
Точка входа Supervisor Layer (Phase 7A).

Запуск:
    python supervisor/run.py

При первом запуске создаёт файловую структуру и логирует состояние.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Настройка логирования
LOG_FILE = Path("supervisor/supervisor.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def setup_directories() -> None:
    """Гарантирует существование всех необходимых директорий."""
    dirs = [
        "supervisor/reports",
        "supervisor/archive",
        "supervisor/recommendations",
        "supervisor/data",
        "supervisor/engine",
        "supervisor/llm",
        "supervisor/tests",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    logger.debug("Directories verified")


def load_memory() -> dict:
    """Загружает memory.json, создаёт пустой если нет."""
    memory_file = Path("supervisor/memory.json")
    if not memory_file.exists():
        logger.info("Memory file not found, creating empty")
        empty_memory = {
            "version": "1.0",
            "period": {
                "from": datetime.utcnow().isoformat() + "Z",
                "to": datetime.utcnow().isoformat() + "Z"
            },
            "total_requests": 0,
            "live_mode_requests": 0,
            "learn_mode_requests": 0,
            "stt_failures": 0,
            "translation_failures": 0,
            "tts_failures": 0,
            "phrases_repeated": {},
            "direction_usage": {"ru→nl": 0, "nl→ru": 0},
            "avg_latency_ms": 0,
            "latency_sample_count": 0,
            "system_health": {}
        }
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(empty_memory, f, indent=2, ensure_ascii=False)
        return empty_memory
    
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
            logger.info(f"Memory loaded: {len(memory)} entries")
            return memory
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load memory: {e}")
        return {}


def load_events() -> tuple[int, list]:
    """Загружает events.jsonl и возвращает (offset, count)."""
    events_file = Path("supervisor/events.jsonl")
    if not events_file.exists():
        logger.info("Events file not found, will be created on first bot request")
        return 0, 0
    
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            count = len([l for l in lines if l.strip()])
            offset = events_file.stat().st_size if count > 0 else 0
            logger.info(f"Events loaded: {count} events")
            return offset, count
    except OSError as e:
        logger.error(f"Failed to read events: {e}")
        return 0, 0


def main():
    parser = argparse.ArgumentParser(description="AI Supervisor for amsterdam-companion")
    parser.add_argument("--update-memory", action="store_true",
                        help="Обновить memory.json из events.jsonl и выйти")
    parser.add_argument("--schedule", action="store_true",
                        help="Запустить планировщик задач")
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("Supervisor started")
    logger.info(f"Args: {args}")
    
    # Проверка структуры
    setup_directories()
    
    # Загрузка состояния
    memory = load_memory()
    offset, event_count = load_events()
    
    if args.schedule:
        import schedule
        import time
        
        def scheduled_update():
            logger.info("Scheduled update started")
            # Обновляем memory.json из events.jsonl
            from supervisor.data.event_reader import EventReader
            from supervisor.data.memory_manager import MemoryManager
            
            events_file = Path("supervisor/events.jsonl")
            memory_file = Path("supervisor/memory.json")
            archive_dir = Path("supervisor/archive")
            
            reader = EventReader(events_file)
            manager = MemoryManager(memory_file, archive_dir)
            
            # Читаем состояние (offset)
            state_file = Path("supervisor/state.json")
            last_offset = 0
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    last_offset = state.get("last_event_offset", 0)
            
            events, new_offset = reader.read_new_events(last_offset)
            if events:
                stats = reader.aggregate_events(events)
                manager.update(stats)
                with open(state_file, 'w') as f:
                    json.dump({"last_event_offset": new_offset}, f)
                logger.info(f"Updated memory with {len(events)} events")
            else:
                logger.info("No new events")
        
        # Запланировать на 03:00
        schedule.every().day.at("03:00").do(scheduled_update)
        logger.info("Scheduler started, next update at 03:00")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    elif args.update_memory:
        logger.info("Update mode: will process events and update memory")
        # TODO: Phase 7A.6 — полноценная обработка
        logger.info(f"Events offset: {offset}, count: {event_count}")
        logger.info("Memory update not yet implemented (Phase 7A.6)")
    else:
        # Стандартный запуск — только статус
        logger.info("Supervisor is ready (observer mode)")
        logger.info(f"Memory version: {memory.get('version', 'unknown')}")
        logger.info(f"Total requests tracked: {memory.get('total_requests', 0)}")
        logger.info(f"Events in queue: {event_count}")
    
    logger.info("Supervisor finished")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
