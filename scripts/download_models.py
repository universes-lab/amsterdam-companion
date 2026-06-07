"""
Скрипт для скачивания и размещения всех необходимых моделей.
Запуск: python scripts/download_models.py
"""

import os
import tarfile
import urllib.request
from pathlib import Path
import subprocess
import sys

def download_file(url: str, dest: Path):
    """Скачать файл с прогрессом"""
    print(f"Скачивание: {url}")
    print(f"В: {dest}")
    urllib.request.urlretrieve(url, dest)
    print(f"✓ Завершено: {dest.name}\n")

def setup_stt():
    """STT: Sherpa-onnx Whisper tiny"""
    stt_dir = Path("models/stt")
    stt_dir.mkdir(parents=True, exist_ok=True)
    
    url = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-tiny.tar.bz2"
    tar_path = stt_dir / "sherpa-onnx-whisper-tiny.tar.bz2"
    
    download_file(url, tar_path)
    
    print("Распаковка...")
    with tarfile.open(tar_path, "r:bz2") as tar:
        tar.extractall(stt_dir)
    
    tar_path.unlink()
    print(f"✓ STT модель готова: {stt_dir / 'sherpa-onnx-whisper-tiny'}\n")

def setup_tts():
    """TTS: Piper voices (nl, ru, en)"""
    tts_dir = Path("models/tts")
    tts_dir.mkdir(parents=True, exist_ok=True)
    
    voices = [
        ("nl_BE-nathalie-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/nl/nl_BE/nathalie/medium/nl_BE-nathalie-medium.onnx"),
        ("nl_BE-nathalie-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/nl/nl_BE/nathalie/medium/nl_BE-nathalie-medium.onnx.json"),
        ("ru_RU-irina-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx"),
        ("ru_RU-irina-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json"),

        ("en_US-amy-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"),
        ("en_US-amy-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"),
    ]
    
    for name, url in voices:
        dest = tts_dir / name
        download_file(url, dest)
    
    print(f"✓ TTS голоса готовы: {tts_dir}\n")

def setup_translation():
    """Translation: NLLB-600M INT8 через CTranslate2"""
    tr_dir = Path("models/translation")
    tr_dir.mkdir(parents=True, exist_ok=True)
    
    print("Установка huggingface-hub...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    
    from huggingface_hub import snapshot_download
    
    print("Скачивание оригинальной модели NLLB-600M (~600 MB)...")
    original_model_path = tr_dir / "nllb-200-distilled-600M-original"
    snapshot_download(
        repo_id="facebook/nllb-200-distilled-600M",
        local_dir=original_model_path,
        local_dir_use_symlinks=False
    )
    
    print("✓ Оригинальная модель скачана")
    print("Запуск конвертации в CTranslate2 INT8...")
    
    # Запустить существующий скрипт конвертации с указанием локальной папки оригинальной модели
    subprocess.check_call([
        sys.executable, "scripts/convert_nllb_ct2.py",
        "--model", str(original_model_path)
    ])
    
    print(f"✓ Translation модель готова: {tr_dir / 'nllb-600m-int8'}\n")

def main():
    print("=" * 60)
    print("СКАЧИВАНИЕ МОДЕЛЕЙ ДЛЯ AMSTERDAM-COMPANION")
    print("=" * 60)
    print()
    
    try:
        setup_stt()
        setup_tts()
        setup_translation()
        
        print("=" * 60)
        print("✓ ВСЕ МОДЕЛИ УСПЕШНО РАЗМЕЩЕНЫ")
        print("=" * 60)
        print()
        print("Структура:")
        print("  models/stt/sherpa-onnx-whisper-tiny/")
        print("  models/tts/*.onnx + *.json (nl, ru, en)")
        print("  models/translation/nllb-600m-int8/")
        print()
        print("Готово к запуску бота!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("Проверьте подключение к интернету и повторите попытку.")
        sys.exit(1)

if __name__ == "__main__":
    main()
