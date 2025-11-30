#!/bin/bash
# Setup script for PDF2Text AI application

echo "========================================"
echo "PDF2Text AI - Setup"
echo "========================================"
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

echo "[1/4] Checking Python version..."
python3 --version

echo
echo "[2/4] Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "[3/4] Creating necessary directories..."
mkdir -p logs outputs temp

echo
echo "[4/4] Setting up environment file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your API key."
else
    echo ".env file already exists."
fi

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit .env file and add your DeepSeek API key"
echo "2. Run './run.sh' to start the application"
echo
