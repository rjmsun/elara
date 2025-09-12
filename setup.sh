#!/bin/bash

# Elara Poker Calculator - Mac Setup Script
echo "Setting up Elara Poker Calculator for macOS..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "WARNING: This script is optimized for macOS. You may need to adjust for other systems."
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Install Python 3.8+ using one of these methods:"
    echo "   - Homebrew: brew install python3"
    echo "   - Official installer: https://www.python.org/downloads/"
    echo "   - MacPorts: sudo port install python38"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $python_version"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not available. Please install pip."
    exit 1
fi

# Navigate to backend directory
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Setup complete!"
    echo ""
    echo "Quick Start Commands:"
    echo "1. Start the backend server:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   python simple_app.py"
    echo ""
    echo "2. Open the frontend (choose one):"
    echo "   - Double-click frontend/index.html"
    echo "   - Or: open frontend/index.html"
    echo "   - Or serve with: cd frontend && python3 -m http.server 8000"
    echo ""
    echo "Backend: http://localhost:5000"
    echo "Frontend: file:///path/to/frontend/index.html or http://localhost:8000"
    echo ""
    echo "Pro tip: You can create an alias in your ~/.zshrc or ~/.bash_profile:"
    echo "   alias elara='cd $(pwd) && cd backend && source venv/bin/activate && python simple_app.py'"
    echo ""
    echo "Happy poker analyzing!"
else
    echo "ERROR: Setup failed. Please check the error messages above."
    exit 1
fi
