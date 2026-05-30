@echo off
cd /d "%~dp0"
echo [*] Starting AnonBOT Toolbox...
uv run main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] AnonBOT Toolbox exited with code %ERRORLEVEL%.
    pause
)
