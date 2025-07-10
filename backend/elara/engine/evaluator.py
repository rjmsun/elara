"""
Hand evaluation for Elara poker engine.

Uses eval7 library for high-performance hand evaluation while maintaining
compatibility with our Card class representation.
"""

import eval7
from .card import Card

class HandEvaluator:
    """
    Provides both raw hand strength evaluation and human-readable hand type
    classification. The eval7 library ensures optimal performance for equity
    calculations requiring millions of hand evaluations.
    """
    
    def __init__(self):
        """Initialize the hand evaluator."""
        pass
    
    def evaluate_hand(self, hand_cards):
        """
        Evaluate a 5-7 card hand and return its strength.
        Args:
            hand_cards: List of Card objects or card strings
        Returns:
            int: Numerical value representing hand strength (lower is better)
        """
        # Convert our Card objects to eval7.Card objects
        eval7_cards = []
        for card in hand_cards:
            if isinstance(card, Card):
                eval7_cards.append(eval7.Card(str(card)))
            elif isinstance(card, str):
                eval7_cards.append(eval7.Card(card))
            else:
                raise ValueError(f"Invalid card type: {type(card)}")
        
        # eval7.evaluate returns a numerical rank where lower is better
        return eval7.evaluate(eval7_cards)
    
    def get_hand_type(self, hand_strength_value):
        """
        Convert a numerical hand strength value to a human-readable string.
        
        Args:
            hand_strength_value: Integer from evaluate_hand()
            
        Returns:
            str: Human-readable hand type (e.g., "Royal Flush", "Two Pair")
        """
        return eval7.handtype(hand_strength_value)
    
    def compare_hands(self, hand1_cards, hand2_cards, board_cards=None):
        """
        Compare two hands and determine the winner.
        
        Args:
            hand1_cards: List of Card objects for first hand
            hand2_cards: List of Card objects for second hand
            board_cards: Optional list of community cards
            
        Returns:
            dict: Contains 'winner' (1, 2, or 0 for tie), 'hand1_strength', 'hand2_strength'
        """
        if board_cards is None:
            board_cards = []
        
        # Evaluate both hands
        hand1_strength = self.evaluate_hand(hand1_cards + board_cards)
        hand2_strength = self.evaluate_hand(hand2_cards + board_cards)
        
        # Determine winner (lower strength value is better)
        if hand1_strength < hand2_strength:
            winner = 1
        elif hand2_strength < hand1_strength:
            winner = 2
        else:
            winner = 0  # Tie
        
        return {
            'winner': winner,
            'hand1_strength': hand1_strength,
            'hand2_strength': hand2_strength,
            'hand1_type': self.get_hand_type(hand1_strength),
            'hand2_type': self.get_hand_type(hand2_strength)
        }
    
    def get_best_hand(self, hole_cards, board_cards):
        """
        Find the best 5-card hand from hole cards and board.
        
        Args:
            hole_cards: List of 2 Card objects (player's hole cards)
            board_cards: List of 3-5 Card objects (community cards)
            
        Returns:
            dict: Contains 'strength', 'type', and 'best_cards'
        """
        all_cards = hole_cards + board_cards
        strength = self.evaluate_hand(all_cards)
        
        return {
            'strength': strength,
            'type': self.get_hand_type(strength),
            'best_cards': all_cards  # eval7 automatically finds best 5-card combination
        }
    
    def is_hand_complete(self, hole_cards, board_cards):
        """
        Check if a hand is complete (has 5 or more cards total).
        
        Args:
            hole_cards: List of Card objects
            board_cards: List of Card objects
            
        Returns:
            bool: True if hand has 5+ cards
        """
        return len(hole_cards) + len(board_cards) >= 5 