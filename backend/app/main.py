#!/usr/bin/env python3
"""
elara poker calculator - just a fun little poker tool i made (do not trust this for real money decisions lol)

basically does:
- hand evaluation (figures out what you have)
- equity calculation (how often you win)
- preflop strategy (should you raise/fold)
- opponent modeling (what they might have)

nothing fancy, just trying to learn some poker math :p
"""

from flask import Flask
from flask_cors import CORS
from .api.routes import register_routes

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    CORS(app)
    
    # Register all routes
    register_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    print("starting elara poker calculator...")
    print("available endpoints:")
    print("  - GET  /health")
    print("  - POST /evaluate_hand")
    print("  - POST /calculate_equity")
    print("  - POST /preflop_action")
    print("  - POST /analyze_hand")
    print("  - POST /partition_range")
    print("  - POST /dynamic_range")
    print("server running on http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
