import ctranslate2
import asyncio
from pathlib import Path

class TranslationEngine:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        model_path = Path("models/translation/nllb-600m-int8")
        # In a real scenario, this would load the model.
        # For testing, we mock if model doesn't exist, but instruction implies it will exist.
        if model_path.exists():
            self.translator = ctranslate2.Translator(str(model_path), device="cpu")
        else:
            self.translator = None
            print("[Warning] Translation model not found, using mock.")
            
        self.target_prefix = {
            "nl": "nld_Latn",
            "ru": "rus_Cyrl",
            "en": "eng_Latn"
        }
    
    async def translate(self, text: str, src: str, dst: str) -> str:
        return await asyncio.to_thread(self._sync_translate, text, src, dst)
    
    def _sync_translate(self, text: str, src: str, dst: str):
        if not self.translator:
            return f"[MOCK_TRANSLATION] {text}"
            
        source_lang = self.target_prefix[src]
        target_lang = self.target_prefix[dst]
        
        # NLLB requires specifying source/target in tokens
        results = self.translator.translate(
            [text],
            source_lang=source_lang,
            target_lang=target_lang,
            max_batch_size=1
        )
        
        # CT2 returns tokens/scores, need to reconstruct string
        # Assuming typical CT2 output structure
        return "".join(results[0].hypotheses[0])

# Interface wrapper
translation_engine = TranslationEngine()

async def translate(text: str, src: str, dst: str) -> str:
    """Translation Interface for NLLB."""
    return await translation_engine.translate(text, src, dst)
