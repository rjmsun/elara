from flask import request, jsonify
from ..poker.card import Card
from ..poker.evaluator import HandEvaluator
from ..poker.equity import EquityCalculator
from ..poker.strategy import PreflopStrategy
from ..poker.range_filter import filter_range_for_board, partition_range
import random

def validate_no_duplicate_cards(hero_hand, board):
    """Check for duplicate cards between hero hand and board"""
    all_cards = hero_hand + board
    card_strings = [f"{card.rank}{card.suit}" for card in all_cards]
    
    if len(card_strings) != len(set(card_strings)):
        # find the duplicates
        seen = set()
        duplicates = set()
        for card_str in card_strings:
            if card_str in seen:
                duplicates.add(card_str)
            seen.add(card_str)
        raise ValueError(f"Duplicate cards detected: {', '.join(duplicates)}")

def get_dynamic_opponent_range(position, pot_size, current_bet, board):
    """Get a dynamic opponent range based on betting action and board texture"""
    
    # figure out how big the bet is to see how tight their range should be
    bet_to_pot_ratio = current_bet / max(pot_size, 1) if pot_size > 0 else 0
    
    # different positions have different ranges
    if position == "SB":
        # against sb, bb defends wider
        if bet_to_pot_ratio < 0.5:  # small bet/limp
            range_type = "wide"
        elif bet_to_pot_ratio < 1.0:  # medium bet
            range_type = "medium"
        else:  # large bet
            range_type = "tight"
    else:  # BB
        # against bb, sb can be more aggressive
        if bet_to_pot_ratio < 0.3:
            range_type = "wide"
        elif bet_to_pot_ratio < 0.8:
            range_type = "medium"
        else:
            range_type = "tight"
    
    # pick the range based on tightness
    if range_type == "wide":
        # ~40% of hands: loose range
        return [
            'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
            'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',
            'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s',
            'QJs', 'QTs', 'Q9s', 'Q8s', 'Q7s', 'Q6s',
            'JTs', 'J9s', 'J8s', 'J7s',
            'T9s', 'T8s', 'T7s',
            '98s', '97s',
            '87s', '86s',
            '76s', '75s',
            '65s', '54s',
            'AKo', 'AQo', 'AJo', 'ATo', 'A9o', 'A8o', 'A7o', 'A6o', 'A5o',
            'KQo', 'KJo', 'KTo', 'K9o', 'K8o',
            'QJo', 'QTo', 'Q9o',
            'JTo', 'J9o',
            'T9o'
        ]
    elif range_type == "medium":
        # ~25% of hands: standard range
        return [
            'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
            'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',
            'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s',
            'QJs', 'QTs', 'Q9s', 'Q8s',
            'JTs', 'J9s', 'J8s',
            'T9s', 'T8s',
            '98s', '97s',
            '87s',
            '76s',
            'AKo', 'AQo', 'AJo', 'ATo', 'A9o',
            'KQo', 'KJo', 'KTo',
            'QJo'
        ]
    else:  # tight
        # ~15% of hands: tight range
        return [
            'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55',
            'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
            'KQs', 'KJs', 'KTs', 'K9s',
            'QJs', 'QTs',
            'JTs',
            'T9s',
            '98s',
            'AKo', 'AQo', 'AJo', 'ATo',
            'KQo'
        ]

def calculate_dynamic_hand_strength(hero_hand, board, position, pot_size, current_bet):
    """Calculate hand strength against a dynamic opponent range"""
    try:
        # get the opponent's range based on their betting
        opponent_range = get_dynamic_opponent_range(position, pot_size, current_bet, board)
        
        # use equity calculator to get win rate against this range
        equity = equity_calculator.calculate_equity(hero_hand, opponent_range, board, simulations=500)
        
        # convert equity (0.0-1.0) to percentage (0-100)
        return round(equity * 100, 1)
    except Exception as e:
        print(f"Error calculating dynamic hand strength: {e}")
        # fallback to percentile calculation
        return calculate_hand_percentile(hero_hand)

def calculate_hand_percentile(hero_hand):
    """Calculate hand strength as percentile (0-100) based on all possible hands"""
    if len(hero_hand) != 2:
        return 0.0
    
    # all possible starting hands (169 total)
    all_hands = [
        # pairs (13 hands)
        'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
        # suited hands (78 hands)
        'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',
        'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s',
        'QJs', 'QTs', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s',
        'JTs', 'J9s', 'J8s', 'J7s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s',
        'T9s', 'T8s', 'T7s', 'T6s', 'T5s', 'T4s', 'T3s', 'T2s',
        '98s', '97s', '96s', '95s', '94s', '93s', '92s',
        '87s', '86s', '85s', '84s', '83s', '82s',
        '76s', '75s', '74s', '73s', '72s',
        '65s', '64s', '63s', '62s',
        '54s', '53s', '52s',
        '43s', '42s',
        '32s',
        # offsuit hands (78 hands)
        'AKo', 'AQo', 'AJo', 'ATo', 'A9o', 'A8o', 'A7o', 'A6o', 'A5o', 'A4o', 'A3o', 'A2o',
        'KQo', 'KJo', 'KTo', 'K9o', 'K8o', 'K7o', 'K6o', 'K5o', 'K4o', 'K3o', 'K2o',
        'QJo', 'QTo', 'Q9o', 'Q8o', 'Q7o', 'Q6o', 'Q5o', 'Q4o', 'Q3o', 'Q2o',
        'JTo', 'J9o', 'J8o', 'J7o', 'J6o', 'J5o', 'J4o', 'J3o', 'J2o',
        'T9o', 'T8o', 'T7o', 'T6o', 'T5o', 'T4o', 'T3o', 'T2o',
        '98o', '97o', '96o', '95o', '94o', '93o', '92o',
        '87o', '86o', '85o', '84o', '83o', '82o',
        '76o', '74o', '73o', '72o',
        '65o', '64o', '63o', '62o',
        '54o', '53o', '52o',
        '43o', '42o',
        '32o'
    ]
    
    # turn the hero hand into AKs notation
    card1, card2 = hero_hand
    if card1.value == card2.value:
        hand_notation = f"{card1.rank}{card2.rank}"
    elif card1.suit == card2.suit:
        if card1.value > card2.value:
            hand_notation = f"{card1.rank}{card2.rank}s"
        else:
            hand_notation = f"{card2.rank}{card1.rank}s"
    else:
        if card1.value > card2.value:
            hand_notation = f"{card1.rank}{card2.rank}o"
        else:
            hand_notation = f"{card2.rank}{card1.rank}o"
    
    # find where this hand ranks
    try:
        position = all_hands.index(hand_notation)
        # convert to percentile (0-100)
        percentile = ((len(all_hands) - position - 1) / (len(all_hands) - 1)) * 100
        return round(percentile, 1)
    except ValueError:
        return 0.0

# set up components we need
hand_evaluator = HandEvaluator()
equity_calculator = EquityCalculator()
preflop_strategy = PreflopStrategy()

def register_routes(app):
    """Register all API routes with the Flask app"""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """just checks if the server is running"""
        return jsonify({
            'status': 'healthy',
            'service': 'elara poker calculator',
            'version': '2.0.0'
        })

    @app.route('/evaluate_hand', methods=['POST'])
    def evaluate_hand():
        """Evaluate a poker hand"""
        try:
            data = request.json
            cards_str = data.get('cards', [])
            
            if len(cards_str) != 5:
                return jsonify({'error': 'Need exactly 5 cards'}), 400
            
            cards = [Card(card_str) for card_str in cards_str]
            result = hand_evaluator.evaluate_hand(cards)
            
            return jsonify(result)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/calculate_equity', methods=['POST'])
    def calculate_equity():
        """figures out how often you win against their range"""
        try:
            data = request.json
            hero_hand_str = data.get('hero_hand', [])
            villain_range = data.get('villain_range', [])
            board_str = data.get('board', [])
            simulations = data.get('simulations', 1000)
            
            # check the inputs
            if len(hero_hand_str) != 2:
                return jsonify({'error': 'Hero hand must have exactly 2 cards'}), 400
            
            hero_hand = [Card(card_str) for card_str in hero_hand_str]
            board = [Card(card_str) for card_str in board_str]
            
            # make sure no duplicate cards
            validate_no_duplicate_cards(hero_hand, board)
            
            # use default top 25% range if no range provided
            if not villain_range:
                villain_range = [
                    'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                    'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',
                    'AKo', 'AQo', 'AJo', 'ATo', 'A9o', 'A8o', 'A7o', 'A6o', 'A5o', 'A4o', 'A3o', 'A2o',
                    'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s',
                    'KQo', 'KJo', 'KTo', 'K9o', 'K8o', 'K7o', 'K6o', 'K5o', 'K4o', 'K3o', 'K2o',
                    'QJs', 'QTs', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s',
                    'QJo', 'QTo', 'Q9o', 'Q8o', 'Q7o', 'Q6o', 'Q5o', 'Q4o', 'Q3o', 'Q2o',
                    'JTs', 'J9s', 'J8s', 'J7s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s',
                    'JTo', 'J9o', 'J8o', 'J7o', 'J6o', 'J5o', 'J4o', 'J3o', 'J2o',
                    'T9s', 'T8s', 'T7s', 'T6s', 'T5s', 'T4s', 'T3s', 'T2s',
                    'T9o', 'T8o', 'T7o', 'T6o', 'T5o', 'T4o', 'T3o', 'T2o',
                    '98s', '97s', '96s', '95s', '94s', '93s', '92s',
                    '98o', '97o', '96o', '95o', '94o', '93o', '92o',
                    '87s', '86s', '85s', '84s', '83s', '82s',
                    '87o', '86o', '85o', '84o', '83o', '82o',
                    '76s', '75s', '74s', '73s', '72s',
                    '76o', '75o', '74o', '73o', '72o',
                    '65s', '64s', '63s', '62s',
                    '65o', '64o', '63o', '62o',
                    '54s', '53s', '52s',
                    '54o', '53o', '52o',
                    '43s', '42s',
                    '43o', '42o',
                    '32s', '32o'
                ]
            
            if simulations < 10 or simulations > 10000:
                return jsonify({'error': 'Simulations must be between 10 and 10000'}), 400
            
            # Parse cards with error handling
            try:
                board = [Card(card_str) for card_str in board_str]
            except Exception as e:
                return jsonify({'error': f'Invalid card format: {str(e)}'}), 400
            
            # make sure no duplicate cards
            all_cards = hero_hand + board
            card_strings = [str(card) for card in all_cards]
            if len(card_strings) != len(set(card_strings)):
                return jsonify({'error': 'Duplicate cards detected in hero hand or board'}), 400
            
            # Validate board size
            if len(board) > 5:
                return jsonify({'error': 'Board cannot have more than 5 cards'}), 400
            
            # Validate no impossible scenarios (like 5 aces on board)
            if len(board) > 0:
                board_ranks = [card.rank for card in board]
                rank_counts = {}
                for rank in board_ranks:
                    rank_counts[rank] = rank_counts.get(rank, 0) + 1
                    if rank_counts[rank] > 4:
                        return jsonify({'error': f'Impossible: {rank_counts[rank]} {rank}s on board (max 4)'}), 400
            
            # Calculate equity
            equity = equity_calculator.calculate_equity(hero_hand, villain_range, board, simulations)
            
            return jsonify({
                'hero_hand': hero_hand_str,
                'villain_range': villain_range,
                'board': board_str,
                'equity': equity,
                'simulations': simulations
            })
        
        except Exception as e:
            return jsonify({'error': f'Calculation failed: {str(e)}'}), 400

    @app.route('/preflop_action', methods=['POST'])
    def preflop_action():
        """tells you what to do preflop"""
        try:
            data = request.json
            position = data.get('position', 'SB')
            hole_cards_str = data.get('hole_cards', [])
            
            if len(hole_cards_str) != 2:
                return jsonify({'error': 'Need exactly 2 hole cards'}), 400
            
            hole_cards = [Card(card_str) for card_str in hole_cards_str]
            
            # Calculate hand percentile for blending
            hand_percentile = calculate_hand_percentile(hole_cards)
            
            # Use dynamic preflop action that blends chart with calculated risk
            action = preflop_strategy.get_dynamic_preflop_action(position, hole_cards, hand_percentile)
            
            return jsonify({
                'position': position,
                'hole_cards': hole_cards_str,
                'action': action
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/analyze_hand', methods=['POST'])
    def analyze_hand():
        """does a full analysis of your hand and situation"""
        try:
            data = request.json
            hero_hand_str = data.get('hero_hand', [])
            board_str = data.get('board', [])
            position = data.get('position', 'SB')
            pot_size = data.get('pot_size', 0)
            current_bet = data.get('current_bet', 0)
            
            hero_hand = [Card(card_str) for card_str in hero_hand_str]
            board = [Card(card_str) for card_str in board_str]
            
            # make sure no duplicate cards
            validate_no_duplicate_cards(hero_hand, board)
            
            # Calculate dynamic hand strength against betting-based range
            hand_strength = calculate_dynamic_hand_strength(hero_hand, board, position, pot_size, current_bet)
            
            # Determine hand type for display
            if len(board) >= 3:
                all_cards = hero_hand + board
                if len(all_cards) >= 5:
                    # Get best 5-card hand for display only
                    from itertools import combinations
                    best_hand_type = "high_card"
                    best_strength = 0
                    
                    for combo in combinations(all_cards, 5):
                        hand_result = hand_evaluator.evaluate_hand(list(combo))
                        if hand_result['strength'] > best_strength:
                            best_strength = hand_result['strength']
                            best_hand_type = hand_result['hand_type']
                else:
                    best_hand_type = "incomplete"
            else:
                best_hand_type = "preflop"
            
            best_hand = {'hand_type': best_hand_type, 'strength': hand_strength}
            
            # Calculate pot odds first
            pot_odds = current_bet / (pot_size + current_bet) if (pot_size + current_bet) > 0 else 0
            
            # Get recommendation based on game stage
            if len(board) == 0:
                # Preflop: Calculate hand percentile for blending
                hand_percentile = calculate_hand_percentile(hero_hand)
                preflop_action = preflop_strategy.get_dynamic_preflop_action(position, hero_hand, hand_percentile)
            else:
                # Postflop: Use hand strength and pot odds
                preflop_action = preflop_strategy.get_postflop_action(position, hand_strength, pot_odds)
            
            return jsonify({
                'hero_hand': hero_hand_str,
                'board': board_str,
                'position': position,
                'hand_analysis': best_hand,
                'preflop_recommendation': preflop_action,
                'pot_size': pot_size,
                'current_bet': current_bet,
                'pot_odds': pot_odds,
                'recommendation': _get_recommendation(best_hand, preflop_action, pot_odds, len(board))
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/partition_range', methods=['POST'])
    def partition_range_endpoint():
        """Partitions a villain's range into strategic categories"""
        try:
            data = request.json
            villain_range = data.get('villain_range', [])
            board_str = data.get('board', [])
            
            if not board_str or len(board_str) < 3:
                return jsonify({'error': 'Board must have at least 3 cards for range partitioning'}), 400
            
            board = [Card(c) for c in board_str]
            
            # Partition the range
            categories = partition_range(villain_range, board)
            
            return jsonify({
                'villain_range': villain_range,
                'board': board_str,
                'categories': categories
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/dynamic_range', methods=['POST'])
    def get_dynamic_range():
        """Filters a preflop range based on board texture"""
        try:
            data = request.json
            preflop_range = data.get('villain_range', [])
            board_str = data.get('board', [])
            player_profile = data.get('player_profile', 'tight')

            if not board_str or len(board_str) < 3:
                return jsonify({'error': 'Board must have at least 3 cards for dynamic filtering'}), 400

            board = [Card(c) for c in board_str]

            # Call the filtering function
            postflop_range = filter_range_for_board(preflop_range, board, player_profile)

            return jsonify({
                'original_range_size': len(preflop_range),
                'filtered_range_size': len(postflop_range),
                'filtered_range': postflop_range,
                'board': board_str,
                'player_profile': player_profile
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 400

# Helper functions
def _get_hand_cards(hand_notation: str, excluded_cards: list) -> list:
    """Get specific cards for a hand notation, avoiding excluded cards"""
    if len(hand_notation) < 2:
        return []
    
    # create a deck excluding the specified cards
    deck = equity_calculator._create_deck(excluded_cards, [])
    
    if len(hand_notation) == 2:  # pair like "AA"
        rank = hand_notation[0]
        cards = []
        for suit in ['s', 'h', 'd', 'c']:
            card_str = f"{rank}{suit}"
            card = Card(card_str)
            if card not in excluded_cards:
                cards.append(card)
        return cards[:2] if len(cards) >= 2 else []
    
    elif hand_notation.endswith('s'):  # suited like "AKs"
        rank1, rank2 = hand_notation[0], hand_notation[1]
        # find a suit that works for both cards
        for suit in ['s', 'h', 'd', 'c']:
            card1_str = f"{rank1}{suit}"
            card2_str = f"{rank2}{suit}"
            card1, card2 = Card(card1_str), Card(card2_str)
            if card1 not in excluded_cards and card2 not in excluded_cards:
                return [card1, card2]
        return []
    
    elif hand_notation.endswith('o'):  # offsuit like "AKo"
        rank1, rank2 = hand_notation[0], hand_notation[1]
        # find two different suits
        suits = ['s', 'h', 'd', 'c']
        for suit1 in suits:
            for suit2 in suits:
                if suit1 != suit2:
                    card1_str = f"{rank1}{suit1}"
                    card2_str = f"{rank2}{suit2}"
                    card1, card2 = Card(card1_str), Card(card2_str)
                    if card1 not in excluded_cards and card2 not in excluded_cards:
                        return [card1, card2]
        return []
    
    return []

def _calculate_hand_strength_simulation(hero_hand: list) -> float:
    """Calculate hand strength by simulating against all possible starting hands"""
    if len(hero_hand) != 2:
        return 0.0
    
    # All possible starting hands (169 total)
    all_hands = [
        'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
        'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',
        'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s',
        'QJs', 'QTs', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s',
        'JTs', 'J9s', 'J8s', 'J7s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s',
        'T9s', 'T8s', 'T7s', 'T6s', 'T5s', 'T4s', 'T3s', 'T2s',
        '98s', '97s', '96s', '95s', '94s', '93s', '92s',
        '87s', '86s', '85s', '84s', '83s', '82s',
        '76s', '75s', '74s', '73s', '72s',
        '65s', '64s', '63s', '62s',
        '54s', '53s', '52s',
        '43s', '42s',
        '32s',
        'AKo', 'AQo', 'AJo', 'ATo', 'A9o', 'A8o', 'A7o', 'A6o', 'A5o', 'A4o', 'A3o', 'A2o',
        'KQo', 'KJo', 'KTo', 'K9o', 'K8o', 'K7o', 'K6o', 'K5o', 'K4o', 'K3o', 'K2o',
        'QJo', 'QTo', 'Q9o', 'Q8o', 'Q7o', 'Q6o', 'Q5o', 'Q4o', 'Q3o', 'Q2o',
        'JTo', 'J9o', 'J8o', 'J7o', 'J6o', 'J5o', 'J4o', 'J3o', 'J2o',
        'T9o', 'T8o', 'T7o', 'T6o', 'T5o', 'T4o', 'T3o', 'T2o',
        '98o', '97o', '96o', '95o', '94o', '93o', '92o',
        '87o', '86o', '85o', '84o', '83o', '82o',
        '76o', '74o', '73o', '72o',
        '65o', '64o', '63o', '62o',
        '54o', '53o', '52o',
        '43o', '42o',
        '32o'
    ]
    
    wins = 0
    total_comparisons = 0
    simulations_per_hand = 100  # reduced from 400 for performance
    
    # get hero hand notation
    card1, card2 = hero_hand
    if card1.value == card2.value:
        hero_notation = f"{card1.rank}{card2.rank}"
    elif card1.suit == card2.suit:
        if card1.value > card2.value:
            hero_notation = f"{card1.rank}{card2.rank}s"
        else:
            hero_notation = f"{card2.rank}{card1.rank}s"
    else:
        if card1.value > card2.value:
            hero_notation = f"{card1.rank}{card2.rank}o"
        else:
            hero_notation = f"{card2.rank}{card1.rank}o"
    
    # skip if hero hand is not in our list
    if hero_notation not in all_hands:
        return 0.0
    
    # simulate against every other hand
    for opponent_hand in all_hands:
        if opponent_hand == hero_notation:
            continue
            
        # run simulations for this matchup
        for _ in range(simulations_per_hand):
            # create a random board (5 cards)
            deck = equity_calculator._create_deck([hero_hand[0], hero_hand[1]], [])
            board = []
            
            # deal 5 board cards
            for _ in range(5):
                if deck:
                    board.append(deck.pop(random.randint(0, len(deck) - 1)))
            
            # get opponent's specific cards for this hand type
            opponent_cards = _get_hand_cards(opponent_hand, [hero_hand[0], hero_hand[1]] + board)
            if not opponent_cards:
                continue
                
            # evaluate both hands
            hero_best = equity_calculator._get_best_hand(hero_hand, board)
            opponent_best = equity_calculator._get_best_hand(opponent_cards, board)
            
            # compare hands
            comparison = equity_calculator._compare_hands(hero_best, opponent_best, hero_hand, opponent_cards, board)
            if comparison > 0:
                wins += 1
            elif comparison == 0:
                wins += 0.5  # tie
                
            total_comparisons += 1
    
    if total_comparisons == 0:
        return 0.0
        
    win_rate = wins / total_comparisons
    return round(win_rate * 100, 1)

def _get_recommendation(hand_analysis: dict, preflop_action: str, pot_odds: float, board_cards: int) -> str:
    """Get a simple recommendation based on hand strength and pot odds"""
    strength = hand_analysis.get('strength', 0)
    
    # Preflop recommendations
    if board_cards == 0:
        if preflop_action == 'RAISE':
            return 'RAISE'
        elif preflop_action == 'CALL':
            return 'CALL'
        else:
            return 'FOLD'
    
    # Postflop recommendations based on hand type
    hand_type = hand_analysis.get('hand_type', '')
    
    if hand_type in ['royal_flush', 'straight_flush', 'four_kind']:
        return 'BET/RAISE'
    elif hand_type in ['full_house', 'flush', 'straight', 'three_kind']:
        return 'BET/RAISE'
    elif hand_type in ['two_pair']:
        return 'BET/CALL'
    elif hand_type in ['pair']:
        if pot_odds < 0.3:
            return 'CALL'
        else:
            return 'FOLD'
    else:  # high_card
        if pot_odds < 0.2:
            return 'CALL'
        else:
            return 'FOLD'
