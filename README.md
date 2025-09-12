# elara poker calculator

just a fun little poker tool i made to learn some poker math. nothing super fancy yet, but it works (to some extent lol)

## what it does

- **hand evaluation**: figures out what kind of hand you have (pair, flush, etc.)
- **equity calculation**: runs simulations to see how often you win against opponent ranges
- **preflop strategy**: tells you whether to raise, call, or fold preflop
- **hand analysis**: gives you a full breakdown of your situation
- **range analysis**: categorizes opponent ranges and filters by board texture

## setup

### what you need
- python 3.8+ (i used 3.12)

### quick start

1. clone this repo or download the files
2. run the simple launcher:
   ```bash
   ./start.sh
   ```
   this will automatically set up the virtual environment and start the server

3. open the frontend:
   - double-click `frontend/index.html` to open in your browser
   - the server runs on http://localhost:5001

### manual setup (if needed)

1. go to the backend folder:
   ```bash
   cd backend
   ```

2. create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # on mac/linux
   ```

3. install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. start the server:
   ```bash
   python -m app.main
   ```

## usage

1. start the backend server (see setup above)
2. open `frontend/index.html` in your browser
3. enter your cards, position, and other info
4. click the buttons to get analysis

## api endpoints

the backend provides these endpoints:

- `GET /health` - check if server is running
- `POST /evaluate_hand` - evaluate a poker hand
- `POST /calculate_equity` - calculate equity against opponent range
- `POST /preflop_action` - get preflop recommendation
- `POST /analyze_hand` - full hand analysis
- `POST /partition_range` - categorize opponent's range
- `POST /dynamic_range` - filter range based on board

## features

- **hand evaluation**: figures out what kind of hand you have
- **equity calculation**: simulation against opponent ranges
- **preflop strategy**: realistic heads-up charts with dynamic blending
- **range analysis**: categorizes opponent ranges and filters by board texture
- **hand analysis**: comprehensive breakdown with recommendations

## notes

- this is just for learning, don't use it for real money decisions
- the equity calculations use monte carlo simulation for accuracy
- the preflop strategy blends human charts with calculated risk
- feel free to improve it or add more features

## troubleshooting

- make sure python 3.8+ is installed
- if you get import errors, make sure you're in the virtual environment
- if the server won't start, check that port 5001 isn't already in use
- if the frontend won't load, make sure the backend is running first