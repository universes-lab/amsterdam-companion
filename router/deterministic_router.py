COMMAND_MAP = {
    "/live": ("live", None),
    "/learn": ("learn", None),
    "/lang ru→nl": ("live", {"target_lang": "nl", "source_lang": "ru"}),
    "/lang nl→ru": ("live", {"target_lang": "ru", "source_lang": "nl"}),
    "/repeat": ("learn", {"action": "repeat"}),
    "/explain": ("learn", {"action": "explain"}),
}

def route(message: str, current_mode: str) -> tuple[str, dict]:
    # 1. Явные команды
    for cmd, (mode, params) in COMMAND_MAP.items():
        if message.startswith(cmd):
            return mode, params or {}
    
    # 2. Если режим уже active — остаёмся в нём
    if current_mode in ("live", "learn"):
        return current_mode, {}
    
    # 3. Default — live режим
    return "live", {}
