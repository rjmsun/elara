# elara poker calculator

just a fun little poker tool i made to learn some poker math. nothing super fancy yet, but it works (to some extent lol)

## what it does

- **hand evaluation**: figures out what kind of hand you have (pair, flush, etc.)
- **equity calculation**: runs simulations to see how often you win against opponent ranges (low number for better calculations)
- **preflop strategy**: tells you whether to raise, call, or fold preflop
- **hand analysis**: gives you a full breakdown of your situation

## setup

### what you need
- python 3.8+ (i used 3.12)

### installation

1. clone this repo or download the files
2. go to the backend folder:
   ```bash
   cd backend
   ```

3. create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # on mac/linux
   # or on windows: venv\Scripts\activate
   ```

4. install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

5. run the app:
   ```bash
   python simple_app.py
   ```


## how to use

### web interface
just open `frontend/index.html` in your browser. it's pretty self-explanatory - enter your cards, opponent range, board, etc.

### api endpoints
if you want to use the api directly:

- `GET /health` - check if server is running
- `POST /calculate_equity` - calculate equity against opponent range
- `POST /preflop_action` - get preflop recommendation
- `POST /analyze_hand` - full hand analysis

### example api call
```bash
curl -X POST http://localhost:5000/calculate_equity \
  -H "Content-Type: application/json" \
  -d '{
    "hero_hand": ["As", "Ah"],
    "villain_range": ["KK", "QQ"],
    "board": [],
    "simulations": 1000
  }'
```

## card format

cards are in the format `"As"`, `"Kh"`, `"7d"`, etc.
- rank: 2-9 (including 6, 7), T, J, Q, K, A
- suit: s (spades), h (hearts), d (diamonds), c (clubs)

## opponent ranges

you can specify ranges like:
- `["AA", "KK", "QQ"]` - specific hands
- `["AKs", "AKo"]` - suited and offsuit
- `[]` - uses default top 25% range
- this is missing a bit

## notes

- the equity calculation runs 1000 simulations by default, so it might take a second
  - currently also very inefficient since it will run against every hand in the range (i will update this later)
- the preflop charts are simplified but should be decent for most situations
- this is just for learning/fun, use at your own risk lol although it's strictly heads up for now and heads up ranges are also notably different

## troubleshooting

if you get import errors, make sure you're in the virtual environment and have installed the requirements.

if the server won't start, make sure port 5000 isn't being used by something else.

## files

- `backend/simple_app.py` - main flask app
- `frontend/index.html` - web interface
- `frontend/js/main.js` - frontend javascript
- `frontend/css/style.css` - styling
- `backend/requirements.txt` - python dependencies

that's it! have fun and don't go broke playing poker :) (always play 67o)