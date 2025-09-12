from flask import Flask, request, jsonify
from flask_cors import CORS
from elara.engine.card import Card
from elara.engine.game_state import GameState, Position, Action, Street
from elara.utils.hand_evaluator import ElaraHandEvaluator
from elara.giffer.range_handler import Range
from elara.gto.strategy import GtoStrategy
from elara.engine.player_profile import OpponentModeler

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize Elara components
hand_evaluator = ElaraHandEvaluator()
gto_strategy = GtoStrategy()
opponent_modeler = OpponentModeler()

@app.route('/evaluate_hand', methods=['POST'])
def evaluate_hand_route():
    """
    Evaluate a hand using Elara's sophisticated analysis.
    
    Expected JSON:
    {
        "hero_hand": ["As", "Kh"],
        "board": ["Ah", "7d", "2c"],
        "hero_position": "button",
        "villain_position": "big_blind",
        "pot_size": 10,
        "current_bet": 5,
        "opponent_name": "player123",
        "action_history": [
            {"player": "villain", "action": "raise", "amount": 3, "street": "preflop"},
            {"player": "hero", "action": "call", "amount": 3, "street": "preflop"},
            {"player": "villain", "action": "bet", "amount": 5, "street": "flop"}
        ]
    }
    """
    try:
        data = request.json
        
        # Parse hero's hand
        hero_hand = [Card(card_str) for card_str in data.get('hero_hand', [])]
        
        # Parse board
        board = [Card(card_str) for card_str in data.get('board', [])]
        
        # Create game state
        game_state = GameState(
            hero_stack=data.get('hero_stack', 100),
            villain_stack=data.get('villain_stack', 100)
        )
        
        # Set positions
        hero_pos = Position.BUTTON if data.get('hero_position') == 'button' else Position.BIG_BLIND
        game_state.set_positions(hero_pos)
        
        # Set pot and current bet
        game_state.pot_size = data.get('pot_size', 0)
        game_state.current_bet = data.get('current_bet', 0)
        
        # Deal board cards
        if len(board) >= 3:
            game_state.deal_flop(board[:3])
        if len(board) >= 4:
            game_state.deal_turn(board[3])
        if len(board) >= 5:
            game_state.deal_river(board[4])
        
        # Add action history
        for action_data in data.get('action_history', []):
            player = action_data['player']
            action_str = action_data['action']
            amount = action_data.get('amount', 0)
            street_str = action_data.get('street', 'preflop')
            
            # Convert street string to enum
            street_map = {
                'preflop': Street.PREFLOP,
                'flop': Street.FLOP,
                'turn': Street.TURN,
                'river': Street.RIVER
            }
            street = street_map.get(street_str, Street.PREFLOP)
            
            # Convert action string to enum
            action_map = {
                'fold': Action.FOLD,
                'check': Action.CHECK,
                'call': Action.CALL,
                'bet': Action.BET,
                'raise': Action.RAISE,
                'all_in': Action.ALL_IN
            }
            action = action_map.get(action_str, Action.CALL)
            
            game_state.add_action(player, action, amount, street)
        
        # Get opponent name for dynamic modeling
        opponent_name = data.get('opponent_name')
        
        # Evaluate the hand with enhanced features
        evaluation = hand_evaluator.evaluate_hand(hero_hand, game_state, opponent_name=opponent_name)
        
        return jsonify(evaluation)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/analyze_action', methods=['POST'])
def analyze_action_route():
    """
    Analyze the consequences of a proposed action.
    
    Expected JSON:
    {
        "hero_hand": ["As", "Kh"],
        "game_state": {...},  # Same as evaluate_hand
        "proposed_action": "raise",
        "bet_size": 15
    }
    """
    try:
        data = request.json
        
        # Parse hero's hand
        hero_hand = [Card(card_str) for card_str in data.get('hero_hand', [])]
        
        # Reconstruct game state (simplified)
        game_state = GameState(
            hero_stack=data.get('hero_stack', 100),
            villain_stack=data.get('villain_stack', 100)
        )
        
        # Set positions
        hero_pos = Position.BUTTON if data.get('hero_position') == 'button' else Position.BIG_BLIND
        game_state.set_positions(hero_pos)
        
        # Add action history
        for action_data in data.get('action_history', []):
            player = action_data['player']
            action_str = action_data['action']
            amount = action_data.get('amount', 0)
            
            action_map = {
                'fold': Action.FOLD,
                'check': Action.CHECK,
                'call': Action.CALL,
                'bet': Action.BET,
                'raise': Action.RAISE,
                'all_in': Action.ALL_IN
            }
            action = action_map.get(action_str, Action.CALL)
            
            game_state.add_action(player, action, amount)
        
        # Analyze the proposed action
        proposed_action = data.get('proposed_action')
        bet_size = data.get('bet_size')
        
        analysis = hand_evaluator.analyze_what_if(hero_hand, game_state, proposed_action, bet_size)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/calculate_equity', methods=['POST'])
def calculate_equity_route():
    """
    Calculate equity between hands or ranges.
    
    Expected JSON:
    {
        "hero_hand": ["As", "Kh"],
        "opponent_range": ["AA", "KK", "QQ", "AKs", "AKo"],
        "board": ["Ah", "7d", "2c"]
    }
    """
    try:
        data = request.json
        
        # Parse hero's hand
        hero_hand = [Card(card_str) for card_str in data.get('hero_hand', [])]
        
        # Parse board
        board = [Card(card_str) for card_str in data.get('board', [])]
        
        # Create opponent range
        opponent_hands = data.get('opponent_range', [])
        opponent_range = Range.from_hand_list(opponent_hands)
        
        # Calculate equity
        equity = hand_evaluator.equity_calculator.calculate_equity(
            hero_hand, opponent_range, board
        )
        
        return jsonify({
            'hero_hand': data.get('hero_hand'),
            'opponent_range': opponent_hands,
            'board': data.get('board', []),
            'equity': equity
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/monte_carlo_equity', methods=['POST'])
def monte_carlo_equity_route():
    """
    Calculate equity using Monte Carlo simulation.
    
    Expected JSON:
    {
        "hero_hand": ["As", "Kh"],
        "opponent_range": "AA,KK,QQ,AKs,AQs",
        "board": ["Ah", "7d", "2c"],
        "num_simulations": 5000
    }
    """
    try:
        data = request.json
        
        # Parse hero's hand
        hero_hand = [Card(card_str) for card_str in data.get('hero_hand', [])]
        
        # Parse board
        board = [Card(card_str) for card_str in data.get('board', [])]
        
        # Get opponent range and simulation count
        opponent_range = data.get('opponent_range', '')
        num_simulations = data.get('num_simulations', 5000)
        
        # Calculate Monte Carlo equity
        equity = hand_evaluator.equity_calculator.monte_carlo_equity(
            hero_hand, opponent_range, board, num_simulations
        )
        
        return jsonify({
            'hero_hand': data.get('hero_hand'),
            'opponent_range': opponent_range,
            'board': data.get('board', []),
            'equity': equity,
            'num_simulations': num_simulations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/partition_range', methods=['POST'])
def partition_range_route():
    """
    Partition an opponent's range into strategic categories.
    
    Expected JSON:
    {
        "opponent_range": "AA,KK,QQ,AKs,AQs",
        "board": ["Ah", "7d", "2c"]
    }
    """
    try:
        data = request.json
        
        # Parse board
        board = [Card(card_str) for card_str in data.get('board', [])]
        
        # Get opponent range
        opponent_range = data.get('opponent_range', '')
        
        # Create range object and partition
        range_obj = Range.from_hand_list(opponent_range.split(','))
        partitions = range_obj.partition_range(opponent_range, board)
        
        return jsonify({
            'opponent_range': opponent_range,
            'board': data.get('board', []),
            'partitions': partitions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/gto_preflop_action', methods=['POST'])
def gto_preflop_action_route():
    """
    Get GTO-based pre-flop action recommendation.
    
    Expected JSON:
    {
        "position": "BTN",
        "hole_cards": ["As", "Kh"]
    }
    """
    try:
        data = request.json
        
        # Parse hole cards
        hole_cards = [Card(card_str) for card_str in data.get('hole_cards', [])]
        
        # Get position and action
        position = data.get('position', 'BB')
        action = gto_strategy.get_preflop_action(position, hole_cards)
        
        # Get range coverage
        range_coverage = gto_strategy.get_range_coverage(position, 'open')
        
        return jsonify({
            'position': position,
            'hole_cards': data.get('hole_cards'),
            'action': action,
            'range_coverage': range_coverage
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/update_player_stats', methods=['POST'])
def update_player_stats_route():
    """
    Update player statistics for opponent modeling.
    
    Expected JSON:
    {
        "player_name": "player123",
        "did_vpip": true,
        "did_pfr": true,
        "postflop_actions": ["BET", "CALL", "RAISE"]
    }
    """
    try:
        data = request.json
        
        player_name = data.get('player_name')
        did_vpip = data.get('did_vpip', False)
        did_pfr = data.get('did_pfr', False)
        postflop_actions = data.get('postflop_actions', [])
        
        # Update player statistics
        opponent_modeler.update_player_stats(player_name, did_vpip, did_pfr, postflop_actions)
        
        # Get updated profile
        profile = opponent_modeler.get_player_tendencies(player_name)
        
        return jsonify({
            'player_name': player_name,
            'profile': profile,
            'message': 'Statistics updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_player_profile', methods=['GET'])
def get_player_profile_route():
    """
    Get player profile and tendencies.
    
    Query parameters:
    - player_name: Name of the player
    """
    try:
        player_name = request.args.get('player_name')
        
        if not player_name:
            return jsonify({'error': 'player_name parameter is required'}), 400
        
        # Get player profile
        profile = opponent_modeler.get_player_tendencies(player_name)
        
        return jsonify({
            'player_name': player_name,
            'profile': profile
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_all_profiles', methods=['GET'])
def get_all_profiles_route():
    """Get all player profiles."""
    try:
        profiles = opponent_modeler.get_all_profiles()
        
        return jsonify({
            'profiles': profiles,
            'total_players': len(profiles)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_range', methods=['POST'])
def get_range_route():
    """
    Get a GTO-based range for a given position and action.
    
    Expected JSON:
    {
        "position": "button",
        "action": "raise",
        "bet_size": 3
    }
    """
    try:
        data = request.json
        
        position = data.get('position')
        action = data.get('action')
        bet_size = data.get('bet_size')
        
        # Create range from GTO chart
        range_obj = Range.from_gto_chart(position, action, bet_size)
        weighted_hands = range_obj.get_weighted_hands()
        
        return jsonify({
            'position': position,
            'action': action,
            'bet_size': bet_size,
            'hands': list(weighted_hands.keys()),
            'total_hands': len(weighted_hands)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Elara Poker Calculator',
        'version': '0.1.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)