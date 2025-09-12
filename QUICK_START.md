# Elara Poker Calculator - Mac Quick Start Guide

## What You Need (macOS)
- **macOS** (any recent version)
- **Python 3.8+** (install with `brew install python3`)
- **Safari/Chrome/Firefox** browser
- **2 minutes** of your time

## Super Quick Setup (2 commands)

### Option 1: One-Click Start (Recommended)
```bash
# Run setup and start everything
./setup.sh && ./start_elara.sh
```

### Option 2: Step by Step
```bash
# 1. Setup dependencies
./setup.sh

# 2. Start the app (opens browser automatically)
./start_elara.sh
```

### Option 3: Manual Setup
```bash
# Install dependencies
cd backend
pip3 install -r requirements.txt

# Start server
python3 simple_app.py

# Open frontend (in another terminal)
open frontend/index.html
```

## What You'll See

1. **Backend Server**: Running on http://localhost:5000
2. **Frontend Interface**: Beautiful web app with 3 main sections:
   - Hand Analysis
   - Equity Calculator  
   - GTO Preflop Strategy

## Test It Works

### 1. Health Check
```bash
curl http://localhost:5000/health
```
**Expected**: `{"status": "healthy", "service": "Elara Poker Calculator", "version": "2.0.0"}`

### 2. Hand Analysis
```bash
curl -X POST http://localhost:5000/analyze_hand \
  -H "Content-Type: application/json" \
  -d '{"hero_hand": ["As", "Kh"], "position": "BTN", "pot_size": 10, "current_bet": 5}'
```
**Expected**: GTO recommendation and hand analysis

### 3. Equity Calculation
```bash
curl -X POST http://localhost:5000/calculate_equity \
  -H "Content-Type: application/json" \
  -d '{"hero_hand": ["As", "Kh"], "villain_range": ["AA", "KK", "QQ"], "simulations": 100}'
```
**Expected**: Equity percentage (e.g., 0.45 = 45%)

## Try These Examples

### Example 1: Preflop with AK
- **Your Hand**: As Kh
- **Position**: Button
- **Result**: GTO recommends RAISE

### Example 2: Equity vs Tight Range
- **Your Hand**: As Kh  
- **Opponent Range**: AA,KK,QQ,AKs,AQs
- **Result**: ~45% equity

### Example 3: Postflop Analysis
- **Your Hand**: As Kh
- **Board**: Ah 7d 2c
- **Result**: Top pair, top kicker - strong hand

## Troubleshooting

### Server Won't Start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill process if needed
kill -9 <PID>

# Try different port
python simple_app.py --port 5001
```

### Frontend Can't Connect
- Make sure backend is running on http://localhost:5000
- Check browser console for errors
- Try refreshing the page

### Python Issues
```bash
# Check Python version
python3 --version

# Install dependencies manually
pip3 install Flask Flask-CORS numpy

# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Using the Web Interface

1. **Hand Analysis Tab**:
   - Enter your 2 cards (e.g., "As Kh")
   - Add board cards if postflop
   - Select position
   - Click "Analyze Hand"

2. **Equity Calculator Tab**:
   - Enter your hand
   - Enter opponent range (comma-separated)
   - Set simulations (1000 is good)
   - Click "Calculate Equity"

3. **GTO Preflop Tab**:
   - Select position
   - Enter hole cards
   - Click "Get GTO Action"

## Key Features

- **Hand Evaluation**: Recognizes all poker hands  
- **Equity Calculation**: Monte Carlo simulation  
- **GTO Strategy**: Optimal preflop play  
- **Modern UI**: Clean, responsive design  
- **Real-time**: Instant analysis  
- **Mobile-friendly**: Works on phones/tablets  

## Next Steps

- Try different hands and positions
- Experiment with various opponent ranges
- Study the GTO recommendations
- Use for poker study and practice

## Need Help?

- Check the full README.md for detailed documentation
- Look at the browser console for error messages
- Make sure all dependencies are installed
- Verify the backend server is running

---

**You're all set! Happy poker analyzing!**
