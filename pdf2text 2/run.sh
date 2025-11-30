#!/bin/bash
# Run script for PDF2Text AI application

echo "========================================"
echo "PDF2Text AI - Starting Application"
echo "========================================"
echo

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please run ./setup.sh first."
    exit 1
fi

# Create directories if they don't exist
mkdir -p logs outputs temp

echo "Starting Streamlit application..."
echo
echo "The application will open in your browser at:"
echo "http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application"
echo

streamlit run app.py
