@echo off
cd /d "%~dp0"
set GCARDS_HOST=0.0.0.0
echo ============================================================
echo   Starting the 5 games on the NETWORK
echo   Friends on the same Wi-Fi open the address shown below.
echo ============================================================
echo.
python run_all.py
echo.
echo (The games have stopped. Press any key to close.)
pause >nul
