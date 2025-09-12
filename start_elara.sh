#!/bin/bash

# Elara Poker Calculator - Mac Launcher Script
echo "Starting Elara Poker Calculator..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "ERROR: Virtual environment not found. Running setup first..."
    ./setup.sh
    if [ $? -ne 0 ]; then
        echo "ERROR: Setup failed. Please run ./setup.sh manually."
        exit 1
    fi
fi

# Start the backend server
echo "Starting backend server..."
cd backend
source venv/bin/activate
python simple_app.py &
BACKEND_PID=$!

# Wait a moment for the server to start
sleep 3

# Check if the server started successfully
if curl -s http://localhost:5000/health > /dev/null; then
    echo "Backend server started successfully!"
    echo "Backend running on http://localhost:5000"
    
    # Open the frontend in the default browser
    echo "Opening frontend in your default browser..."
    open "../frontend/index.html"
    
    echo ""
    echo "Elara is now running!"
    echo "Backend: http://localhost:5000"
    echo "Frontend: Opened in your browser"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Keep the script running and show server logs
    wait $BACKEND_PID
else
    echo "ERROR: Failed to start backend server"
    echo "Try running manually:"
    echo "   cd backend && source venv/bin/activate && python simple_app.py"
    exit 1
fi
