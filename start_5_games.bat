@echo off
cd /d "%~dp0"
echo Starting the game versions...
echo.
python run_all.py
echo.
echo (The games have stopped. Press any key to close this window.)
pause >nul
