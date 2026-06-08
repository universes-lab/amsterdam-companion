@echo off
set FFMPEG_PATH=E:\pinokio\api\facefusion-pinokio.git\.env\Library\bin\ffmpeg.exe
cd ..
mkdir logs 2>nul
python bot\telegram_bot.py > logs\bot.log 2>&1
