def build_response(mode: str, translation: str, tts_audio: bytes = None, explanation: str = None) -> dict:
    if mode == "live":
        # LIVE: минимум текста, упор на голос
        return {
            "text": translation,  # краткий текст
            "voice": tts_audio,
            "reply_markup": None
        }
    elif mode == "learn":
        # LEARN: текст + пояснения + кнопки
        buttons = []
        if explanation:
            buttons.append({"text": "Объяснить", "callback_data": "explain"})
        return {
            "text": f"{translation}\n\n📖 {explanation}" if explanation else translation,
            "voice": tts_audio,
            "reply_markup": {"inline_keyboard": [buttons]} if buttons else None
        }
    return {"text": translation, "voice": tts_audio}
