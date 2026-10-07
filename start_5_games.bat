@echo off
cd /d "%~dp0"
REM Listen on the network too, so other devices can join.
set GCARDS_HOST=0.0.0.0
echo ============================================================
echo   Starting the 5 games (reachable on your Wi-Fi network)
echo   Friends open the address printed below.
echo ============================================================
echo.
python run_all.py
echo.
echo (The games have stopped. Press any key to close this window.)
pause >nul
