import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    """Управляет memory.json (агрегированная статистика)."""
    
    def __init__(self, memory_file: Path, archive_dir: Path):
        """
        Args:
            memory_file: Путь к memory.json
            archive_dir: Путь к директории архивов
        """
        self.memory_file = Path(memory_file)
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Загружает текущий memory.json."""
        if not self.memory_file.exists():
            logger.warning(f"Memory file not found: {self.memory_file}")
            return self._create_empty_memory()
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load memory: {e}")
            return self._create_empty_memory()
    
    def save(self, memory: Dict[str, Any]) -> None:
        """Сохраняет memory.json."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    
    def update(self, new_stats: Dict[str, Any]) -> None:
        """
        Обновляет memory.json новыми агрегатами.
        
        Args:
            new_stats: Новая статистика (результат aggregate_events)
        """
        current = self.load()
        
        # Обновляем счётчики
        for key in ["total_requests", "live_mode_requests", "learn_mode_requests",
                    "stt_failures", "translation_failures", "tts_failures"]:
            current[key] = current.get(key, 0) + new_stats.get(key, 0)
        
        # Обновляем phrases_repeated
        for phrase, count in new_stats.get("phrases_repeated", {}).items():
            current.setdefault("phrases_repeated", {})[phrase] = current.get("phrases_repeated", {}).get(phrase, 0) + count
        
        # Обновляем direction_usage
        for direction, count in new_stats.get("direction_usage", {}).items():
            current.setdefault("direction_usage", {})[direction] = current.get("direction_usage", {}).get(direction, 0) + count
        
        # Обновляем среднюю латентность (скользящее среднее)
        if new_stats.get("avg_latency_count", 0) > 0:
            old_avg = current.get("avg_latency_ms", 0)
            old_count = current.get("latency_sample_count", 0)
            new_avg = new_stats["avg_latency_sum"] / new_stats["avg_latency_count"]
            new_count = old_count + new_stats["avg_latency_count"]
            
            if old_count == 0:
                current["avg_latency_ms"] = new_avg
            else:
                current["avg_latency_ms"] = (old_avg * old_count + new_stats["avg_latency_sum"]) / new_count
            
            current["latency_sample_count"] = new_count
        
        # Обновляем период
        current["period"] = {
            "from": current.get("period", {}).get("from", datetime.utcnow().isoformat() + "Z"),
            "to": datetime.utcnow().isoformat() + "Z"
        }
        
        # Обновляем версию
        current["version"] = "1.0"
        
        # Системные метрики (пока заглушки)
        current.setdefault("system_health", {})
        
        self.save(current)
    
    def rotate_if_needed(self, max_age_days: int = 90) -> None:
        """
        Если memory.json старше max_age_days — архивирует и создаёт новый.
        """
        if not self.memory_file.exists():
            return
        
        current = self.load()
        period_to = current.get("period", {}).get("to")
        if not period_to:
            return
        
        try:
            # Парсим ISO формат (2026-06-01T00:00:00Z)
            to_date = datetime.fromisoformat(period_to.replace('Z', '+00:00'))
            age_days = (datetime.utcnow() - to_date).days
            
            if age_days >= max_age_days:
                # Архивируем
                archive_name = f"memory_{to_date.strftime('%Y_%m')}.json"
                archive_path = self.archive_dir / archive_name
                
                import shutil
                shutil.copy(self.memory_file, archive_path)
                logger.info(f"Archived memory to {archive_path}")
                
                # Создаём новый memory.json
                new_memory = self._create_empty_memory()
                new_memory["period"]["from"] = datetime.utcnow().isoformat() + "Z"
                new_memory["period"]["to"] = datetime.utcnow().isoformat() + "Z"
                self.save(new_memory)
                logger.info("Created new memory.json")
        except Exception as e:
            logger.error(f"Failed to rotate memory: {e}")
    
    def _create_empty_memory(self) -> Dict[str, Any]:
        """Создаёт пустую структуру memory.json."""
        now = datetime.utcnow().isoformat() + "Z"
        return {
            "version": "1.0",
            "period": {"from": now, "to": now},
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
