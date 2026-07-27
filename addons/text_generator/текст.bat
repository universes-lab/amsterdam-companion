@echo off
chcp 65001 >nul
echo Generating text...
rem  python generate.py --topic "╨в╤Л ╨│╤Г╨╗╤П╨╡╤И╤М ╨┐╨╛ ╤Г╨╗╨╕╤Ж╨╡" --level A2 --variants 1 --output output/walk_variant.txt
python generate.py --topic "все что с нами проиходит закономерно" --level A2 --variants 1 --output output/walk_variant.txt
echo Done.
