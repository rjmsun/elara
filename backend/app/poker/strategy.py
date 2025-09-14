from typing import List
from .card import Card

# preflop strategy - tells you whether to raise, call, or fold preflop
class PreflopStrategy:
    def __init__(self):
        # preflop charts - what to do with each hand
        self.preflop_charts = {
            'SB': {  # small blind: aggressive but not crazy
                # these are the good hands - obviously raise these
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
                'T9o': 'CALL', 'T8o': 'CALL', 'T7o': 'CALL', 'T6o': 'CALL', 'T5o': 'CALL', 'T4o': 'CALL', 'T3o': 'CALL', 'T2o': 'CALL',
                '98s': 'CALL', '97s': 'CALL', '96s': 'CALL', '95s': 'CALL', '94s': 'CALL', '93s': 'CALL', '92s': 'CALL',
                '98o': 'CALL', '97o': 'CALL', '96o': 'CALL', '95o': 'CALL', '94o': 'CALL', '93o': 'CALL', '92o': 'CALL',
                '87s': 'CALL', '86s': 'CALL', '85s': 'CALL', '84s': 'CALL', '83s': 'CALL', '82s': 'CALL',
                '87o': 'CALL', '86o': 'CALL', '85o': 'CALL', '84o': 'CALL', '83o': 'CALL', '82o': 'CALL',
                '76s': 'CALL', '75s': 'CALL', '74s': 'CALL', '73s': 'CALL', '72s': 'CALL',
                '76o': 'CALL', '75o': 'CALL', '74o': 'CALL', '73o': 'CALL', '72o': 'CALL',
                '65s': 'CALL', '64s': 'CALL', '63s': 'CALL', '62s': 'CALL',
                '65o': 'CALL', '64o': 'CALL', '63o': 'CALL', '62o': 'CALL',
                '54s': 'CALL', '53s': 'CALL', '52s': 'CALL',
                '54o': 'CALL', '53o': 'CALL', '52o': 'CALL',
                '43s': 'CALL', '42s': 'CALL',
                '43o': 'FOLD', '42o': 'FOLD',
                '32s': 'CALL',
                '32o': 'FOLD'
            },
            'BB': {  # big blind: a bit more picky here
                # same good hands - still raise these
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
                'T9o': 'CALL', 'T8o': 'CALL', 'T7o': 'CALL', 'T6o': 'CALL', 'T5o': 'CALL', 'T4o': 'CALL', 'T3o': 'CALL', 'T2o': 'CALL',
                '98s': 'CALL', '97s': 'CALL', '96s': 'CALL', '95s': 'CALL', '94s': 'CALL', '93s': 'CALL', '92s': 'CALL',
                '98o': 'CALL', '97o': 'CALL', '96o': 'CALL', '95o': 'CALL', '94o': 'CALL', '93o': 'CALL', '92o': 'CALL',
                '87s': 'CALL', '86s': 'CALL', '85s': 'CALL', '84s': 'CALL', '83s': 'CALL', '82s': 'CALL',
                '87o': 'CALL', '86o': 'CALL', '85o': 'CALL', '84o': 'CALL', '83o': 'CALL', '82o': 'CALL',
                '76s': 'CALL', '75s': 'CALL', '74s': 'CALL', '73s': 'CALL', '72s': 'CALL',
                '76o': 'CALL', '75o': 'CALL', '74o': 'CALL', '73o': 'CALL', '72o': 'CALL',
                '65s': 'CALL', '64s': 'CALL', '63s': 'CALL', '62s': 'CALL',
                '65o': 'CALL', '64o': 'CALL', '63o': 'CALL', '62o': 'CALL',
                '54s': 'CALL', '53s': 'CALL', '52s': 'CALL',
                '54o': 'CALL', '53o': 'CALL', '52o': 'CALL',
                '43s': 'CALL', '42s': 'CALL',
                '43o': 'FOLD', '42o': 'FOLD',
                '32s': 'CALL',
                '32o': 'FOLD'
            }
        }
        
        # thresholds for when to do stuff
        self.gto_thresholds = {
            'SB': {
                'RAISE': 70,  # top 30% of hands = raise
                'CALL': 30,   # next 40% = call
                'FOLD': 0     # bottom 30% = fold
            },
            'BB': {
                'RAISE': 80,
                'CALL': 40,
                'FOLD': 0
            }
        }
    
    def get_preflop_action(self, position: str, hole_cards: List[Card]) -> str:
        """looks up what you should do preflop based on position and cards"""
        if len(hole_cards) != 2:
            return 'FOLD'
        
        # turn the cards into AKs or 72o format
        card1, card2 = hole_cards
        if card1.value == card2.value:
            hand = f"{card1.rank}{card2.rank}"
        elif card1.suit == card2.suit:
            # suited hand - put the higher card first
            if card1.value > card2.value:
                hand = f"{card1.rank}{card2.rank}s"
            else:
                hand = f"{card2.rank}{card1.rank}s"
        else:
            # offsuit hand - higher card first
            if card1.value > card2.value:
                hand = f"{card1.rank}{card2.rank}o"
            else:
                hand = f"{card2.rank}{card1.rank}o"
        
        chart = self.preflop_charts.get(position, {})
        return chart.get(hand, 'FOLD')
    
    def get_position_specific_action(self, position: str, generic_action: str) -> str:
        """Convert generic action to position-specific action"""
        action_mapping = {
            'SB': {  # small blind can fold, call (limp), or raise
                'FOLD': 'FOLD',
                'CALL': 'CALL',  # limp in
                'RAISE': 'RAISE'  # open raise
            },
            'BB': {  # big blind can fold, call, or reraise
                'FOLD': 'FOLD',
                'CALL': 'CALL',   # call the sb raise/limp
                'RAISE': 'RERAISE'  # 3-bet the sb
            }
        }
        
        mapping = action_mapping.get(position, action_mapping['SB'])
        return mapping.get(generic_action, generic_action)

    def get_dynamic_preflop_action(self, position: str, hole_cards: List[Card], hand_percentile: float) -> str:
        """Blends chart lookup with calculated risk (GTO components)"""
        # first get what the chart says to do
        chart_action = self.get_preflop_action(position, hole_cards)
        
        # then get what the math says to do
        thresholds = self.gto_thresholds.get(position, {})
        calculated_action = 'FOLD'  # default to fold
        if hand_percentile >= thresholds.get('RAISE', 101):
            calculated_action = 'RAISE'
        elif hand_percentile >= thresholds.get('CALL', 101):
            calculated_action = 'CALL'
        
        # now blend them together
        # if the chart is more aggressive than the math, trust the chart
        # mixing human strategy with math
        if chart_action == 'RAISE':
            final_action = 'RAISE'  # chart says raise so raise
        elif chart_action == 'CALL' and calculated_action != 'RAISE':
            final_action = 'CALL'
        else:
            # otherwise just use the math
            final_action = calculated_action
        
        # make it position specific
        return self.get_position_specific_action(position, final_action)

    def get_postflop_action(self, position: str, hand_strength: float, pot_odds: float) -> str:
        """Get postflop recommendation based on position, hand strength, and pot odds"""
        
        # different positions act differently postflop
        if position == "SB":
            # sb acts first postflop
            if hand_strength >= 75:  # really strong hand
                return "BET"
            elif hand_strength >= 50:  # medium strength
                return "CHECK"  # can check-call or check-raise
            else:  # weak hand
                return "CHECK"  # check-fold usually
        else:  # BB
            # bb acts second postflop (if sb checks)
            if hand_strength >= 70:  # strong hand
                return "BET"  # value bet
            elif hand_strength >= 40:  # medium strength
                if pot_odds <= 0.3:  # good pot odds
                    return "CALL"
                else:
                    return "CHECK"
            else:  # weak hand
                return "CHECK"  # check back or fold to bet
