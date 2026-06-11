import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from supervisor.llm.base import SupervisorLLM
from supervisor.data.event_reader import EventReader
from supervisor.data.memory_manager import MemoryManager
from supervisor.engine.validator import ReportValidator

logger = logging.getLogger(__name__)

class SupervisorEngine:
    """Оркестратор анализа и генерации отчётов."""
    
    def __init__(self, llm: SupervisorLLM, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            llm: Реализация SupervisorLLM (например, SupervisorQwen)
            config: Конфигурация (пути к файлам)
        """
        self.llm = llm
        self.config = config or {}
        
        # Инициализация компонентов
        events_file = Path(self.config.get("events_file", "supervisor/events.jsonl"))
        memory_file = Path(self.config.get("memory_file", "supervisor/memory.json"))
        archive_dir = Path(self.config.get("archive_dir", "supervisor/archive"))
        self.reports_dir = Path(self.config.get("reports_dir", "supervisor/reports"))
        
        self.event_reader = EventReader(events_file)
        self.memory_manager = MemoryManager(memory_file, archive_dir)
        
        self._loaded = False
        self._last_analysis = None
        self._last_report = None
        self._error_count = 0
    
    def load(self) -> None:
        """Загружает LLM и инициализирует компоненты."""
        logger.info("Loading SupervisorEngine...")
        self.llm.load()
        self._loaded = True
        logger.info("SupervisorEngine ready")
    
    def unload(self) -> None:
        """Выгружает LLM и освобождает ресурсы."""
        if self._loaded:
            self.llm.unload()
            self._loaded = False
            logger.info("SupervisorEngine unloaded")
    
    def _build_prompt(self, memory: Dict[str, Any]) -> str:
        """Формирует промпт для модели на основе memory.json."""
        period = memory.get("period", {})
        
        # Адаптируем под структуру memory.json из MemoryManager
        total = memory.get("total_requests", 0)
        live_pct = round(memory.get("live_mode_requests", 0) / max(total, 1) * 100)
        learn_pct = round(memory.get("learn_mode_requests", 0) / max(total, 1) * 100)
        
        prompt = f"""Ты — AI Supervisor для нидерландского языкового помощника.

Данные для анализа за период {period.get('from', 'N/A')} - {period.get('to', 'N/A')}:

Использование:
- Всего запросов: {total}
- LIVE Mode: {live_pct}%
- LEARNING Mode: {learn_pct}%

Ошибки:
- STT failures: {memory.get('stt_failures', 0)}
- Translation failures: {memory.get('translation_failures', 0)}
- TTS failures: {memory.get('tts_failures', 0)}

Повторяемые фразы: {json.dumps(memory.get('phrases_repeated', {}), ensure_ascii=False)}

Система:
- Средняя латентность: {memory.get('avg_latency_ms', 0)} мс

Сгенерируй еженедельный отчёт в формате JSON со следующими полями:
- period: {{"from": "...", "to": "..."}}
- usage_summary: {{"total_requests": 0, "live_mode_pct": 0, "learn_mode_pct": 0}}
- learning_insights: {{"top_mistakes": [{{"category": "...", "count": 0, "recommendation": "..."}}], "progress_trend": "improving|stable|declining"}}
- system_health: {{"avg_latency_ms": 0, "error_rate_pct": 0, "recommendations": ["..."]}}
- actionable_advice: ["..."]

Важно:
1. Не выдумывай данные. Если данных недостаточно — пиши "недостаточно данных".
2. Все числа должны соответствовать входным данным.
3. Рекомендации должны быть конкретными.
4. Язык отчёта: русский.

Вот JSON:
"""
        return prompt
    
    def _call_model(self, prompt: str) -> str:
        """Синхронный вызов модели (обёртка)."""
        if not self._loaded:
            raise RuntimeError("Engine not loaded. Call load() first.")
        return self.llm.analyze(prompt)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Парсит ответ модели с валидацией."""
        is_valid, data, errors = ReportValidator.validate(response)
        if not is_valid:
            logger.error(f"Validation failed: {errors}")
            raise ValueError(f"Invalid model output: {errors}")
        return data
    
    def analyze_and_report(self, report_type: str = "weekly") -> str:
        """
        Выполняет полный цикл анализа и генерирует отчёт.
        
        Returns:
            Путь к сгенерированному отчёту
        """
        logger.info(f"Starting {report_type} analysis...")
        
        # 1. Загружаем memory.json
        memory = self.memory_manager.load()
        
        # 2. Формируем промпт
        prompt = self._build_prompt(memory)
        logger.debug(f"Prompt length: {len(prompt)} chars")
        
        # 3. Вызываем модель
        start_time = time.time()
        try:
            response = self._call_model(prompt)
            elapsed = time.time() - start_time
            logger.info(f"Model inference completed in {elapsed:.2f}s")
        except Exception as e:
            logger.error(f"Model call failed: {e}")
            self._error_count += 1
            raise
        
        # 4. Валидируем ответ
        try:
            data = self._parse_response(response)
        except ValueError as e:
            self._error_count += 1
            raise
        
        # 5. Генерируем Markdown отчёт
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_filename = f"{report_type}_{datetime.utcnow().strftime('%Y_%W')}.md"
        report_path = self.reports_dir / report_filename
        
        markdown = ReportValidator.to_markdown(data)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        self._last_analysis = datetime.utcnow().isoformat()
        self._last_report = str(report_path)
        
        logger.info(f"Report saved: {report_path}")
        return str(report_path)
    
    def update_memory(self) -> None:
        """Обновляет memory.json на основе новых событий."""
        logger.info("Updating memory from events...")
        
        # Читаем состояние (offset)
        state_file = Path("supervisor/state.json")
        last_offset = 0
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    last_offset = state.get("last_event_offset", 0)
            except:
                pass
        
        # Читаем новые события
        events, new_offset = self.event_reader.read_new_events(last_offset)
        
        if not events:
            logger.info("No new events to process")
        else:
            # Агрегируем события
            stats = self.event_reader.aggregate_events(events)
            
            # Обновляем memory.json
            self.memory_manager.update(stats)
            
            # Сохраняем новый offset
            state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(state_file, 'w') as f:
                json.dump({"last_event_offset": new_offset}, f)
            
            logger.info(f"Processed {len(events)} events, memory updated")
        
        # Ротация памяти (если нужно)
        self.memory_manager.rotate_if_needed(max_age_days=90)
    
    def get_status(self) -> dict:
        """Возвращает текущий статус Supervisor."""
        return {
            "status": "READY" if self._loaded else "NOT_LOADED",
            "last_analysis": self._last_analysis,
            "last_report": self._last_report,
            "errors": self._error_count
        }
