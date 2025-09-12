from typing import List
from .card import Card
from .evaluator import HandEvaluator
from .equity import EquityCalculator

def filter_range_for_board(preflop_range: List[str], board: List[Card], player_profile='tight') -> List[str]:
    """
    Filters a preflop range down to a likely postflop range based on board texture.
    """
    hand_evaluator = HandEvaluator()
    equity_calculator = EquityCalculator()

    # Define what a 'tight' player continues with. You can add more profiles.
    tight_continue_categories = {
        "NUT_MADE_HAND", "SET", "TRIPS", "TWO_PAIR", "OVERPAIR", "TOP_PAIR",
        "FLUSH_DRAW", "STRAIGHT_DRAW"  # A tight player still chases good draws
    }
    
    postflop_range = []

    for hand_notation in preflop_range:
        # Generate the specific card combos for this notation (e.g., AA -> AsAh, AsAc...)
        hand_combos = equity_calculator._generate_all_combinations(hand_notation)

        for combo in hand_combos:
            if equity_calculator._cards_conflict(combo, board):
                continue
            
            # Get the detailed category for this specific hand on this board
            category = hand_evaluator.get_hand_category(combo, board)

            # The CORE LOGIC: Check if the category is one we expect to continue
            if category in tight_continue_categories:
                # If it's a hand they'd play, we keep its notation in the new range
                if hand_notation not in postflop_range:
                    postflop_range.append(hand_notation)
                break  # Move to the next hand notation (e.g., from AA to KK)

    return postflop_range

def partition_range(villain_range: List[str], board: List[Card]) -> dict:
    """
    Partitions a villain's range into strategic categories based on board texture.
    """
    hand_evaluator = HandEvaluator()
    equity_calculator = EquityCalculator()
    
    categories = {
        "value": 0, 
        "marginal": 0, 
        "flush_draw": 0, 
        "straight_draw": 0, 
        "bluff_air": 0
    }
    total_combos = 0

    for hand_notation in villain_range:
        # Generate all possible combinations for this hand type
        hand_combos = equity_calculator._generate_all_combinations(hand_notation)
        
        for combo in hand_combos:
            # Skip combos that conflict with the board
            if equity_calculator._cards_conflict(combo, board):
                continue

            # Get the detailed category for this specific hand on this board
            category = hand_evaluator.get_hand_category(combo, board)
            
            # Map detailed categories to strategic categories
            if category in ["NUT_MADE_HAND", "SET", "TRIPS", "TWO_PAIR", "OVERPAIR"]:
                categories["value"] += 1
            elif category in ["TOP_PAIR", "MID_WEAK_PAIR"]:
                categories["marginal"] += 1
            elif category == "FLUSH_DRAW":
                categories["flush_draw"] += 1
            elif category == "STRAIGHT_DRAW":
                categories["straight_draw"] += 1
            else:  # NO_MADE_HAND_OR_DRAW, etc.
                categories["bluff_air"] += 1
            
            total_combos += 1

    # Convert counts to percentages
    for category in categories:
        categories[category] = round((categories[category] / total_combos) * 100, 2) if total_combos > 0 else 0

    return categories
