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

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import json
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)

# card class - just holds rank, suit, and value
class Card:
    def __init__(self, card_str: str):
        # parse the card string like "As" or "Kh"
        self.rank = card_str[:-1]
        self.suit = card_str[-1]
        self.value = self._get_value()
    
    def _get_value(self):
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return rank_values.get(self.rank, 0)
    
    def __str__(self):
        return f"{self.rank}{self.suit}"

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

# equity calculator - runs monte carlo simulations to see how often you win
class EquityCalculator:
    def __init__(self):
        self.evaluator = HandEvaluator()
    
    def calculate_equity(self, hero_hand: List[Card], villain_range: List[str], 
                        board: List[Card] = None, simulations: int = 1000) -> float:
        """runs a bunch of simulations to see how often you win"""
        if board is None:
            board = []
        
        wins = 0
        total = 0
        
        # Generate all possible villain hands from range
        all_villain_hands = []
        for hand_str in villain_range:
            villain_hands = self._generate_all_combinations(hand_str)
            all_villain_hands.extend(villain_hands)
        
        if not all_villain_hands:
            return 0.0
        
        # Run simulations
        for _ in range(simulations):
            # Pick a random villain hand from all possible combinations
            villain_hand = random.choice(all_villain_hands)
            
            # Check if villain hand conflicts with known cards
            if self._cards_conflict(villain_hand, hero_hand + board):
                continue
            
            # Create a fresh deck excluding ALL known cards (hero + villain + board)
            deck = self._create_deck(hero_hand + villain_hand, board)
            random.shuffle(deck)
            
            # Complete the board
            remaining_board = 5 - len(board)
            full_board = board + deck[:remaining_board]
            
            # Evaluate hands
            hero_best = self._get_best_hand(hero_hand, full_board)
            villain_best = self._get_best_hand(villain_hand, full_board)
            
            # Compare hands with proper tie-breaking
            result = self._compare_hands(hero_best, villain_best, hero_hand, villain_hand, full_board)
            if result > 0:
                wins += 1
            elif result == 0:
                wins += 0.5
            
            total += 1
        
        return wins / total if total > 0 else 0.0
    
    def _generate_all_combinations(self, hand_str: str) -> List[List[Card]]:
        """Generate all possible card combinations for a hand string"""
        combinations = []
        
        try:
            if len(hand_str) == 2:  # Pair like 'AA'
                rank = hand_str[0]
                suits = ['s', 'h', 'd', 'c']
                # Generate all 6 possible pair combinations
                for i in range(len(suits)):
                    for j in range(i + 1, len(suits)):
                        combinations.append([Card(f"{rank}{suits[i]}"), Card(f"{rank}{suits[j]}")])
            
            elif len(hand_str) == 4:  # Two specific cards like 'AsKh'
                combinations.append([Card(hand_str[:2]), Card(hand_str[2:])])
            
            elif len(hand_str) == 3:  # Suited/offsuit like 'AKs' or 'AKo'
                rank1, rank2 = hand_str[0], hand_str[1]
                if hand_str.endswith('s'):  # Suited
                    suits = ['s', 'h', 'd', 'c']
                    for suit in suits:
                        combinations.append([Card(f"{rank1}{suit}"), Card(f"{rank2}{suit}")])
                elif hand_str.endswith('o'):  # Offsuit
                    suits = ['s', 'h', 'd', 'c']
                    for i in range(len(suits)):
                        for j in range(len(suits)):
                            if suits[i] != suits[j]:  # Different suits
                                combinations.append([Card(f"{rank1}{suits[i]}"), Card(f"{rank2}{suits[j]}")])
        
        except Exception as e:
            print(f"Error generating combinations for {hand_str}: {e}")
        
        return combinations
    
    def _parse_hand(self, hand_str: str) -> List[Card]:
        """Parse hand string like 'AsKh' or 'AA' into Card objects"""
        try:
            if len(hand_str) == 2:  # Pair like 'AA'
                rank = hand_str[0]
                # Return all possible combinations for pairs
                return [Card(f"{rank}s"), Card(f"{rank}h"), Card(f"{rank}d"), Card(f"{rank}c")]
            elif len(hand_str) == 4:  # Two cards like 'AsKh'
                return [Card(hand_str[:2]), Card(hand_str[2:])]
            elif len(hand_str) == 3:  # Suited hand like 'AKs'
                if hand_str.endswith('s'):
                    rank1, rank2 = hand_str[0], hand_str[1]
                    return [Card(f"{rank1}s"), Card(f"{rank2}s")]
                elif hand_str.endswith('o'):
                    rank1, rank2 = hand_str[0], hand_str[1]
                    return [Card(f"{rank1}s"), Card(f"{rank2}h")]
            return []
        except:
            return []
    
    def _cards_conflict(self, hand1: List[Card], hand2: List[Card]) -> bool:
        """Check if two hands share any cards"""
        for card1 in hand1:
            for card2 in hand2:
                if str(card1) == str(card2):
                    return True
        return False
    
    def _create_deck(self, known_cards: List[Card], board: List[Card]) -> List[Card]:
        """Create a deck excluding known cards"""
        all_cards = []
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['s', 'h', 'd', 'c']
        
        for rank in ranks:
            for suit in suits:
                card = Card(f"{rank}{suit}")
                if not self._cards_conflict([card], known_cards + board):
                    all_cards.append(card)
        
        return all_cards
    
    def _get_best_hand(self, hole_cards: List[Card], board: List[Card]) -> Dict[str, Any]:
        """Get the best 5-card hand from hole cards and board"""
        all_cards = hole_cards + board
        if len(all_cards) < 5:
            return {'strength': 0, 'hand_type': 'incomplete'}
        
        # Try all combinations of 5 cards
        best_hand = None
        best_strength = 0
        
        from itertools import combinations
        for combo in combinations(all_cards, 5):
            hand_result = self.evaluator.evaluate_hand(list(combo))
            if hand_result['strength'] > best_strength:
                best_strength = hand_result['strength']
                best_hand = hand_result
        
        return best_hand or {'strength': 0, 'hand_type': 'incomplete'}
    
    def _compare_hands(self, hero_hand: Dict, villain_hand: Dict, hero_cards: List[Card], 
                      villain_cards: List[Card], board: List[Card]) -> int:
        """Compare two hands and return 1 if hero wins, -1 if villain wins, 0 if tie"""
        hero_strength = hero_hand['strength']
        villain_strength = villain_hand['strength']
        
        # Different hand types - higher strength wins
        if hero_strength > villain_strength:
            return 1
        elif hero_strength < villain_strength:
            return -1
        
        # Same hand type - need to compare kickers
        hero_type = hero_hand['hand_type']
        villain_type = villain_hand['hand_type']
        
        if hero_type != villain_type:
            return 0  # Shouldn't happen, but safety check
        
        # Get the best 5-card hands for both players
        hero_best_5 = self._get_best_5_cards(hero_cards, board)
        villain_best_5 = self._get_best_5_cards(villain_cards, board)
        
        # Compare based on hand type
        if hero_type == 'pair':
            return self._compare_pairs(hero_best_5, villain_best_5)
        elif hero_type == 'two_pair':
            return self._compare_two_pairs(hero_best_5, villain_best_5)
        elif hero_type == 'three_kind':
            return self._compare_three_of_a_kind(hero_best_5, villain_best_5)
        elif hero_type == 'straight':
            return self._compare_straights(hero_best_5, villain_best_5)
        elif hero_type == 'flush':
            return self._compare_flushes(hero_best_5, villain_best_5)
        elif hero_type == 'full_house':
            return self._compare_full_houses(hero_best_5, villain_best_5)
        elif hero_type == 'four_kind':
            return self._compare_four_of_a_kind(hero_best_5, villain_best_5)
        elif hero_type in ['straight_flush', 'royal_flush']:
            return self._compare_straights(hero_best_5, villain_best_5)
        else:  # high_card
            return self._compare_high_cards(hero_best_5, villain_best_5)
    
    def _get_best_5_cards(self, hole_cards: List[Card], board: List[Card]) -> List[Card]:
        """Get the best 5-card combination from hole cards and board"""
        all_cards = hole_cards + board
        if len(all_cards) < 5:
            return all_cards
        
        best_hand = None
        best_strength = 0
        
        from itertools import combinations
        for combo in combinations(all_cards, 5):
            hand_result = self.evaluator.evaluate_hand(list(combo))
            if hand_result['strength'] > best_strength:
                best_strength = hand_result['strength']
                best_hand = list(combo)
        
        return best_hand or all_cards[:5]
    
    def _compare_pairs(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare pair hands"""
        hero_values = sorted([c.value for c in hero_cards], reverse=True)
        villain_values = sorted([c.value for c in villain_cards], reverse=True)
        
        # Find the pair values
        hero_pair = None
        villain_pair = None
        
        for i in range(4):
            if hero_values[i] == hero_values[i+1]:
                hero_pair = hero_values[i]
                break
        
        for i in range(4):
            if villain_values[i] == villain_values[i+1]:
                villain_pair = villain_values[i]
                break
        
        if hero_pair > villain_pair:
            return 1
        elif hero_pair < villain_pair:
            return -1
        
        # Same pair, compare kickers
        hero_kickers = [v for v in hero_values if v != hero_pair]
        villain_kickers = [v for v in villain_values if v != villain_pair]
        
        for i in range(len(hero_kickers)):
            if hero_kickers[i] > villain_kickers[i]:
                return 1
            elif hero_kickers[i] < villain_kickers[i]:
                return -1
        
        return 0
    
    def _compare_high_cards(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare high card hands"""
        hero_values = sorted([c.value for c in hero_cards], reverse=True)
        villain_values = sorted([c.value for c in villain_cards], reverse=True)
        
        for i in range(5):
            if hero_values[i] > villain_values[i]:
                return 1
            elif hero_values[i] < villain_values[i]:
                return -1
        
        return 0
    
    def _compare_three_of_a_kind(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare three of a kind hands"""
        hero_values = sorted([c.value for c in hero_cards], reverse=True)
        villain_values = sorted([c.value for c in villain_cards], reverse=True)
        
        # Find the three of a kind values
        hero_trips = None
        villain_trips = None
        
        for i in range(3):
            if hero_values[i] == hero_values[i+1] == hero_values[i+2]:
                hero_trips = hero_values[i]
                break
        
        for i in range(3):
            if villain_values[i] == villain_values[i+1] == villain_values[i+2]:
                villain_trips = villain_values[i]
                break
        
        if hero_trips > villain_trips:
            return 1
        elif hero_trips < villain_trips:
            return -1
        
        # Same trips, compare kickers
        hero_kickers = [v for v in hero_values if v != hero_trips]
        villain_kickers = [v for v in villain_values if v != villain_trips]
        
        for i in range(len(hero_kickers)):
            if hero_kickers[i] > villain_kickers[i]:
                return 1
            elif hero_kickers[i] < villain_kickers[i]:
                return -1
        
        return 0
    
    def _compare_straights(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare straight hands"""
        hero_values = sorted([c.value for c in hero_cards], reverse=True)
        villain_values = sorted([c.value for c in villain_cards], reverse=True)
        
        # For straights, compare the highest card
        return self._compare_high_cards(hero_cards, villain_cards)
    
    def _compare_flushes(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare flush hands"""
        return self._compare_high_cards(hero_cards, villain_cards)
    
    def _compare_full_houses(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare full house hands"""
        hero_values = sorted([c.value for c in hero_cards], reverse=True)
        villain_values = sorted([c.value for c in villain_cards], reverse=True)
        
        # Find the three of a kind and pair values
        hero_trips = None
        hero_pair = None
        villain_trips = None
        villain_pair = None
        
        # Count occurrences
        hero_counts = {}
        villain_counts = {}
        for v in hero_values:
            hero_counts[v] = hero_counts.get(v, 0) + 1
        for v in villain_values:
            villain_counts[v] = villain_counts.get(v, 0) + 1
        
        for v, count in hero_counts.items():
            if count == 3:
                hero_trips = v
            elif count == 2:
                hero_pair = v
        
        for v, count in villain_counts.items():
            if count == 3:
                villain_trips = v
            elif count == 2:
                villain_pair = v
        
        # Compare trips first
        if hero_trips > villain_trips:
            return 1
        elif hero_trips < villain_trips:
            return -1
        
        # Same trips, compare pairs
        if hero_pair > villain_pair:
            return 1
        elif hero_pair < villain_pair:
            return -1
        
        return 0
    
    def _compare_four_of_a_kind(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare four of a kind hands"""
        hero_values = sorted([c.value for c in hero_cards], reverse=True)
        villain_values = sorted([c.value for c in villain_cards], reverse=True)
        
        # Find the four of a kind values
        hero_quads = None
        villain_quads = None
        
        for i in range(2):
            if hero_values[i] == hero_values[i+1] == hero_values[i+2] == hero_values[i+3]:
                hero_quads = hero_values[i]
                break
        
        for i in range(2):
            if villain_values[i] == villain_values[i+1] == villain_values[i+2] == villain_values[i+3]:
                villain_quads = villain_values[i]
                break
        
        if hero_quads > villain_quads:
            return 1
        elif hero_quads < villain_quads:
            return -1
        
        # Same quads, compare kicker
        hero_kicker = [v for v in hero_values if v != hero_quads][0]
        villain_kicker = [v for v in villain_values if v != villain_quads][0]
        
        if hero_kicker > villain_kicker:
            return 1
        elif hero_kicker < villain_kicker:
            return -1
        
        return 0
    
    def _compare_two_pairs(self, hero_cards: List[Card], villain_cards: List[Card]) -> int:
        """Compare two pair hands"""
        hero_values = sorted([c.value for c in hero_cards], reverse=True)
        villain_values = sorted([c.value for c in villain_cards], reverse=True)
        
        # Find the pair values
        hero_pairs = []
        villain_pairs = []
        
        for i in range(4):
            if hero_values[i] == hero_values[i+1] and hero_values[i] not in hero_pairs:
                hero_pairs.append(hero_values[i])
        
        for i in range(4):
            if villain_values[i] == villain_values[i+1] and villain_values[i] not in villain_pairs:
                villain_pairs.append(villain_values[i])
        
        hero_pairs.sort(reverse=True)
        villain_pairs.sort(reverse=True)
        
        # Compare higher pair
        if hero_pairs[0] > villain_pairs[0]:
            return 1
        elif hero_pairs[0] < villain_pairs[0]:
            return -1
        
        # Compare lower pair
        if hero_pairs[1] > villain_pairs[1]:
            return 1
        elif hero_pairs[1] < villain_pairs[1]:
            return -1
        
        # Compare kicker
        hero_kicker = [v for v in hero_values if v not in hero_pairs][0]
        villain_kicker = [v for v in villain_values if v not in villain_pairs][0]
        
        if hero_kicker > villain_kicker:
            return 1
        elif hero_kicker < villain_kicker:
            return -1
        
        return 0

# preflop strategy - tells you whether to raise, call, or fold preflop
class PreflopStrategy:
    def __init__(self):
        self.preflop_charts = {
            'SB': {  # Small Blind (heads up) - more aggressive range
                'AA': 'RAISE', 'KK': 'RAISE', 'QQ': 'RAISE', 'JJ': 'RAISE', 'TT': 'RAISE', '99': 'RAISE', '88': 'RAISE', '77': 'RAISE', '66': 'RAISE', '55': 'RAISE', '44': 'RAISE', '33': 'RAISE', '22': 'RAISE',
                'AKs': 'RAISE', 'AQs': 'RAISE', 'AJs': 'RAISE', 'ATs': 'RAISE', 'A9s': 'RAISE', 'A8s': 'RAISE', 'A7s': 'RAISE', 'A6s': 'RAISE', 'A5s': 'RAISE', 'A4s': 'RAISE', 'A3s': 'RAISE', 'A2s': 'RAISE',
                'AKo': 'RAISE', 'AQo': 'RAISE', 'AJo': 'RAISE', 'ATo': 'RAISE', 'A9o': 'RAISE', 'A8o': 'RAISE', 'A7o': 'RAISE', 'A6o': 'RAISE', 'A5o': 'RAISE', 'A4o': 'RAISE', 'A3o': 'RAISE', 'A2o': 'RAISE',
                'KQs': 'RAISE', 'KJs': 'RAISE', 'KTs': 'RAISE', 'K9s': 'RAISE', 'K8s': 'RAISE', 'K7s': 'RAISE', 'K6s': 'RAISE', 'K5s': 'RAISE', 'K4s': 'RAISE', 'K3s': 'RAISE', 'K2s': 'RAISE',
                'KQo': 'RAISE', 'KJo': 'RAISE', 'KTo': 'RAISE', 'K9o': 'RAISE', 'K8o': 'RAISE', 'K7o': 'RAISE', 'K6o': 'RAISE', 'K5o': 'RAISE', 'K4o': 'RAISE', 'K3o': 'RAISE', 'K2o': 'RAISE',
                'QJs': 'RAISE', 'QTs': 'RAISE', 'Q9s': 'RAISE', 'Q8s': 'RAISE', 'Q7s': 'RAISE', 'Q6s': 'RAISE', 'Q5s': 'RAISE', 'Q4s': 'RAISE', 'Q3s': 'RAISE', 'Q2s': 'RAISE',
                'QJo': 'RAISE', 'QTo': 'RAISE', 'Q9o': 'RAISE', 'Q8o': 'RAISE', 'Q7o': 'RAISE', 'Q6o': 'RAISE', 'Q5o': 'RAISE', 'Q4o': 'RAISE', 'Q3o': 'RAISE', 'Q2o': 'RAISE',
                'JTs': 'RAISE', 'J9s': 'RAISE', 'J8s': 'RAISE', 'J7s': 'RAISE', 'J6s': 'RAISE', 'J5s': 'RAISE', 'J4s': 'RAISE', 'J3s': 'RAISE', 'J2s': 'RAISE',
                'JTo': 'RAISE', 'J9o': 'RAISE', 'J8o': 'RAISE', 'J7o': 'RAISE', 'J6o': 'RAISE', 'J5o': 'RAISE', 'J4o': 'RAISE', 'J3o': 'RAISE', 'J2o': 'RAISE',
                'T9s': 'RAISE', 'T8s': 'RAISE', 'T7s': 'RAISE', 'T6s': 'RAISE', 'T5s': 'RAISE', 'T4s': 'RAISE', 'T3s': 'RAISE', 'T2s': 'RAISE',
                'T9o': 'RAISE', 'T8o': 'RAISE', 'T7o': 'RAISE', 'T6o': 'RAISE', 'T5o': 'RAISE', 'T4o': 'RAISE', 'T3o': 'RAISE', 'T2o': 'RAISE',
                '98s': 'RAISE', '97s': 'RAISE', '96s': 'RAISE', '95s': 'RAISE', '94s': 'RAISE', '93s': 'RAISE', '92s': 'RAISE',
                '98o': 'RAISE', '97o': 'RAISE', '96o': 'RAISE', '95o': 'RAISE', '94o': 'RAISE', '93o': 'RAISE', '92o': 'RAISE',
                '87s': 'RAISE', '86s': 'RAISE', '85s': 'RAISE', '84s': 'RAISE', '83s': 'RAISE', '82s': 'RAISE',
                '87o': 'RAISE', '86o': 'RAISE', '85o': 'RAISE', '84o': 'RAISE', '83o': 'RAISE', '82o': 'RAISE',
                '76s': 'RAISE', '75s': 'RAISE', '74s': 'RAISE', '73s': 'RAISE', '72s': 'RAISE',
                '76o': 'RAISE', '75o': 'RAISE', '74o': 'RAISE', '73o': 'RAISE', '72o': 'RAISE',
                '65s': 'RAISE', '64s': 'RAISE', '63s': 'RAISE', '62s': 'RAISE',
                '65o': 'RAISE', '64o': 'RAISE', '63o': 'RAISE', '62o': 'RAISE',
                '54s': 'RAISE', '53s': 'RAISE', '52s': 'RAISE',
                '54o': 'RAISE', '53o': 'RAISE', '52o': 'RAISE',
                '43s': 'RAISE', '42s': 'RAISE',
                '43o': 'RAISE', '42o': 'RAISE',
                '32s': 'RAISE',
                '32o': 'RAISE'
            },
            'BB': {  # Big Blind (heads up) - tighter range for calling
                'AA': 'RAISE', 'KK': 'RAISE', 'QQ': 'RAISE', 'JJ': 'RAISE', 'TT': 'RAISE', '99': 'RAISE', '88': 'RAISE', '77': 'RAISE', '66': 'RAISE', '55': 'RAISE', '44': 'RAISE', '33': 'RAISE', '22': 'RAISE',
                'AKs': 'RAISE', 'AQs': 'RAISE', 'AJs': 'RAISE', 'ATs': 'RAISE', 'A9s': 'RAISE', 'A8s': 'RAISE', 'A7s': 'RAISE', 'A6s': 'RAISE', 'A5s': 'RAISE', 'A4s': 'RAISE', 'A3s': 'RAISE', 'A2s': 'RAISE',
                'AKo': 'RAISE', 'AQo': 'RAISE', 'AJo': 'RAISE', 'ATo': 'RAISE', 'A9o': 'RAISE', 'A8o': 'RAISE', 'A7o': 'RAISE', 'A6o': 'RAISE', 'A5o': 'RAISE', 'A4o': 'RAISE', 'A3o': 'RAISE', 'A2o': 'RAISE',
                'KQs': 'RAISE', 'KJs': 'RAISE', 'KTs': 'RAISE', 'K9s': 'RAISE', 'K8s': 'RAISE', 'K7s': 'RAISE', 'K6s': 'RAISE', 'K5s': 'RAISE', 'K4s': 'RAISE', 'K3s': 'RAISE', 'K2s': 'RAISE',
                'KQo': 'RAISE', 'KJo': 'RAISE', 'KTo': 'RAISE', 'K9o': 'RAISE', 'K8o': 'RAISE', 'K7o': 'RAISE', 'K6o': 'RAISE', 'K5o': 'RAISE', 'K4o': 'RAISE', 'K3o': 'RAISE', 'K2o': 'RAISE',
                'QJs': 'RAISE', 'QTs': 'RAISE', 'Q9s': 'RAISE', 'Q8s': 'RAISE', 'Q7s': 'RAISE', 'Q6s': 'RAISE', 'Q5s': 'RAISE', 'Q4s': 'RAISE', 'Q3s': 'RAISE', 'Q2s': 'RAISE',
                'QJo': 'RAISE', 'QTo': 'RAISE', 'Q9o': 'RAISE', 'Q8o': 'RAISE', 'Q7o': 'RAISE', 'Q6o': 'RAISE', 'Q5o': 'RAISE', 'Q4o': 'RAISE', 'Q3o': 'RAISE', 'Q2o': 'RAISE',
                'JTs': 'RAISE', 'J9s': 'RAISE', 'J8s': 'RAISE', 'J7s': 'RAISE', 'J6s': 'RAISE', 'J5s': 'RAISE', 'J4s': 'RAISE', 'J3s': 'RAISE', 'J2s': 'RAISE',
                'JTo': 'RAISE', 'J9o': 'RAISE', 'J8o': 'RAISE', 'J7o': 'RAISE', 'J6o': 'RAISE', 'J5o': 'RAISE', 'J4o': 'RAISE', 'J3o': 'RAISE', 'J2o': 'RAISE',
                'T9s': 'RAISE', 'T8s': 'RAISE', 'T7s': 'RAISE', 'T6s': 'RAISE', 'T5s': 'RAISE', 'T4s': 'RAISE', 'T3s': 'RAISE', 'T2s': 'RAISE',
                'T9o': 'RAISE', 'T8o': 'RAISE', 'T7o': 'RAISE', 'T6o': 'RAISE', 'T5o': 'RAISE', 'T4o': 'RAISE', 'T3o': 'RAISE', 'T2o': 'RAISE',
                '98s': 'RAISE', '97s': 'RAISE', '96s': 'RAISE', '95s': 'RAISE', '94s': 'RAISE', '93s': 'RAISE', '92s': 'RAISE',
                '98o': 'RAISE', '97o': 'RAISE', '96o': 'RAISE', '95o': 'RAISE', '94o': 'RAISE', '93o': 'RAISE', '92o': 'RAISE',
                '87s': 'RAISE', '86s': 'RAISE', '85s': 'RAISE', '84s': 'RAISE', '83s': 'RAISE', '82s': 'RAISE',
                '87o': 'RAISE', '86o': 'RAISE', '85o': 'RAISE', '84o': 'RAISE', '83o': 'RAISE', '82o': 'RAISE',
                '76s': 'RAISE', '75s': 'RAISE', '74s': 'RAISE', '73s': 'RAISE', '72s': 'RAISE',
                '76o': 'RAISE', '75o': 'RAISE', '74o': 'RAISE', '73o': 'RAISE', '72o': 'RAISE',
                '65s': 'RAISE', '64s': 'RAISE', '63s': 'RAISE', '62s': 'RAISE',
                '65o': 'RAISE', '64o': 'RAISE', '63o': 'RAISE', '62o': 'RAISE',
                '54s': 'RAISE', '53s': 'RAISE', '52s': 'RAISE',
                '54o': 'RAISE', '53o': 'RAISE', '52o': 'RAISE',
                '43s': 'RAISE', '42s': 'RAISE',
                '43o': 'RAISE', '42o': 'RAISE',
                '32s': 'RAISE',
                '32o': 'RAISE'
            }
        }
    
    def get_preflop_action(self, position: str, hole_cards: List[Card]) -> str:
        """looks up what you should do preflop based on position and cards"""
        if len(hole_cards) != 2:
            return 'FOLD'
        
        # Convert cards to hand notation
        card1, card2 = hole_cards
        if card1.value == card2.value:
            hand = f"{card1.rank}{card2.rank}"
        elif card1.suit == card2.suit:
            # Suited hand - higher card first
            if card1.value > card2.value:
                hand = f"{card1.rank}{card2.rank}s"
            else:
                hand = f"{card2.rank}{card1.rank}s"
        else:
            # Offsuit hand - higher card first
            if card1.value > card2.value:
                hand = f"{card1.rank}{card2.rank}o"
            else:
                hand = f"{card2.rank}{card1.rank}o"
        
        chart = self.preflop_charts.get(position, {})
        return chart.get(hand, 'FOLD')

# Initialize components
hand_evaluator = HandEvaluator()
equity_calculator = EquityCalculator()
preflop_strategy = PreflopStrategy()

# API Routes
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
        
        # Validate inputs
        if len(hero_hand_str) != 2:
            return jsonify({'error': 'Hero hand must have exactly 2 cards'}), 400
        
        # Use default top 25% range if no range provided
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
            hero_hand = [Card(card_str) for card_str in hero_hand_str]
            board = [Card(card_str) for card_str in board_str]
        except Exception as e:
            return jsonify({'error': f'Invalid card format: {str(e)}'}), 400
        
        # Validate no duplicate cards
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
        action = preflop_strategy.get_preflop_action(position, hole_cards)
        
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
        
        # Get current hand strength
        if len(board) >= 3:
            all_cards = hero_hand + board
            if len(all_cards) >= 5:
                # Get best 5-card hand
                from itertools import combinations
                best_hand = None
                best_strength = 0
                
                for combo in combinations(all_cards, 5):
                    hand_result = hand_evaluator.evaluate_hand(list(combo))
                    if hand_result['strength'] > best_strength:
                        best_strength = hand_result['strength']
                        best_hand = hand_result
            else:
                best_hand = {'hand_type': 'incomplete', 'strength': 0}
        else:
            # Preflop analysis - calculate hand strength by simulation
            hand_strength = _calculate_hand_strength_simulation(hero_hand)
            best_hand = {'hand_type': 'preflop', 'strength': hand_strength}
        
        # Get preflop recommendation
        preflop_action = preflop_strategy.get_preflop_action(position, hero_hand) if len(board) == 0 else 'POSTFLOP'
        
        # Calculate pot odds
        pot_odds = current_bet / (pot_size + current_bet) if (pot_size + current_bet) > 0 else 0
        
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

def _get_hand_cards(hand_notation: str, excluded_cards: List[Card]) -> List[Card]:
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

def _calculate_hand_strength_simulation(hero_hand: List[Card]) -> float:
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

def _calculate_hand_percentile(hero_hand: List[Card]) -> float:
    """Calculate hand strength as percentile (0-100) based on all possible hands"""
    if len(hero_hand) != 2:
        return 0.0
    
    # All possible starting hands (169 total)
    all_hands = [
        # Pairs (13 hands)
        'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
        # Suited hands (78 hands)
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
        # Offsuit hands (78 hands)
        'AKo', 'AQo', 'AJo', 'ATo', 'A9o', 'A8o', 'A7o', 'A6o', 'A5o', 'A4o', 'A3o', 'A2o',
        'KQo', 'KJo', 'KTo', 'K9o', 'K8o', 'K7o', 'K6o', 'K5o', 'K4o', 'K3o', 'K2o',
        'QJo', 'QTo', 'Q9o', 'Q8o', 'Q7o', 'Q6o', 'Q5o', 'Q4o', 'Q3o', 'Q2o',
        'JTo', 'J9o', 'J8o', 'J7o', 'J6o', 'J5o', 'J4o', 'J3o', 'J2o',
        'T9o', 'T8o', 'T7o', 'T6o', 'T5o', 'T4o', 'T3o', 'T2o',
        '98o', '97o', '96o', '95o', '94o', '93o', '92o',
        '87o', '86o', '85o', '84o', '83o', '82o',
        '76o', '75o', '74o', '73o', '72o',
        '65o', '64o', '63o', '62o',
        '54o', '53o', '52o',
        '43o', '42o',
        '32o'
    ]
    
    # Convert hero hand to notation
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
    
    # Find position in ranked list
    try:
        position = all_hands.index(hand_notation)
        # Convert to percentile (0-100)
        percentile = ((len(all_hands) - position - 1) / (len(all_hands) - 1)) * 100
        return round(percentile, 1)
    except ValueError:
        return 0.0

def _calculate_preflop_strength(hero_hand: List[Card]) -> int:
    """Calculate preflop hand strength (1-10 scale)"""
    if len(hero_hand) != 2:
        return 0
    
    card1, card2 = hero_hand
    val1, val2 = card1.value, card2.value
    
    # Pairs
    if val1 == val2:
        if val1 >= 14:  # AA
            return 10
        elif val1 >= 13:  # KK
            return 9
        elif val1 >= 12:  # QQ
            return 8
        elif val1 >= 11:  # JJ
            return 7
        elif val1 >= 10:  # TT
            return 6
        elif val1 >= 8:  # 99, 88
            return 5
        elif val1 >= 6:  # 77, 66
            return 4
        else:  # Lower pairs
            return 3
    
    # Suited hands
    if card1.suit == card2.suit:
        high_val = max(val1, val2)
        low_val = min(val1, val2)
        
        if high_val == 14 and low_val == 13:  # AKs
            return 9
        elif high_val == 14 and low_val >= 12:  # AQs, AJs
            return 8
        elif high_val == 14 and low_val >= 10:  # ATs, A9s
            return 7
        elif high_val == 13 and low_val == 12:  # KQs
            return 7
        elif high_val == 13 and low_val >= 10:  # KJs, KTs
            return 6
        elif high_val == 12 and low_val == 11:  # QJs
            return 6
        elif high_val == 12 and low_val >= 9:  # QTs, Q9s
            return 5
        elif high_val == 11 and low_val >= 9:  # JTs, J9s
            return 5
        elif high_val == 10 and low_val >= 8:  # T9s, T8s
            return 4
        else:
            return 3
    
    # Offsuit hands
    else:
        high_val = max(val1, val2)
        low_val = min(val1, val2)
        
        if high_val == 14 and low_val == 13:  # AKo
            return 8
        elif high_val == 14 and low_val >= 12:  # AQo, AJo
            return 7
        elif high_val == 14 and low_val >= 10:  # ATo, A9o
            return 6
        elif high_val == 13 and low_val == 12:  # KQo
            return 6
        elif high_val == 13 and low_val >= 10:  # KJo, KTo
            return 5
        elif high_val == 12 and low_val == 11:  # QJo
            return 5
        elif high_val == 12 and low_val >= 9:  # QTo, Q9o
            return 4
        elif high_val == 11 and low_val >= 9:  # JTo, J9o
            return 4
        else:
            return 3

def _get_recommendation(hand_analysis: Dict, preflop_action: str, pot_odds: float, board_cards: int) -> str:
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

if __name__ == '__main__':
    print("starting elara poker calculator...")
    print("available endpoints:")
    print("  - GET  /health")
    print("  - POST /evaluate_hand")
    print("  - POST /calculate_equity")
    print("  - POST /preflop_action")
    print("  - POST /analyze_hand")
    print("server running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
