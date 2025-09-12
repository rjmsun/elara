#!/bin/bash

# Elara Poker Calculator - Simple Launcher
echo "Starting Elara Poker Calculator..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start the server
echo "Starting server on http://localhost:5001..."
python -m app.main
