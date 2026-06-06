# Правила для режима обучения
DUTCH_FIRST_RULES = {
    "default_language": "nl",
    "english_fallback": False,
    "russian_hints": "on_demand",  # только по команде /hint
    "simplify_on_error": True,
    "slow_on_request": True,
}

def apply_dutch_policy(response_text: str, user_level: str = "beginner") -> str:
    # упрощение сложных конструкций для beginners
    if user_level == "beginner":
        response_text = response_text.replace("zou kunnen", "kan")
        # ...
    return response_text
