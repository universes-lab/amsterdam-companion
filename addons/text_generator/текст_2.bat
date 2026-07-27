@echo off
REM python generate.py --input-text "Я иду в магазин за хлебом" --variants 5 --style conversation --target-language nl  > test.txt
python generate.py --input-text "Я иду в магазин за хлебом" --variants 5 --style conversation --target-language ru > test.txt

