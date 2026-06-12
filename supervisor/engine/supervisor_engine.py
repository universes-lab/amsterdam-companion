import json
import logging
import time
import yaml
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
        
        # Загрузка промпта
        self.system_prompt = self._load_system_prompt()
        
        self._loaded = False
        self._last_analysis = None
        self._last_report = None
        self._error_count = 0

    def _load_system_prompt(self) -> str:
        """Загружает системный промпт из YAML."""
        prompt_path = Path("supervisor/prompts/system_prompt.yaml")
        if not prompt_path.exists():
            logger.warning("System prompt not found, using minimal default")
            return "You are an AI supervisor. Analyze data and return JSON."
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_config = yaml.safe_load(f)
            
            # Извлекаем компоненты
            constitution = prompt_config.get('constitution', {})
            identity = prompt_config.get('identity', {})
            analysis_rules = prompt_config.get('analysis_rules', {})
            
            # Формируем текстовый промпт для модели
            prompt_parts = []
            
            # 1. Конституция (высший приоритет)
            rules = constitution.get('mandatory_rules', [])
            if rules:
                prompt_parts.append("## CONSTITUTION (absolute priority)")
                for rule in rules:
                    prompt_parts.append(f"- {rule.get('rule', '')}")
            
            # 2. Идентичность
            prompt_parts.append(f"\n## IDENTITY\nRole: {identity.get('role', 'AI Supervisor')}")
            prompt_parts.append(f"Personality: {identity.get('personality', 'Inspector')}")
            prompt_parts.append(f"Operating Mode: {identity.get('operating_mode', 'Offline asynchronous analysis')}")
            
            # 3. Аналитические правила
            if analysis_rules:
                prompt_parts.append("\n## ANALYSIS RULES")
                for key, value in analysis_rules.items():
                    if isinstance(value, list):
                        prompt_parts.append(f"- {key}: {', '.join(value)}")
                    else:
                        prompt_parts.append(f"- {key}: {value}")
            
            # 4. Формат вывода
            output_format = prompt_config.get('output_format', {})
            prompt_parts.append(f"\n## OUTPUT FORMAT\n{output_format.get('format', 'json')}")
            prompt_parts.append(f"Required fields: {output_format.get('required_fields', [])}")
            
            final_prompt = "\n".join(prompt_parts)
            logger.info(f"System prompt loaded ({len(final_prompt)} chars)")
            return final_prompt
            
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            return "You are an AI supervisor. Analyze data and return JSON."

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
        # ... (здесь используется старый код сборки промпта) ...
        # ВНИМАНИЕ: Для Phase 7B.1 этот метод должен быть обновлен, 
        # чтобы формировать только ДАННЫЕ, так как системный промпт теперь отделен.
        
        # Обновленная реализация:
        data_str = json.dumps(memory, ensure_ascii=False)
        return f"Данные для анализа:\n{data_str}"
    
    def _call_model(self, prompt: str, profile: str = "inspector") -> str:
        """Синхронный вызов модели."""
        if not self._loaded:
            raise RuntimeError("Engine not loaded. Call load() first.")
        
        # Подстановка профиля в системный промпт
        system_prompt = self.system_prompt.replace("{profile_name}", profile)
        return self.llm.analyze(prompt, system_prompt=system_prompt)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Парсит ответ модели с валидацией."""
        is_valid, data, errors = ReportValidator.validate(response)
        if not is_valid:
            logger.error(f"Validation failed: {errors}")
            raise ValueError(f"Invalid model output: {errors}")
        return data
    
    def analyze_and_report(self, report_type: str = "weekly", profile: str = "inspector") -> str:
        """
        Выполняет полный цикл анализа и генерирует отчёт.
        """
        logger.info(f"Starting {report_type} analysis with profile {profile}...")
        
        # 1. Загружаем memory.json
        memory = self.memory_manager.load()
        
        # 2. Формируем промпт (только данные)
        prompt = self._build_prompt(memory)
        logger.debug(f"Prompt length: {len(prompt)} chars")
        
        # 3. Вызываем модель с системным промптом
        start_time = time.time()
        try:
            response = self._call_model(prompt, profile=profile)
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
        # ... (остается без изменений) ...
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
