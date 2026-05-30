@echo off
cd /d "%~dp0"
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] uv is not installed. Install it first: https://docs.astral.sh/uv/#installation
    echo You can also use: pip install uv
    pause
    exit /b 1
)
echo [*] Creating virtual environment with UV...
uv venv
echo.
echo [*] Installing dependencies...
uv pip install -r requirements.txt
echo.
echo [*] Done! Run start.bat to launch AnonBOT Toolbox.
pause
