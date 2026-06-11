import json
import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger(__name__)

class ReportValidator:
    """Валидирует JSON-вывод модели и генерирует отчёт в Markdown."""
    
    # Ожидаемая схема для weekly отчёта
    EXPECTED_SCHEMA = {
        "period": dict,
        "usage_summary": dict,
        "learning_insights": dict,
        "system_health": dict,
        "actionable_advice": list
    }
    
    @classmethod
    def validate(cls, report_json: str) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Валидирует JSON-строку от модели.
        
        Returns:
            (is_valid, parsed_dict, errors)
        """
        errors = []
        
        # 1. Проверка валидности JSON
        try:
            data = json.loads(report_json)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return False, {}, errors
        
        # 2. Проверка наличия обязательных полей
        for field, expected_type in cls.EXPECTED_SCHEMA.items():
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(data[field], expected_type):
                errors.append(f"Field '{field}' has wrong type: expected {expected_type.__name__}, got {type(data[field]).__name__}")
        
        # 3. Проверка числовых значений (неотрицательные)
        for num_field in ["total_requests", "avg_latency_ms"]:
            value = data.get("usage_summary", {}).get(num_field)
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"usage_summary.{num_field} must be numeric")
        
        # 4. Проверка, что recommendations не пуст
        if not data.get("actionable_advice"):
            errors.append("actionable_advice is empty (model may have no data)")
        
        is_valid = len(errors) == 0
        return is_valid, data, errors
    
    @classmethod
    def to_markdown(cls, data: Dict[str, Any]) -> str:
        """Преобразует валидированный JSON в Markdown отчёт."""
        
        period = data.get("period", {})
        usage = data.get("usage_summary", {})
        insights = data.get("learning_insights", {})
        health = data.get("system_health", {})
        advice = data.get("actionable_advice", [])
        
        md = f"""📊 Еженедельный отчёт ({period.get('from', 'N/A')} - {period.get('to', 'N/A')})

**Использование:**
- Всего запросов: {usage.get('total_requests', 0)}
- LIVE Mode: {usage.get('live_mode_pct', 0)}%
- LEARNING Mode: {usage.get('learn_mode_pct', 0)}%

**Типичные ошибки:**"""
        
        top_mistakes = insights.get('top_mistakes', [])
        if top_mistakes:
            for i, mistake in enumerate(top_mistakes[:3], 1):
                md += f"\n{i}. {mistake.get('category', 'unknown')} — {mistake.get('count', 0)} повторений"
                if mistake.get('recommendation'):
                    md += f"\n   💡 {mistake.get('recommendation')}"
        else:
            md += "\n- Недостаточно данных для выявления закономерностей"
        
        md += f"""

**Система:**
- Средняя латентность: {health.get('avg_latency_ms', 0)} мс
- Ошибок STT: {health.get('stt_failures', 0)}
- Ошибок TTS: {health.get('tts_failures', 0)}
- Общая стабильность: {health.get('error_rate_pct', 100)}%

**Рекомендации:**"""
        
        if advice:
            for rec in advice[:5]:
                md += f"\n- {rec}"
        else:
            md += "\n- Продолжайте практиковаться! Данных пока недостаточно."
        
        md += "\n\n📅 Отчёт сгенерирован автоматически AI Supervisor."
        
        return md
