import random
from typing import List, Dict, Any
from .card import Card
from .evaluator import HandEvaluator

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
