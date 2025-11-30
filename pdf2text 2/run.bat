@echo off
REM Run script for PDF2Text AI application

echo ========================================
echo PDF2Text AI - Starting Application
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Create directories if they don't exist
if not exist "logs" mkdir logs
if not exist "outputs" mkdir outputs
if not exist "temp" mkdir temp

echo Starting Streamlit application...
echo.
echo The application will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py

pause
