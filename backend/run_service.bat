@echo off
setlocal
cd /d "%~dp0"

:loop
echo [%date% %time%] Starting AutoVision AI Service...
python app.py
echo [%date% %time%] Service stopped or crashed. Restarting in 3 seconds...
timeout /t 3
goto loop
