import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class EventReader:
    """Читает события из events.jsonl (append-only лог)."""
    
    def __init__(self, events_file: Path):
        """
        Args:
            events_file: Путь к events.jsonl
        """
        self.events_file = Path(events_file)
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
    
    def read_new_events(self, last_offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """
        Читает новые события из events.jsonl начиная с last_offset.
        
        Args:
            last_offset: Позиция в файле (байт), с которой читать
            
        Returns:
            (список событий, новый offset (размер файла))
        """
        events = []
        if not self.events_file.exists():
            return events, 0
        
        with open(self.events_file, 'r', encoding='utf-8') as f:
            # Пропускаем до last_offset
            if last_offset > 0:
                f.seek(last_offset)
            
            # Читаем все строки
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse event: {line[:100]}... Error: {e}")
                    continue
        
        # Новый offset = размер файла
        new_offset = self.events_file.stat().st_size if self.events_file.exists() else 0
        return events, new_offset
    
    @staticmethod
    def aggregate_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Агрегирует события в статистику для memory.json.
        
        Args:
            events: Список событий
            
        Returns:
            Агрегированная статистика (счётчики по типам)
        """
        stats = {
            "total_requests": 0,
            "live_mode_requests": 0,
            "learn_mode_requests": 0,
            "stt_failures": 0,
            "translation_failures": 0,
            "tts_failures": 0,
            "recent_transcriptions": [], # Новый список для анализа текста
            "phrases_repeated": {},
            "direction_usage": {"ru→nl": 0, "nl→ru": 0},
            "avg_latency_sum": 0,
            "avg_latency_count": 0,
        }
        
        for event in events:
            event_type = event.get("type", "")
            stats["total_requests"] += 1
            
            if event_type == "live_request":
                stats["live_mode_requests"] += 1
                
                # Собираем текст для анализа
                transcription = event.get("transcription")
                if transcription:
                    stats["recent_transcriptions"].append(transcription)
                
                direction = event.get("direction", "")
                if direction in stats["direction_usage"]:
                    stats["direction_usage"][direction] += 1
                # Латентность
                latency = event.get("latency_ms")
                if latency is not None and isinstance(latency, (int, float)):
                    stats["avg_latency_sum"] += latency
                    stats["avg_latency_count"] += 1
                    
            elif event_type == "learn_request":
                stats["learn_mode_requests"] += 1
                phrase_category = event.get("phrase_category")
                if phrase_category:
                    stats["phrases_repeated"][phrase_category] = stats["phrases_repeated"].get(phrase_category, 0) + 1
                    
            elif event_type == "error":
                component = event.get("component", "")
                if component == "stt":
                    stats["stt_failures"] += 1
                elif component == "translation":
                    stats["translation_failures"] += 1
                elif component == "tts":
                    stats["tts_failures"] += 1
        
        return stats
