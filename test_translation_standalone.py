# test_translation_standalone.py
import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translation.nllb_wrapper import TranslationEngine

async def test():
    tr = TranslationEngine()
    text = "Hoe gaat het met je?"
    print(f"Translating: {text}")
    
    try:
        result = await tr.translate(text, src="nl", dst="ru")
        print(f"Result: '{result}'")
        
        if not result or len(result.strip()) == 0:
            print("ERROR: translation returned empty")
    except Exception as e:
        print(f"ERROR: Translation failed with: {e}")

if __name__ == "__main__":
    asyncio.run(test())
