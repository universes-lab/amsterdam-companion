import ctranslate2
import asyncio
from pathlib import Path
from config.settings import TRANSLATION_MODEL_PATH
from transformers import AutoTokenizer

class TranslationEngine:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def _init(self):
        if self._initialized:
            return
            
        if TRANSLATION_MODEL_PATH.exists():
            # Use absolute path from settings
            self.translator = ctranslate2.Translator(str(TRANSLATION_MODEL_PATH), device="cpu")
            # Load tokenizer to properly decode subwords
            # Using the original model path for tokenizer
            orig_model_path = TRANSLATION_MODEL_PATH.parent.parent / "translation" / "nllb-200-distilled-600M-original"
            self.tokenizer = AutoTokenizer.from_pretrained(str(orig_model_path))
        else:
            self.translator = None
            self.tokenizer = None
            print(f"[Warning] Translation model not found at {TRANSLATION_MODEL_PATH}, using mock.")
            
        self.target_prefix = {
            "nl": "nld_Latn",
            "ru": "rus_Cyrl",
            "en": "eng_Latn"
        }
        self._initialized = True
    
    async def translate(self, text: str, src: str, dst: str) -> str:
        if not self._initialized:
            self._init()
        return await asyncio.to_thread(self._sync_translate, text, src, dst)
    
    def _sync_translate(self, text: str, src: str, dst: str):
        if not self.translator:
            return f"[MOCK_TRANSLATION] {text}"
            
        target_lang = self.target_prefix[dst]
        
        # Tokenize input
        tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(text))
        
        # NLLB requires specifying target in prefix
        results = self.translator.translate_batch(
            [[text]],
            target_prefix=[[target_lang]]
        )
        
        # Use tokenizer to decode properly
        hypotheses = results[0].hypotheses[0]
        
        # Remove target prefix if model leaked it
        if hypotheses and hypotheses[0] == target_lang:
            hypotheses = hypotheses[1:]
            
        # Proper decoding
        translated_text = self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(hypotheses), skip_special_tokens=True)
        return translated_text

    def is_loaded(self):
        return self._initialized and self.translator is not None

# Lazy singleton helper
_translation_engine = None

def get_translation_engine():
    global _translation_engine
    if _translation_engine is None:
        _translation_engine = TranslationEngine()
    return _translation_engine

async def translate(text: str, src: str, dst: str) -> str:
    """Translation Interface for NLLB."""
    engine = get_translation_engine()
    return await engine.translate(text, src, dst)
