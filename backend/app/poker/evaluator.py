from typing import List, Dict, Any
from .card import Card

# hand evaluator - figures out what kind of hand you have
class HandEvaluator:
    def __init__(self):
        self.hand_rankings = {
            'high_card': 1, 'pair': 2, 'two_pair': 3, 'three_kind': 4,
            'straight': 5, 'flush': 6, 'full_house': 7, 'four_kind': 8,
            'straight_flush': 9, 'royal_flush': 10
        }
    
    def evaluate_hand(self, cards: List[Card]) -> Dict[str, Any]:
        """Evaluate a 5-card hand and return its strength"""
        if len(cards) != 5:
            return {'error': 'Need exactly 5 cards'}
        
        # Sort cards by value
        sorted_cards = sorted(cards, key=lambda x: x.value, reverse=True)
        
        # Check for different hand types
        hand_type, strength = self._get_hand_type(sorted_cards)
        
        return {
            'hand_type': hand_type,
            'strength': strength,
            'cards': [str(card) for card in sorted_cards]
        }
    
    def _get_hand_type(self, cards: List[Card]) -> tuple:
        """Determine hand type and calculate strength"""
        values = [card.value for card in cards]
        suits = [card.suit for card in cards]
        
        # Count occurrences of each value
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        counts = sorted(value_counts.values(), reverse=True)
        is_flush = len(set(suits)) == 1
        is_straight = self._is_straight(values)
        
        # Determine hand type with proper ranking
        if is_straight and is_flush:
            if min(values) == 10:  # Royal flush (A, K, Q, J, 10)
                return 'royal_flush', 10
            else:
                return 'straight_flush', 9
        elif counts == [4, 1]:
            return 'four_kind', 8
        elif counts == [3, 2]:
            return 'full_house', 7
        elif is_flush:
            return 'flush', 6
        elif is_straight:
            return 'straight', 5
        elif counts == [3, 1, 1]:
            return 'three_kind', 4
        elif counts == [2, 2, 1]:
            return 'two_pair', 3
        elif counts == [2, 1, 1, 1]:
            return 'pair', 2
        else:
            return 'high_card', 1
    
    def _is_straight(self, values: List[int]) -> bool:
        """Check if values form a straight"""
        sorted_values = sorted(set(values))
        if len(sorted_values) != 5:
            return False
        
        # Check for regular straight
        if sorted_values[-1] - sorted_values[0] == 4:
            return True
        
        # Check for A-2-3-4-5 straight
        if sorted_values == [2, 3, 4, 5, 14]:
            return True
        
        return False
    
    def get_hand_category(self, hole_cards: List[Card], board: List[Card]) -> str:
        """Provides a detailed category of a hand's connection to the board."""
        if len(board) < 3:
            return "PREFLOP"

        # --- Board Analysis ---
        board_ranks = [c.value for c in board]
        board_suits = [c.suit for c in board]
        top_board_card = max(board_ranks) if board_ranks else 0
        is_board_paired = len(set(board_ranks)) < len(board_ranks)

        # --- Hand Analysis ---
        best_hand_result = self._get_best_hand(hole_cards, board)
        hand_type = best_hand_result['hand_type']
        hole_ranks = [c.value for c in hole_cards]

        # --- Made Hand Categories (strongest first) ---
        if hand_type in ['straight_flush', 'four_kind', 'full_house', 'flush', 'straight']:
            return "NUT_MADE_HAND"

        if hand_type == 'three_kind':
            # Check if it's a set (pocket pair) or trips
            if hole_cards[0].value == hole_cards[1].value:
                return "SET"
            else:
                return "TRIPS"

        if hand_type == 'two_pair':
            # Check if using both hole cards
            if hole_ranks[0] in board_ranks and hole_ranks[1] in board_ranks:
                return "TWO_PAIR"
            else: # Using one hole card and a pair on the board
                return "ONE_CARD_TWO_PAIR"

        if hand_type == 'pair':
            # Overpair: Pocket pair higher than the board's highest card
            if hole_cards[0].value == hole_cards[1].value and hole_cards[0].value > top_board_card:
                return "OVERPAIR"
            # Top Pair
            if max(hole_ranks) == top_board_card:
                return "TOP_PAIR"
            # Middle/Bottom Pair
            return "MID_WEAK_PAIR"

        # --- Drawing Hand Categories ---
        all_cards = hole_cards + board
        all_suits = [c.suit for c in all_cards]
        # Flush Draw
        from collections import Counter
        if any(count == 4 for count in Counter(all_suits).values()):
            return "FLUSH_DRAW"

        # Straight Draw (implement a helper for this)
        if self._is_straight_draw(all_cards):
            return "STRAIGHT_DRAW"

        # --- No Connection ---
        return "NO_MADE_HAND_OR_DRAW"
    
    def _get_best_hand(self, hole_cards: List[Card], board: List[Card]) -> Dict[str, Any]:
        """Get the best 5-card hand from hole cards and board"""
        from itertools import combinations
        
        all_cards = hole_cards + board
        if len(all_cards) < 5:
            return {'hand_type': 'incomplete', 'strength': 0}
        
        best_hand = None
        best_strength = 0
        
        for combo in combinations(all_cards, 5):
            hand_result = self.evaluate_hand(list(combo))
            if hand_result['strength'] > best_strength:
                best_strength = hand_result['strength']
                best_hand = hand_result
        
        return best_hand if best_hand else {'hand_type': 'incomplete', 'strength': 0}
    
    def _is_straight_draw(self, cards: List[Card]) -> bool:
        """Check if cards contain a straight draw"""
        values = [c.value for c in cards]
        unique_values = sorted(set(values))
        
        # Check for 4-card straight draws
        for i in range(len(unique_values) - 3):
            if unique_values[i+3] - unique_values[i] == 3:
                return True
        
        # Check for gutshot draws (3 cards with 1 gap)
        for i in range(len(unique_values) - 2):
            if unique_values[i+2] - unique_values[i] == 4:
                return True
        
        return False
