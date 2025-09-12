"""
GTO Strategy implementation for Elara poker engine.

Implements pre-flop decision making based on GTO charts and position.
"""

import json
import os
from ..engine.card import Card
from ..giffer.range_handler import Range

class GtoStrategy:
    """
    GTO-based strategy implementation for pre-flop decision making.
    
    This class loads pre-computed GTO charts and provides decision logic
    for pre-flop actions based on position and hole cards.
    """
    
    def __init__(self):
        """Initialize the GTO strategy with pre-flop charts."""
        self.charts = self._load_preflop_charts()
    
    def _load_preflop_charts(self):
        """
        Load pre-flop charts from JSON file.
        
        Returns:
            dict: Pre-flop charts data
        """
        charts_path = os.path.join(os.path.dirname(__file__), 'preflop_charts.json')
        try:
            with open(charts_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to default charts if file not found
            return self._get_default_charts()
    
    def _get_default_charts(self):
        """Get default pre-flop charts as fallback."""
        return {
            "UTG": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "AKs", "AQs", "AJs", "ATs", "AKo", "AQo"],
                "call": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AQs", "AJs", "AKo", "AQo"],
                "3bet": ["AA", "KK", "QQ", "JJ", "AKs", "AKo"]
            },
            "BTN": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o", "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s", "KQo", "KJo", "KTo", "K9o", "K8o", "K7o", "K6o", "K5o", "K4o", "K3o", "K2o", "QJs", "QTs", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s", "QJo", "QTo", "Q9o", "Q8o", "Q7o", "Q6o", "Q5o", "Q4o", "Q3o", "Q2o", "JTs", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s", "JTo", "J9o", "J8o", "J7o", "J6o", "J5o", "J4o", "J3o", "J2o", "T9s", "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s", "T9o", "T8o", "T7o", "T6o", "T5o", "T4o", "T3o", "T2o", "98s", "97s", "96s", "95s", "94s", "93s", "92s", "98o", "97o", "96o", "95o", "94o", "93o", "92o", "87s", "86s", "85s", "84s", "83s", "82s", "87o", "86o", "85o", "84o", "83o", "82o", "76s", "75s", "74s", "73s", "72s", "76o", "75o", "74o", "73o", "72o", "65s", "64s", "63s", "62s", "65o", "64o", "63o", "62o", "54s", "53s", "52s", "54o", "53o", "52o", "43s", "42s", "43o", "42o", "32s", "32o"],
                "call": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o", "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s", "KQo", "KJo", "KTo", "K9o", "K8o", "K7o", "K6o", "K5o", "K4o", "K3o", "K2o", "QJs", "QTs", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s", "QJo", "QTo", "Q9o", "Q8o", "Q7o", "Q6o", "Q5o", "Q4o", "Q3o", "Q2o", "JTs", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s", "JTo", "J9o", "J8o", "J7o", "J6o", "J5o", "J4o", "J3o", "J2o", "T9s", "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s", "T9o", "T8o", "T7o", "T6o", "T5o", "T4o", "T3o", "T2o", "98s", "97s", "96s", "95s", "94s", "93s", "92s", "98o", "97o", "96o", "95o", "94o", "93o", "92o", "87s", "86s", "85s", "84s", "83s", "82s", "87o", "86o", "85o", "84o", "83o", "82o", "76s", "75s", "74s", "73s", "72s", "76o", "75o", "74o", "73o", "72o", "65s", "64s", "63s", "62s", "65o", "64o", "63o", "62o", "54s", "53s", "52s", "54o", "53o", "52o", "43s", "42s", "43o", "42o", "32s", "32o"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "AKs", "AKo", "AQo", "AJo", "KQs", "KQo"]
            },
            "BB": {
                "defend": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o", "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s", "KQo", "KJo", "KTo", "K9o", "K8o", "K7o", "K6o", "K5o", "K4o", "K3o", "K2o", "QJs", "QTs", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s", "QJo", "QTo", "Q9o", "Q8o", "Q7o", "Q6o", "Q5o", "Q4o", "Q3o", "Q2o", "JTs", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s", "JTo", "J9o", "J8o", "J7o", "J6o", "J5o", "J4o", "J3o", "J2o", "T9s", "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s", "T9o", "T8o", "T7o", "T6o", "T5o", "T4o", "T3o", "T2o", "98s", "97s", "96s", "95s", "94s", "93s", "92s", "98o", "97o", "96o", "95o", "94o", "93o", "92o", "87s", "86s", "85s", "84s", "83s", "82s", "87o", "86o", "85o", "84o", "83o", "82o", "76s", "75s", "74s", "73s", "72s", "76o", "75o", "74o", "73o", "72o", "65s", "64s", "63s", "62s", "65o", "64o", "63o", "62o", "54s", "53s", "52s", "54o", "53o", "52o", "43s", "42s", "43o", "42o", "32s", "32o"],
                "call": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22", "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o", "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s", "KQo", "KJo", "KTo", "K9o", "K8o", "K7o", "K6o", "K5o", "K4o", "K3o", "K2o", "QJs", "QTs", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s", "QJo", "QTo", "Q9o", "Q8o", "Q7o", "Q6o", "Q5o", "Q4o", "Q3o", "Q2o", "JTs", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s", "JTo", "J9o", "J8o", "J7o", "J6o", "J5o", "J4o", "J3o", "J2o", "T9s", "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s", "T9o", "T8o", "T7o", "T6o", "T5o", "T4o", "T3o", "T2o", "98s", "97s", "96s", "95s", "94s", "93s", "92s", "98o", "97o", "96o", "95o", "94o", "93o", "92o", "87s", "86s", "85s", "84s", "83s", "82s", "87o", "86o", "85o", "84o", "83o", "82o", "76s", "75s", "74s", "73s", "72s", "76o", "75o", "74o", "73o", "72o", "65s", "64s", "63s", "62s", "65o", "64o", "63o", "62o", "54s", "53s", "52s", "54o", "53o", "52o", "43s", "42s", "43o", "42o", "32s", "32o"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "AKs", "AKo", "AQo", "AJo", "KQs", "KQo"]
            }
        }
    
    def get_preflop_action(self, position, hole_cards):
        """
        Get pre-flop action recommendation based on position and hole cards.
        
        Args:
            position: Player position ('UTG', 'HJ', 'CO', 'BTN', 'SB', 'BB')
            hole_cards: List of 2 Card objects
            
        Returns:
            str: Action recommendation ('RAISE', 'CALL', 'FOLD')
        """
        if len(hole_cards) != 2:
            return 'FOLD'
        
        # Convert hole cards to string format
        hand_str = self._cards_to_hand_string(hole_cards)
        
        # Get the appropriate range for the position
        if position not in self.charts:
            return 'FOLD'
        
        position_charts = self.charts[position]
        
        # Check if hand is in the opening range
        if 'open' in position_charts and hand_str in position_charts['open']:
            return 'RAISE'
        
        # Check if hand is in the calling range
        if 'call' in position_charts and hand_str in position_charts['call']:
            return 'CALL'
        
        # Check if hand is in the 3bet range
        if '3bet' in position_charts and hand_str in position_charts['3bet']:
            return 'RAISE'
        
        # Check if hand is in the defend range (for BB)
        if 'defend' in position_charts and hand_str in position_charts['defend']:
            return 'CALL'
        
        return 'FOLD'
    
    def _cards_to_hand_string(self, hole_cards):
        """
        Convert hole cards to standard poker notation.
        
        Args:
            hole_cards: List of 2 Card objects
            
        Returns:
            str: Hand string (e.g., 'AKs', 'QQ', 'T9o')
        """
        if len(hole_cards) != 2:
            return ''
        
        card1, card2 = hole_cards
        
        # Pocket pair
        if card1.rank == card2.rank:
            return f"{card1.rank}{card2.rank}"
        
        # Suited or offsuit
        rank1, rank2 = card1.rank, card2.rank
        
        # Ensure higher rank comes first
        if card1.val < card2.val:  # Lower val is higher rank
            rank1, rank2 = rank2, rank1
        
        # Check if suited
        if card1.suit == card2.suit:
            return f"{rank1}{rank2}s"
        else:
            return f"{rank1}{rank2}o"
    
    def get_range_for_position(self, position, action_type):
        """
        Get the range for a specific position and action type.
        
        Args:
            position: Player position
            action_type: Type of action ('open', 'call', '3bet', 'defend')
            
        Returns:
            list: List of hands in the range
        """
        if position not in self.charts:
            return []
        
        position_charts = self.charts[position]
        if action_type not in position_charts:
            return []
        
        return position_charts[action_type]
    
    def get_range_coverage(self, position, action_type):
        """
        Get the percentage of hands covered by a range.
        
        Args:
            position: Player position
            action_type: Type of action
            
        Returns:
            float: Percentage of hands (0.0 to 1.0)
        """
        range_hands = self.get_range_for_position(position, action_type)
        if not range_hands:
            return 0.0
        
        # Create a Range object to get the total number of combos
        range_obj = Range.from_hand_list(range_hands)
        total_combos = len(range_obj.expand_to_combos())
        
        # Total possible starting hands is 1326
        return total_combos / 1326.0 