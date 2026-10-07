@echo off
cd /d "%~dp0"
set GCARDS_HOST=0.0.0.0
echo ============================================================
echo   Starting ONE game on the NETWORK (port 8000)
echo   Friends on the same Wi-Fi open the address shown below.
echo ============================================================
echo.
python run.py
echo.
echo (The game has stopped. Press any key to close.)
pause >nul
