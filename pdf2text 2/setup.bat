@echo off
REM Setup script for PDF2Text AI application

echo ========================================
echo PDF2Text AI - Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "outputs" mkdir outputs
if not exist "temp" mkdir temp

echo.
echo [4/4] Setting up environment file...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file. Please edit it with your API key.
) else (
    echo .env file already exists.
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your DeepSeek API key
echo 2. Run 'run.bat' to start the application
echo.
pause
