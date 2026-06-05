
@echo off

set GIT_EXE="C:\Program Files\Git\bin\git.exe"

cd /d D:\Gemini\PROJECT\amsterdam-companion

echo.
set /p STAGE=Stage name:

echo.
echo Adding files...
%GIT_EXE% add .

echo.
echo Commit...
%GIT_EXE% commit -m "%STAGE%"

echo.
echo Push...
%GIT_EXE% push github main

echo.
echo DONE
pause