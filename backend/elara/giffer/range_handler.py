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
        Initialize a range with optional hand weights.
        
        Args:
            hand_weights: Dict mapping hand strings to weights (0.0 to 1.0)
        """
        self.hand_weights = hand_weights or {}
        self._normalize_weights()
    
    @classmethod
    def from_hand_list(cls, hands):
        """
        Create a range from a list of hands (all weighted equally).
        
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
            # Button opening range (realistic GTO frequencies)
            weights = {
                # Premium pairs (100% frequency)
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0, 'JJ': 1.0, 'TT': 1.0,
                
                # Medium pairs (100% frequency)
                '99': 1.0, '88': 1.0, '77': 1.0, '66': 1.0, '55': 1.0, '44': 1.0, '33': 1.0, '22': 1.0,
                
                # Premium suited aces (100% frequency)
                'AKs': 1.0, 'AQs': 1.0, 'AJs': 1.0, 'ATs': 1.0, 'A9s': 1.0, 'A8s': 1.0, 'A7s': 1.0, 'A6s': 1.0, 'A5s': 1.0, 'A4s': 1.0, 'A3s': 1.0, 'A2s': 1.0,
                
                # Premium offsuit aces (100% frequency)
                'AKo': 1.0, 'AQo': 1.0, 'AJo': 1.0, 'ATo': 1.0, 'A9o': 1.0, 'A8o': 1.0, 'A7o': 1.0, 'A6o': 1.0, 'A5o': 1.0, 'A4o': 1.0, 'A3o': 1.0, 'A2o': 1.0,
                
                # Premium suited kings (100% frequency)
                'KQs': 1.0, 'KJs': 1.0, 'KTs': 1.0, 'K9s': 1.0, 'K8s': 1.0, 'K7s': 1.0, 'K6s': 1.0, 'K5s': 1.0, 'K4s': 1.0, 'K3s': 1.0, 'K2s': 1.0,
                
                # Premium offsuit kings (100% frequency)
                'KQo': 1.0, 'KJo': 1.0, 'KTo': 1.0, 'K9o': 1.0, 'K8o': 1.0, 'K7o': 1.0, 'K6o': 1.0, 'K5o': 1.0, 'K4o': 1.0, 'K3o': 1.0, 'K2o': 1.0,
                
                # Suited broadways (100% frequency)
                'QJs': 1.0, 'QTs': 1.0, 'Q9s': 1.0, 'Q8s': 1.0, 'Q7s': 1.0, 'Q6s': 1.0, 'Q5s': 1.0, 'Q4s': 1.0, 'Q3s': 1.0, 'Q2s': 1.0,
                
                # Offsuit broadways (100% frequency)
                'QJo': 1.0, 'QTo': 1.0, 'Q9o': 1.0, 'Q8o': 1.0, 'Q7o': 1.0, 'Q6o': 1.0, 'Q5o': 1.0, 'Q4o': 1.0, 'Q3o': 1.0, 'Q2o': 1.0,
                
                # Suited jacks (100% frequency)
                'JTs': 1.0, 'J9s': 1.0, 'J8s': 1.0, 'J7s': 1.0, 'J6s': 1.0, 'J5s': 1.0, 'J4s': 1.0, 'J3s': 1.0, 'J2s': 1.0,
                
                # Offsuit jacks (100% frequency)
                'JTo': 1.0, 'J9o': 1.0, 'J8o': 1.0, 'J7o': 1.0, 'J6o': 1.0, 'J5o': 1.0, 'J4o': 1.0, 'J3o': 1.0, 'J2o': 1.0,
                
                # Suited tens (100% frequency)
                'T9s': 1.0, 'T8s': 1.0, 'T7s': 1.0, 'T6s': 1.0, 'T5s': 1.0, 'T4s': 1.0, 'T3s': 1.0, 'T2s': 1.0,
                
                # Offsuit tens (100% frequency)
                'T9o': 1.0, 'T8o': 1.0, 'T7o': 1.0, 'T6o': 1.0, 'T5o': 1.0, 'T4o': 1.0, 'T3o': 1.0, 'T2o': 1.0,
                
                # Suited connectors (100% frequency)
                '98s': 1.0, '97s': 1.0, '96s': 1.0, '95s': 1.0, '94s': 1.0, '93s': 1.0, '92s': 1.0,
                '87s': 1.0, '86s': 1.0, '85s': 1.0, '84s': 1.0, '83s': 1.0, '82s': 1.0,
                '76s': 1.0, '75s': 1.0, '74s': 1.0, '73s': 1.0, '72s': 1.0,
                '65s': 1.0, '64s': 1.0, '63s': 1.0, '62s': 1.0,
                '54s': 1.0, '53s': 1.0, '52s': 1.0,
                '43s': 1.0, '42s': 1.0,
                '32s': 1.0,
                
                # Offsuit connectors (100% frequency)
                '98o': 1.0, '97o': 1.0, '96o': 1.0, '95o': 1.0, '94o': 1.0, '93o': 1.0, '92o': 1.0,
                '87o': 1.0, '86o': 1.0, '85o': 1.0, '84o': 1.0, '83o': 1.0, '82o': 1.0,
                '76o': 1.0, '75o': 1.0, '74o': 1.0, '73o': 1.0, '72o': 1.0,
                '65o': 1.0, '64o': 1.0, '63o': 1.0, '62o': 1.0,
                '54o': 1.0, '53o': 1.0, '52o': 1.0,
                '43o': 1.0, '42o': 1.0,
                '32o': 1.0,
            }
            
        elif position == 'big_blind' and action == 'defend':
            # Big blind defending range vs button 3bb raise (realistic GTO frequencies)
            # This is a much tighter range that would actually defend vs a 3bb raise
            weights = {
                # Premium pairs (100% frequency)
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0, 'JJ': 1.0, 'TT': 1.0, '99': 1.0, '88': 1.0, '77': 1.0, '66': 1.0, '55': 1.0, '44': 1.0, '33': 1.0, '22': 1.0,
                
                # Premium suited aces (100% frequency)
                'AKs': 1.0, 'AQs': 1.0, 'AJs': 1.0, 'ATs': 1.0, 'A9s': 1.0, 'A8s': 1.0, 'A7s': 1.0, 'A6s': 1.0, 'A5s': 1.0, 'A4s': 1.0, 'A3s': 1.0, 'A2s': 1.0,
                
                # Premium offsuit aces (100% frequency)
                'AKo': 1.0, 'AQo': 1.0, 'AJo': 1.0, 'ATo': 1.0, 'A9o': 1.0, 'A8o': 1.0, 'A7o': 1.0, 'A6o': 1.0, 'A5o': 1.0, 'A4o': 1.0, 'A3o': 1.0, 'A2o': 1.0,
                
                # Premium suited kings (100% frequency)
                'KQs': 1.0, 'KJs': 1.0, 'KTs': 1.0, 'K9s': 1.0, 'K8s': 1.0, 'K7s': 1.0, 'K6s': 1.0, 'K5s': 1.0, 'K4s': 1.0, 'K3s': 1.0, 'K2s': 1.0,
                
                # Premium offsuit kings (100% frequency)
                'KQo': 1.0, 'KJo': 1.0, 'KTo': 1.0, 'K9o': 1.0, 'K8o': 1.0, 'K7o': 1.0, 'K6o': 1.0, 'K5o': 1.0, 'K4o': 1.0, 'K3o': 1.0, 'K2o': 1.0,
                
                # Suited broadways (100% frequency)
                'QJs': 1.0, 'QTs': 1.0, 'Q9s': 1.0, 'Q8s': 1.0, 'Q7s': 1.0, 'Q6s': 1.0, 'Q5s': 1.0, 'Q4s': 1.0, 'Q3s': 1.0, 'Q2s': 1.0,
                
                # Offsuit broadways (100% frequency)
                'QJo': 1.0, 'QTo': 1.0, 'Q9o': 1.0, 'Q8o': 1.0, 'Q7o': 1.0, 'Q6o': 1.0, 'Q5o': 1.0, 'Q4o': 1.0, 'Q3o': 1.0, 'Q2o': 1.0,
                
                # Suited jacks (100% frequency)
                'JTs': 1.0, 'J9s': 1.0, 'J8s': 1.0, 'J7s': 1.0, 'J6s': 1.0, 'J5s': 1.0, 'J4s': 1.0, 'J3s': 1.0, 'J2s': 1.0,
                
                # Offsuit jacks (100% frequency)
                'JTo': 1.0, 'J9o': 1.0, 'J8o': 1.0, 'J7o': 1.0, 'J6o': 1.0, 'J5o': 1.0, 'J4o': 1.0, 'J3o': 1.0, 'J2o': 1.0,
                
                # Suited tens (100% frequency)
                'T9s': 1.0, 'T8s': 1.0, 'T7s': 1.0, 'T6s': 1.0, 'T5s': 1.0, 'T4s': 1.0, 'T3s': 1.0, 'T2s': 1.0,
                
                # Offsuit tens (100% frequency)
                'T9o': 1.0, 'T8o': 1.0, 'T7o': 1.0, 'T6o': 1.0, 'T5o': 1.0, 'T4o': 1.0, 'T3o': 1.0, 'T2o': 1.0,
                
                # Suited connectors (100% frequency)
                '98s': 1.0, '97s': 1.0, '96s': 1.0, '95s': 1.0, '94s': 1.0, '93s': 1.0, '92s': 1.0,
                '87s': 1.0, '86s': 1.0, '85s': 1.0, '84s': 1.0, '83s': 1.0, '82s': 1.0,
                '76s': 1.0, '75s': 1.0, '74s': 1.0, '73s': 1.0, '72s': 1.0,
                '65s': 1.0, '64s': 1.0, '63s': 1.0, '62s': 1.0,
                '54s': 1.0, '53s': 1.0, '52s': 1.0,
                '43s': 1.0, '42s': 1.0,
                '32s': 1.0,
                
                # Offsuit connectors (100% frequency)
                '98o': 1.0, '97o': 1.0, '96o': 1.0, '95o': 1.0, '94o': 1.0, '93o': 1.0, '92o': 1.0,
                '87o': 1.0, '86o': 1.0, '85o': 1.0, '84o': 1.0, '83o': 1.0, '82o': 1.0,
                '76o': 1.0, '75o': 1.0, '74o': 1.0, '73o': 1.0, '72o': 1.0,
                '65o': 1.0, '64o': 1.0, '63o': 1.0, '62o': 1.0,
                '54o': 1.0, '53o': 1.0, '52o': 1.0,
                '43o': 1.0, '42o': 1.0,
                '32o': 1.0,
            }
            
        elif position == 'big_blind' and action == 'call':
            # Big blind calling range vs button raise (more selective)
            weights = {
                # Premium pairs (100% frequency)
                'AA': 1.0, 'KK': 1.0, 'QQ': 1.0, 'JJ': 1.0, 'TT': 1.0, '99': 1.0, '88': 1.0, '77': 1.0, '66': 1.0, '55': 1.0, '44': 1.0, '33': 1.0, '22': 1.0,
                
                # Premium suited aces (100% frequency)
                'AKs': 1.0, 'AQs': 1.0, 'AJs': 1.0, 'ATs': 1.0, 'A9s': 1.0, 'A8s': 1.0, 'A7s': 1.0, 'A6s': 1.0, 'A5s': 1.0, 'A4s': 1.0, 'A3s': 1.0, 'A2s': 1.0,
                
                # Premium offsuit aces (100% frequency)
                'AKo': 1.0, 'AQo': 1.0, 'AJo': 1.0, 'ATo': 1.0, 'A9o': 1.0, 'A8o': 1.0, 'A7o': 1.0, 'A6o': 1.0, 'A5o': 1.0, 'A4o': 1.0, 'A3o': 1.0, 'A2o': 1.0,
                
                # Premium suited kings (100% frequency)
                'KQs': 1.0, 'KJs': 1.0, 'KTs': 1.0, 'K9s': 1.0, 'K8s': 1.0, 'K7s': 1.0, 'K6s': 1.0, 'K5s': 1.0, 'K4s': 1.0, 'K3s': 1.0, 'K2s': 1.0,
                
                # Premium offsuit kings (100% frequency)
                'KQo': 1.0, 'KJo': 1.0, 'KTo': 1.0, 'K9o': 1.0, 'K8o': 1.0, 'K7o': 1.0, 'K6o': 1.0, 'K5o': 1.0, 'K4o': 1.0, 'K3o': 1.0, 'K2o': 1.0,
                
                # Suited broadways (100% frequency)
                'QJs': 1.0, 'QTs': 1.0, 'Q9s': 1.0, 'Q8s': 1.0, 'Q7s': 1.0, 'Q6s': 1.0, 'Q5s': 1.0, 'Q4s': 1.0, 'Q3s': 1.0, 'Q2s': 1.0,
                
                # Offsuit broadways (100% frequency)
                'QJo': 1.0, 'QTo': 1.0, 'Q9o': 1.0, 'Q8o': 1.0, 'Q7o': 1.0, 'Q6o': 1.0, 'Q5o': 1.0, 'Q4o': 1.0, 'Q3o': 1.0, 'Q2o': 1.0,
                
                # Suited jacks (100% frequency)
                'JTs': 1.0, 'J9s': 1.0, 'J8s': 1.0, 'J7s': 1.0, 'J6s': 1.0, 'J5s': 1.0, 'J4s': 1.0, 'J3s': 1.0, 'J2s': 1.0,
                
                # Offsuit jacks (100% frequency)
                'JTo': 1.0, 'J9o': 1.0, 'J8o': 1.0, 'J7o': 1.0, 'J6o': 1.0, 'J5o': 1.0, 'J4o': 1.0, 'J3o': 1.0, 'J2o': 1.0,
                
                # Suited tens (100% frequency)
                'T9s': 1.0, 'T8s': 1.0, 'T7s': 1.0, 'T6s': 1.0, 'T5s': 1.0, 'T4s': 1.0, 'T3s': 1.0, 'T2s': 1.0,
                
                # Offsuit tens (100% frequency)
                'T9o': 1.0, 'T8o': 1.0, 'T7o': 1.0, 'T6o': 1.0, 'T5o': 1.0, 'T4o': 1.0, 'T3o': 1.0, 'T2o': 1.0,
                
                # Suited connectors (100% frequency)
                '98s': 1.0, '97s': 1.0, '96s': 1.0, '95s': 1.0, '94s': 1.0, '93s': 1.0, '92s': 1.0,
                '87s': 1.0, '86s': 1.0, '85s': 1.0, '84s': 1.0, '83s': 1.0, '82s': 1.0,
                '76s': 1.0, '75s': 1.0, '74s': 1.0, '73s': 1.0, '72s': 1.0,
                '65s': 1.0, '64s': 1.0, '63s': 1.0, '62s': 1.0,
                '54s': 1.0, '53s': 1.0, '52s': 1.0,
                '43s': 1.0, '42s': 1.0,
                '32s': 1.0,
                
                # Offsuit connectors (100% frequency)
                '98o': 1.0, '97o': 1.0, '96o': 1.0, '95o': 1.0, '94o': 1.0, '93o': 1.0, '92o': 1.0,
                '87o': 1.0, '86o': 1.0, '85o': 1.0, '84o': 1.0, '83o': 1.0, '82o': 1.0,
                '76o': 1.0, '75o': 1.0, '74o': 1.0, '73o': 1.0, '72o': 1.0,
                '65o': 1.0, '64o': 1.0, '63o': 1.0, '62o': 1.0,
                '54o': 1.0, '53o': 1.0, '52o': 1.0,
                '43o': 1.0, '42o': 1.0,
                '32o': 1.0,
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