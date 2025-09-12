"""
Range handling and GTO charts for Elara poker engine.

Implements the Range class for representing hand distributions and
GTO charts for pre-flop strategy. Provides dynamic range filtering
based on betting actions.
"""

import itertools
from ..engine.card import Card, RANKS

class Range:
    """
    Represents a distribution of starting hands with associated probabilities.
    
    The Range class is central to Elara's strategic analysis, providing
    a way to model an opponent's likely holdings and update this model
    based on their actions throughout the hand.
    """
    
    def __init__(self, hand_weights=None):
        """
        Args:
            hand_weights: Dict mapping hand strings to weights (0.0 to 1.0)
        """
        self.hand_weights = hand_weights or {}
        self._normalize_weights()
    
    @classmethod
    def from_hand_list(cls, hands):
        """
        Args:
            hands: List of hand strings (e.g., ['AA', 'KK', 'AKs'])
            
        Returns:
            Range object
        """
        weights = {hand: 1.0 for hand in hands}
        return cls(weights)
    
    @classmethod
    def from_gto_chart(cls, position, action, bet_size=None):
        """
        Create a range from a GTO chart based on position and action.
        
        Args:
            position: 'button' or 'big_blind'
            action: 'raise', 'call', 'fold', '3bet', 'defend'
            bet_size: Optional bet size for sizing-specific ranges
            
        Returns:
            Range object with realistic hand weights
        """
        if position == 'button' and action == 'raise':
            # Button opening range (realistic GTO frequencies for heads-up)
            weights = {
                # All pairs (100% frequency)
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0, 'JJ': 1.0, 'TT': 1.0,
                '99': 1.0, '88': 1.0, '77': 1.0, '66': 1.0, '55': 1.0, '44': 1.0, '33': 1.0, '22': 1.0,
                
                # All suited aces (100% frequency) 
                'AKs': 1.0, 'AQs': 1.0, 'AJs': 1.0, 'ATs': 1.0, 'A9s': 1.0, 'A8s': 1.0, 'A7s': 1.0, 'A6s': 1.0, 'A5s': 1.0, 'A4s': 1.0, 'A3s': 1.0, 'A2s': 1.0,
                
                # Strong offsuit aces (most frequency)
                'AKo': 1.0, 'AQo': 1.0, 'AJo': 1.0, 'ATo': 1.0, 'A9o': 1.0, 'A8o': 0.8, 'A7o': 0.6, 'A6o': 0.4, 'A5o': 0.6, 'A4o': 0.4, 'A3o': 0.4, 'A2o': 0.4,
                
                # Suited kings (high frequency)
                'KQs': 1.0, 'KJs': 1.0, 'KTs': 1.0, 'K9s': 1.0, 'K8s': 0.9, 'K7s': 0.8, 'K6s': 0.7, 'K5s': 0.7, 'K4s': 0.6, 'K3s': 0.6, 'K2s': 0.6,
                
                # Strong offsuit kings (mixed frequency)
                'KQo': 1.0, 'KJo': 1.0, 'KTo': 0.9, 'K9o': 0.7, 'K8o': 0.5, 'K7o': 0.3, 'K6o': 0.2, 'K5o': 0.2,
                
                # Suited queens (high frequency for strong ones)
                'QJs': 1.0, 'QTs': 1.0, 'Q9s': 0.9, 'Q8s': 0.8, 'Q7s': 0.7, 'Q6s': 0.6, 'Q5s': 0.5, 'Q4s': 0.4,
                
                # Strong offsuit queens (mixed frequency)
                'QJo': 1.0, 'QTo': 0.9, 'Q9o': 0.6, 'Q8o': 0.4, 'Q7o': 0.2,
                
                # Suited jacks (good connectivity)
                'JTs': 1.0, 'J9s': 1.0, 'J8s': 0.9, 'J7s': 0.8, 'J6s': 0.6, 'J5s': 0.5, 'J4s': 0.4,
                
                # Strong offsuit jacks
                'JTo': 1.0, 'J9o': 0.8, 'J8o': 0.5, 'J7o': 0.3,
                
                # Suited tens (connectors and strong)
                'T9s': 1.0, 'T8s': 1.0, 'T7s': 0.9, 'T6s': 0.8, 'T5s': 0.7, 'T4s': 0.5,
                
                # Strong offsuit tens
                'T9o': 0.9, 'T8o': 0.7, 'T7o': 0.4,
                
                # Suited connectors and one-gappers
                '98s': 1.0, '97s': 0.9, '96s': 0.7, '95s': 0.5,
                '87s': 1.0, '86s': 0.8, '85s': 0.6,
                '76s': 1.0, '75s': 0.7,
                '65s': 1.0, '64s': 0.6,
                '54s': 1.0, '53s': 0.5,
                '43s': 0.8,
                
                # Strong offsuit connectors (very selective)
                '98o': 0.7, '97o': 0.4,
                '87o': 0.6,
                '76o': 0.5,
                '65o': 0.4,
            }
            
        elif position == 'big_blind' and action == 'defend':
            # Big blind defending range vs button raise (realistic GTO frequencies)
            # Tighter than button opening but still wide enough for heads-up
            weights = {
                # All pairs (high frequency)
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0, 'JJ': 1.0, 'TT': 1.0, '99': 1.0, '88': 1.0, '77': 1.0, '66': 1.0, '55': 1.0, '44': 1.0, '33': 1.0, '22': 1.0,
                
                # All suited aces (high frequency)
                'AKs': 1.0, 'AQs': 1.0, 'AJs': 1.0, 'ATs': 1.0, 'A9s': 1.0, 'A8s': 1.0, 'A7s': 1.0, 'A6s': 1.0, 'A5s': 1.0, 'A4s': 1.0, 'A3s': 1.0, 'A2s': 1.0,
                
                # Strong offsuit aces (mixed frequency)
                'AKo': 1.0, 'AQo': 1.0, 'AJo': 1.0, 'ATo': 1.0, 'A9o': 0.8, 'A8o': 0.6, 'A7o': 0.5, 'A6o': 0.4, 'A5o': 0.5, 'A4o': 0.4, 'A3o': 0.4, 'A2o': 0.4,
                
                # Suited kings (good frequency)
                'KQs': 1.0, 'KJs': 1.0, 'KTs': 1.0, 'K9s': 0.9, 'K8s': 0.8, 'K7s': 0.7, 'K6s': 0.6, 'K5s': 0.6, 'K4s': 0.5, 'K3s': 0.5, 'K2s': 0.5,
                
                # Offsuit kings (more selective)
                'KQo': 1.0, 'KJo': 1.0, 'KTo': 0.8, 'K9o': 0.6, 'K8o': 0.4, 'K7o': 0.3, 'K6o': 0.2, 'K5o': 0.2,
                
                # Suited queens (good connectivity)
                'QJs': 1.0, 'QTs': 1.0, 'Q9s': 0.8, 'Q8s': 0.7, 'Q7s': 0.6, 'Q6s': 0.5, 'Q5s': 0.4, 
                
                # Offsuit queens (selective)
                'QJo': 1.0, 'QTo': 0.8, 'Q9o': 0.5, 'Q8o': 0.3, 'Q7o': 0.2,
                
                # Suited jacks (good connectivity)
                'JTs': 1.0, 'J9s': 1.0, 'J8s': 0.8, 'J7s': 0.7, 'J6s': 0.5, 'J5s': 0.4,
                
                # Offsuit jacks (selective)
                'JTo': 1.0, 'J9o': 0.7, 'J8o': 0.4, 'J7o': 0.2,
                
                # Suited tens (connectors)
                'T9s': 1.0, 'T8s': 1.0, 'T7s': 0.8, 'T6s': 0.6, 'T5s': 0.5,
                
                # Offsuit tens (limited)
                'T9o': 0.8, 'T8o': 0.5, 'T7o': 0.3,
                
                # Suited connectors (good playability)
                '98s': 1.0, '97s': 0.8, '96s': 0.6,
                '87s': 1.0, '86s': 0.7, '85s': 0.5,
                '76s': 1.0, '75s': 0.6,
                '65s': 1.0, '64s': 0.5,
                '54s': 1.0, '53s': 0.4,
                '43s': 0.7,
                
                # Offsuit connectors (very selective)
                '98o': 0.6, '97o': 0.3,
                '87o': 0.5,
                '76o': 0.4,
                '65o': 0.3,
            }
            
        elif position == 'big_blind' and action == 'call':
            # Big blind calling range vs button raise (balanced but realistic)
            weights = {
                # All pairs (high frequency - have good implied odds)
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0, 'JJ': 1.0, 'TT': 1.0, '99': 1.0, '88': 1.0, '77': 1.0, '66': 1.0, '55': 1.0, '44': 1.0, '33': 1.0, '22': 1.0,
                
                # All suited aces (high frequency - good playability)
                'AKs': 1.0, 'AQs': 1.0, 'AJs': 1.0, 'ATs': 1.0, 'A9s': 1.0, 'A8s': 1.0, 'A7s': 1.0, 'A6s': 1.0, 'A5s': 1.0, 'A4s': 1.0, 'A3s': 1.0, 'A2s': 1.0,
                
                # Strong offsuit aces (mixed frequency)
                'AKo': 1.0, 'AQo': 1.0, 'AJo': 1.0, 'ATo': 1.0, 'A9o': 0.9, 'A8o': 0.7, 'A7o': 0.6, 'A6o': 0.5, 'A5o': 0.6, 'A4o': 0.5, 'A3o': 0.5, 'A2o': 0.5,
                
                # Suited kings (good frequency)
                'KQs': 1.0, 'KJs': 1.0, 'KTs': 1.0, 'K9s': 1.0, 'K8s': 0.9, 'K7s': 0.8, 'K6s': 0.7, 'K5s': 0.7, 'K4s': 0.6, 'K3s': 0.6, 'K2s': 0.6,
                
                # Offsuit kings (selective)
                'KQo': 1.0, 'KJo': 1.0, 'KTo': 0.9, 'K9o': 0.7, 'K8o': 0.5, 'K7o': 0.4, 'K6o': 0.3, 'K5o': 0.3, 'K4o': 0.2, 'K3o': 0.2, 'K2o': 0.2,
                
                # Suited queens (good connectivity)
                'QJs': 1.0, 'QTs': 1.0, 'Q9s': 1.0, 'Q8s': 0.9, 'Q7s': 0.8, 'Q6s': 0.7, 'Q5s': 0.6, 'Q4s': 0.5, 'Q3s': 0.4, 'Q2s': 0.3,
                
                # Offsuit queens (mixed frequency)
                'QJo': 1.0, 'QTo': 0.9, 'Q9o': 0.7, 'Q8o': 0.5, 'Q7o': 0.4, 'Q6o': 0.3, 'Q5o': 0.2, 'Q4o': 0.1, 'Q3o': 0.1, 'Q2o': 0.1,
                
                # Suited jacks (good connectivity)
                'JTs': 1.0, 'J9s': 1.0, 'J8s': 1.0, 'J7s': 0.9, 'J6s': 0.7, 'J5s': 0.6, 'J4s': 0.5, 'J3s': 0.4, 'J2s': 0.3,
                
                # Offsuit jacks (mixed frequency)
                'JTo': 1.0, 'J9o': 0.8, 'J8o': 0.6, 'J7o': 0.4, 'J6o': 0.3, 'J5o': 0.2, 'J4o': 0.1, 'J3o': 0.1, 'J2o': 0.1,
                
                # Suited tens (connectors and strong)
                'T9s': 1.0, 'T8s': 1.0, 'T7s': 1.0, 'T6s': 0.9, 'T5s': 0.8, 'T4s': 0.6, 'T3s': 0.4, 'T2s': 0.3,
                
                # Offsuit tens (selective)
                'T9o': 0.9, 'T8o': 0.7, 'T7o': 0.5, 'T6o': 0.3, 'T5o': 0.2, 'T4o': 0.1, 'T3o': 0.1, 'T2o': 0.1,
                
                # Suited connectors and gappers (good playability)
                '98s': 1.0, '97s': 1.0, '96s': 0.8, '95s': 0.6, '94s': 0.4, '93s': 0.3, '92s': 0.2,
                '87s': 1.0, '86s': 0.9, '85s': 0.7, '84s': 0.5, '83s': 0.3, '82s': 0.2,
                '76s': 1.0, '75s': 0.8, '74s': 0.6, '73s': 0.4, '72s': 0.2,
                '65s': 1.0, '64s': 0.7, '63s': 0.5, '62s': 0.3,
                '54s': 1.0, '53s': 0.6, '52s': 0.3,
                '43s': 0.8, '42s': 0.4,
                '32s': 0.3,
                
                # Offsuit connectors (very selective - only strong ones)
                '98o': 0.7, '97o': 0.5, '96o': 0.3, '95o': 0.2, '94o': 0.1, '93o': 0.1, '92o': 0.1,
                '87o': 0.6, '86o': 0.4, '85o': 0.2, '84o': 0.1, '83o': 0.1, '82o': 0.1,
                '76o': 0.5, '75o': 0.3, '74o': 0.1, '73o': 0.1, '72o': 0.0,  # 72o is the worst hand
                '65o': 0.4, '64o': 0.2, '63o': 0.1, '62o': 0.1,
                '54o': 0.3, '53o': 0.1, '52o': 0.1,
                '43o': 0.2, '42o': 0.1,
                '32o': 0.1,
            }
            
        else:
            # Default to a tight range for other scenarios
            weights = {
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0, 'JJ': 1.0, 'TT': 1.0, '99': 1.0, '88': 1.0, '77': 1.0, '66': 1.0, '55': 1.0, '44': 1.0, '33': 1.0, '22': 1.0,
                'AKs': 1.0, 'AQs': 1.0, 'AJs': 1.0, 'ATs': 1.0, 'A9s': 1.0, 'A8s': 1.0, 'A7s': 1.0, 'A6s': 1.0, 'A5s': 1.0, 'A4s': 1.0, 'A3s': 1.0, 'A2s': 1.0,
                'AKo': 1.0, 'AQo': 1.0, 'AJo': 1.0, 'ATo': 1.0, 'A9o': 1.0, 'A8o': 1.0, 'A7o': 1.0, 'A6o': 1.0, 'A5o': 1.0, 'A4o': 1.0, 'A3o': 1.0, 'A2o': 1.0,
            }
        
        return cls(weights)
    
    @classmethod
    def from_equity_based_chart(cls, position, action, button_range=None, num_trials=100):
        """
        Generate a preflop defend range for the big blind using equity-based frequencies.
        For each BB hand, simulate vs each button open hand, and set frequency based on
        the percent of matchups where BB hand is 'playable' (>=45% equity).
        """
        from ..engine.card import Card, RANKS, SUITS
        from ..engine.deck import Deck
        from ..engine.evaluator import HandEvaluator
        import random

        # Use default button open range if not provided
        if button_range is None:
            button_range = [
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
                '32s', '32o',
            ]

        # Generate all possible BB hands (same as above)
        bb_hands = button_range.copy()
        hand_evaluator = HandEvaluator()
        weights = {}

        def expand_hand(hand_str):
            # Returns all combos for a hand string (e.g., 'AKs' -> ['AsKs', ...])
            combos = []
            if len(hand_str) == 2:  # Pair
                rank = hand_str[0]
                for i, s1 in enumerate(SUITS):
                    for j, s2 in enumerate(SUITS):
                        if i < j:
                            combos.append(f"{rank}{s1}{rank}{s2}")
            elif len(hand_str) == 3:
                r1, r2, suitedness = hand_str[0], hand_str[1], hand_str[2]
                if suitedness == 's':
                    for s in SUITS:
                        combos.append(f"{r1}{s}{r2}{s}")
                elif suitedness == 'o':
                    for s1 in SUITS:
                        for s2 in SUITS:
                            if s1 != s2:
                                combos.append(f"{r1}{s1}{r2}{s2}")
            return combos

        # Precompute all button combos
        button_combos = []
        for btn_hand in button_range:
            button_combos.extend(expand_hand(btn_hand))

        for bb_hand in bb_hands:
            bb_combos = expand_hand(bb_hand)
            playable_count = 0
            total_count = 0
            for bb_combo in bb_combos:
                bb_cards = Card.parse_hand_string(bb_combo)
                for btn_hand in button_range:
                    btn_combos = expand_hand(btn_hand)
                    for btn_combo in btn_combos:
                        btn_cards = Card.parse_hand_string(btn_combo)
                        # Skip if overlap
                        if set(str(c) for c in bb_cards) & set(str(c) for c in btn_cards):
                            continue
                        # Simulate num_trials random boards
                        bb_favored = 0
                        for _ in range(num_trials):
                            # Build deck
                            excluded = bb_cards + btn_cards
                            deck = Deck.create_from_excluded_cards(excluded)
                            board = deck.deal(5)
                            bb_score = hand_evaluator.evaluate_hand(bb_cards + board)
                            btn_score = hand_evaluator.evaluate_hand(btn_cards + board)
                            # Lower score is better (eval7 convention)
                            if bb_score < btn_score:
                                bb_favored += 1
                        equity = bb_favored / num_trials
                        if equity >= 0.45:
                            playable_count += 1
                        total_count += 1
            freq = playable_count / total_count if total_count > 0 else 0.0
            weights[bb_hand] = freq
        return cls(weights)
    
    def _normalize_weights(self):
        """Normalize hand weights to sum to 1.0."""
        total_weight = sum(self.hand_weights.values())
        if total_weight > 0:
            for hand in self.hand_weights:
                self.hand_weights[hand] /= total_weight
    
    def get_weighted_hands(self):
        """
        Get the weighted hand distribution.
        
        Returns:
            Dict mapping hand strings to weights
        """
        return self.hand_weights.copy()
    
    def filter_by_action(self, action, bet_size=None, position=None):
        """
        Filter the range based on an action taken.
        
        Args:
            action: 'fold', 'call', 'raise', 'check'
            bet_size: Size of bet/raise (in big blinds)
            position: Player position for context
            
        Returns:
            New Range object with filtered weights
        """
        # This is a simplified implementation
        # A full implementation would use detailed GTO charts
        
        filtered_weights = {}
        
        for hand, weight in self.hand_weights.items():
            # Simple filtering logic
            if action == 'fold':
                # Hands that fold get weight reduced to 0
                continue
            elif action == 'call':
                # Hands that call keep their weight
                filtered_weights[hand] = weight
            elif action == 'raise':
                # Hands that raise keep their weight
                filtered_weights[hand] = weight
            elif action == 'check':
                # Hands that check keep their weight
                filtered_weights[hand] = weight
        
        return Range(filtered_weights)
    
    def update_from_betting_action(self, action, bet_size, position, street):
        """
        Update range based on a betting action using GTO principles.
        
        Args:
            action: Action taken
            bet_size: Size of bet/raise
            position: Player position
            street: Current street
            
        Returns:
            Updated Range object
        """
        # This is where the sophisticated range filtering happens
        # For now, use simplified logic
        
        if action == 'fold':
            # Remove all hands from range
            return Range({})
        
        elif action == 'call':
            # Keep hands that would call at this sizing
            return self._filter_by_call_sizing(bet_size, position, street)
        
        elif action == 'raise':
            # Keep hands that would raise at this sizing
            return self._filter_by_raise_sizing(bet_size, position, street)
        
        else:
            # For other actions, keep current range
            return Range(self.hand_weights.copy())
    
    def _filter_by_call_sizing(self, bet_size, position, street):
        """Filter range based on call sizing."""
        # Simplified: keep stronger hands more likely to call
        filtered_weights = {}
        
        for hand, weight in self.hand_weights.items():
            hand_strength = self._get_hand_strength(hand)
            
            # Adjust weight based on bet size and hand strength
            if bet_size <= 0.5:  # Small bet
                filtered_weights[hand] = weight * 0.9
            elif bet_size <= 1.0:  # Medium bet
                filtered_weights[hand] = weight * (0.7 + hand_strength * 0.3)
            else:  # Large bet
                filtered_weights[hand] = weight * hand_strength
        
        return Range(filtered_weights)
    
    def _filter_by_raise_sizing(self, bet_size, position, street):
        """Filter range based on raise sizing."""
        # Simplified: keep stronger hands more likely to raise
        filtered_weights = {}
        
        for hand, weight in self.hand_weights.items():
            hand_strength = self._get_hand_strength(hand)
            
            # Adjust weight based on raise size and hand strength
            if bet_size <= 3.0:  # Small raise
                filtered_weights[hand] = weight * (0.5 + hand_strength * 0.5)
            else:  # Large raise
                filtered_weights[hand] = weight * hand_strength
        
        return Range(filtered_weights)
    
    def _get_hand_strength(self, hand):
        """
        Get a rough strength estimate for a hand (0.0 to 1.0).
        
        Args:
            hand: Hand string (e.g., 'AA', 'AKs')
            
        Returns:
            float: Hand strength estimate
        """
        # Simplified hand strength calculation
        if len(hand) != 2 and len(hand) != 3:
            return 0.5
        
        if len(hand) == 2:
            # Pocket pair
            rank = hand[0]
            rank_val = RANKS.index(rank)
            return (rank_val + 1) / 13.0
        
        else:
            # Suited or offsuit hand
            rank1, rank2 = hand[0], hand[1]
            rank1_val = RANKS.index(rank1)
            rank2_val = RANKS.index(rank2)
            
            # Base strength on higher rank
            base_strength = max(rank1_val, rank2_val) / 13.0
            
            # Adjust for suitedness
            if hand.endswith('s'):
                base_strength *= 1.1
            
            return min(base_strength, 1.0)
    
    def expand_to_combos(self):
        """
        Expand all hand strings in the range to valid two-card combos.
        Returns a list of (combo_str, weight) tuples.
        """
        combos = []
        SUITS = 'shdc'
        for hand, weight in self.hand_weights.items():
            if len(hand) == 2:  # Pair, e.g., 'AA'
                rank = hand[0]
                for i, suit1 in enumerate(SUITS):
                    for j, suit2 in enumerate(SUITS):
                        if i < j:
                            combos.append((f"{rank}{suit1}{rank}{suit2}", weight))
            elif len(hand) == 3:
                rank1, rank2, suitedness = hand[0], hand[1], hand[2]
                if suitedness == 's':
                    for suit in SUITS:
                        combos.append((f"{rank1}{suit}{rank2}{suit}", weight))
                elif suitedness == 'o':
                    for suit1 in SUITS:
                        for suit2 in SUITS:
                            if suit1 != suit2:
                                combos.append((f"{rank1}{suit1}{rank2}{suit2}", weight))
        return combos
    
    def partition_range(self, opponent_range_str, board_cards):
        """
        Partitions a range into value, semi-bluff, and bluff categories based on the board.
        
        Args:
            opponent_range_str: String representation of opponent's range (e.g., "AA,KK,QQ,AKs")
            board_cards: List of Card objects (community cards)
            
        Returns:
            dict: Dictionary with 'value', 'semi_bluff', and 'bluff' lists of hands
        """
        from ..utils.hand_evaluator import HandEvaluator
        
        evaluator = HandEvaluator()
        all_hands = self.parse_range(opponent_range_str)

        partitions = {
            "value": [],        # Two pair or better
            "semi_bluff": [],   # Strong draws
            "bluff": []         # Everything else
        }

        # Remove impossible hands given the board
        possible_hands = [
            hand for hand in all_hands
            if not any(c in board_cards for c in hand)
        ]

        for hand in possible_hands:
            # The rank from the evaluator (lower is better)
            # 7461 is high card, 1 is a straight flush
            rank, hand_type = evaluator.evaluate_hand_with_type(hand, board_cards)

            # Check for strong draws (at least 8 outs for OESD or flush draw)
            # This is a simplification; a more robust check is needed
            outs, is_flush_draw, is_straight_draw = self._calculate_draw_outs(hand, board_cards)

            if hand_type in ["Straight Flush", "Four of a Kind", "Full House", "Flush", "Straight", "Three of a Kind", "Two Pair"]:
                partitions["value"].append(hand)
            elif is_flush_draw or is_straight_draw:
                partitions["semi_bluff"].append(hand)
            else:
                partitions["bluff"].append(hand)

        return partitions

    def _calculate_draw_outs(self, hand, board):
        """
        A helper function to determine if a hand is a strong draw.
        
        Args:
            hand: List of Card objects (hole cards)
            board: List of Card objects (community cards)
            
        Returns:
            tuple: (outs, is_flush_draw, is_straight_draw)
        """
        # This is a placeholder for more complex draw detection logic
        # For now, we'll do a simple check
        all_cards = hand + board
        
        # Flush draw check
        suits = [c.suit for c in all_cards]
        is_flush_draw = any(suits.count(s) == 4 for s in 'shdc')

        # Straight draw check (simplified)
        ranks = sorted(list(set([c.get_rank_value() for c in all_cards])))
        is_straight_draw = False
        if len(ranks) >= 4:
            for i in range(len(ranks) - 3):
                # Check for 4 consecutive ranks (open-ended)
                if ranks[i+3] - ranks[i] == 3:
                    is_straight_draw = True
                    break
                # Check for gutshot (e.g., 5,6,8,9)
                if ranks[i+3] - ranks[i] == 4 and len(ranks) == 4:
                     is_straight_draw = True
                     break
        
        # This is a simplified out counter
        outs = 0
        if is_flush_draw:
            outs += 9
        if is_straight_draw:
            outs += 8  # Could be 4 for gutshot, but simplified for now
        
        return outs, is_flush_draw, is_straight_draw

    def parse_range(self, range_str):
        """
        Parse a range string into a list of hand combinations.
        
        Args:
            range_str: String like "AA,KK,QQ,AKs"
            
        Returns:
            List of hand combinations
        """
        hands = []
        for hand_str in range_str.split(','):
            hand_str = hand_str.strip()
            if len(hand_str) == 2:  # Pair
                hands.append(hand_str)
            elif len(hand_str) == 3:  # Suited or offsuit
                hands.append(hand_str)
        return hands
    
    def __len__(self):
        """Return the number of hands in the range."""
        return len(self.hand_weights)
    
    def __repr__(self):
        return f"Range({len(self)} hands)"
    
    def __str__(self):
        return f"Range with {len(self)} hands"


class GTOCharts:
    """
    Pre-computed GTO strategy charts for heads-up play.
    
    This class would contain the extensive lookup tables derived from
    GTO solvers, mapping every possible game situation to optimal
    action frequencies.
    """
    
    def __init__(self):
        """Initialize GTO charts."""
        # In a full implementation, this would load pre-computed charts
        # from files or databases
        self.charts = {}
    
    def get_action_frequencies(self, position, action_history, bet_sizing):
        """
        Get optimal action frequencies for a given situation.
        
        Args:
            position: Player position
            action_history: History of actions in the hand
            bet_sizing: Available bet sizes
            
        Returns:
            Dict mapping actions to frequencies
        """
        # Simplified implementation
        # A full implementation would use extensive lookup tables
        
        if position == 'button':
            return {
                'fold': 0.1,
                'call': 0.3,
                'raise': 0.6
            }
        else:
            return {
                'fold': 0.2,
                'call': 0.5,
                'raise': 0.3
            }
    
    def get_minimum_defense_frequency(self, bet_size, pot_size):
        """
        Calculate minimum defense frequency for a bet size.
        
        Args:
            bet_size: Size of the bet
            pot_size: Size of the pot
            
        Returns:
            float: Minimum defense frequency (0.0 to 1.0)
        """
        if bet_size <= 0:
            return 1.0
        
        # MDF = pot_size / (pot_size + bet_size)
        return pot_size / (pot_size + bet_size) 