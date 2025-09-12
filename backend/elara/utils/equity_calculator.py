"""
Equity calculation utilities for Elara poker engine.

Provides Monte Carlo simulation for calculating hand equity against ranges,
with support for board cards and weighted hand distributions.
"""

import random
import eval7
from ..engine.card import Card
from ..engine.deck import Deck
from ..engine.evaluator import HandEvaluator

class EquityCalculator:
    """
    Calculates poker equity through Monte Carlo simulation.
    
    Provides efficient equity calculation against opponent ranges using
    the eval7 library for high-performance hand evaluation.
    """
    
    def __init__(self):
        """Initialize the equity calculator."""
        self.hand_evaluator = HandEvaluator()
    
    def calculate_equity(self, hero_hand, opponent_range, board=None, num_simulations=10000):
        """
        Calculate hero's equity against an opponent's range.
        
        Args:
            hero_hand: List of 2 Card objects or strings (hero's hole cards)
            opponent_range: Range object or list of possible hands
            board: List of Card objects or strings (community cards)
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            float: Hero's equity (0.0 to 1.0)
        """
        if board is None:
            board = []
        
        # Convert inputs to Card objects
        hero_cards = self._convert_to_cards(hero_hand)
        board_cards = self._convert_to_cards(board)
        
        # Create deck excluding known cards
        excluded_cards = hero_cards + board_cards
        deck = Deck.create_from_excluded_cards(excluded_cards)
        
        wins = 0
        ties = 0
        valid_simulations = 0
        
        for _ in range(num_simulations):
            try:
                # Get opponent hand from range
                opponent_hand = self._get_opponent_hand(opponent_range, deck)
                if opponent_hand is None:
                    continue
                
                # Deal remaining board cards
                remaining_board = deck.deal(5 - len(board_cards))
                full_board = board_cards + remaining_board
                
                # Evaluate hands
                hero_strength = self.hand_evaluator.evaluate_hand(hero_cards + full_board)
                opponent_strength = self.hand_evaluator.evaluate_hand(opponent_hand + full_board)
                
                if hero_strength < opponent_strength:
                    wins += 1
                elif hero_strength == opponent_strength:
                    ties += 1
                
                valid_simulations += 1
                
                # Reset deck for next simulation
                deck.reset()
                deck.remove_cards(excluded_cards)
                
            except (ValueError, IndexError):
                # Skip invalid simulations (e.g., card conflicts)
                continue
        
        if valid_simulations == 0:
            return 0.0
        
        return (wins + ties / 2) / valid_simulations
    
    def calculate_range_vs_range_equity(self, hero_range, villain_range, board=None, num_simulations=10000):
        """
        Calculate equity between two ranges.
        
        Args:
            hero_range: Range object for hero
            villain_range: Range object for villain
            board: List of Card objects or strings (community cards)
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            dict: Contains 'hero_equity', 'villain_equity', 'tie_percentage'
        """
        if board is None:
            board = []
        
        board_cards = self._convert_to_cards(board)
        
        # Create deck excluding board cards
        deck = Deck.create_from_excluded_cards(board_cards)
        
        hero_wins = 0
        villain_wins = 0
        ties = 0
        valid_simulations = 0
        
        for _ in range(num_simulations):
            try:
                # Get hands from both ranges
                hero_hand = self._get_opponent_hand(hero_range, deck)
                villain_hand = self._get_opponent_hand(villain_range, deck)
                
                if hero_hand is None or villain_hand is None:
                    continue
                
                # Deal remaining board cards
                remaining_board = deck.deal(5 - len(board_cards))
                full_board = board_cards + remaining_board
                
                # Evaluate hands
                hero_strength = self.hand_evaluator.evaluate_hand(hero_hand + full_board)
                villain_strength = self.hand_evaluator.evaluate_hand(villain_hand + full_board)
                
                if hero_strength < villain_strength:
                    hero_wins += 1
                elif villain_strength < hero_strength:
                    villain_wins += 1
                else:
                    ties += 1
                
                valid_simulations += 1
                
                # Reset deck for next simulation
                deck.reset()
                deck.remove_cards(board_cards)
                
            except (ValueError, IndexError):
                continue
        
        if valid_simulations == 0:
            return {'hero_equity': 0.0, 'villain_equity': 0.0, 'tie_percentage': 0.0}
        
        return {
            'hero_equity': (hero_wins + ties / 2) / valid_simulations,
            'villain_equity': (villain_wins + ties / 2) / valid_simulations,
            'tie_percentage': ties / valid_simulations
        }
    
    def calculate_equity_realization(self, hero_hand, opponent_range, board=None, 
                                   position='in_position', num_simulations=10000):
        """
        Calculate equity realization (what percentage of raw equity is actually won).
        
        Args:
            hero_hand: List of 2 Card objects or strings
            opponent_range: Range object
            board: List of Card objects or strings
            position: 'in_position' or 'out_of_position'
            num_simulations: Number of simulations
            
        Returns:
            float: Equity realization factor (0.0 to 1.0)
        """
        # This is a simplified implementation
        # A full implementation would require complex post-flop modeling
        
        raw_equity = self.calculate_equity(hero_hand, opponent_range, board, num_simulations)
        
        # Simple heuristic for equity realization
        # In practice, this would be based on extensive GTO solver data
        if board is None or len(board) == 0:
            # Pre-flop: most hands realize close to their raw equity
            return 0.8 + (raw_equity * 0.2)  # 80-100% realization
        else:
            # Post-flop: depends on hand type and board texture
            # This is a very simplified heuristic
            return 0.6 + (raw_equity * 0.4)  # 60-100% realization
    
    def monte_carlo_equity(self, hero_cards, opponent_range_str, board_cards, num_simulations=5000):
        """
        Calculates hero's equity using a Monte Carlo simulation.
        
        Args:
            hero_cards: List of Card objects (hero's hole cards)
            opponent_range_str: String representation of opponent's range (e.g., "AA,KK,QQ,AKs")
            board_cards: List of Card objects (community cards)
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            float: Hero's equity (0.0 to 1.0)
        """
        if not isinstance(hero_cards, list):
            raise TypeError("hero_cards must be a list of Card objects.")
        if not isinstance(board_cards, list):
            raise TypeError("board_cards must be a list of Card objects.")

        from ..giffer.range_handler import Range
        
        range_handler = Range.from_hand_list(opponent_range_str.split(','))
        evaluator = self.hand_evaluator
        
        # Get all possible two-card hands from the string notation
        opponent_hands = range_handler.expand_to_combos()

        wins = 0
        ties = 0

        # Remove known cards from the possible opponent hands
        known_cards = hero_cards + board_cards
        opponent_hands = [
            (combo_str, weight) for combo_str, weight in opponent_hands 
            if not any(card in combo_str for card in [str(c) for c in known_cards])
        ]

        if not opponent_hands:
            return 0.0  # Opponent range is impossible given known cards

        for _ in range(num_simulations):
            # 1. Create a deck and remove known cards
            sim_deck = Deck.create_from_excluded_cards(known_cards)

            # 2. Randomly select an opponent hand from their range
            combo_str, weight = random.choice(opponent_hands)
            opponent_hand = Card.parse_hand_string(combo_str)
            
            # Create a copy of the deck for this simulation run
            run_deck = Deck.create_from_excluded_cards(known_cards + opponent_hand)
            run_deck.shuffle()

            # 3. Deal the rest of the board
            num_remaining_cards = 5 - len(board_cards)
            sim_board = board_cards + run_deck.deal(num_remaining_cards)

            # 4. Evaluate hands
            hero_rank = evaluator.evaluate_hand(hero_cards + sim_board)
            villain_rank = evaluator.evaluate_hand(opponent_hand + sim_board)

            if hero_rank < villain_rank:  # Lower rank is better in eval7
                wins += 1
            elif hero_rank == villain_rank:
                ties += 1
        
        equity = (wins + (ties / 2)) / num_simulations
        return equity
    
    def _convert_to_cards(self, card_list):
        """Convert a list of card representations to Card objects."""
        if card_list is None:
            return []
        
        cards = []
        for card in card_list:
            if isinstance(card, Card):
                cards.append(card)
            elif isinstance(card, str):
                cards.append(Card(card))
            else:
                raise ValueError(f"Invalid card type: {type(card)}")
        
        return cards
    
    def _get_opponent_hand(self, opponent_range, deck):
        """
        Get a random hand from the opponent's range.
        Args:
            opponent_range: Range object or list of hands
            deck: Deck object with available cards
        Returns:
            List of 2 Card objects or None if no valid hand found
        """
        # If the range has expand_to_combos, use it for valid combos
        if hasattr(opponent_range, 'expand_to_combos'):
            combos = opponent_range.expand_to_combos()
            # Filter combos to only those possible with the current deck
            valid_combos = []
            for combo_str, weight in combos:
                try:
                    cards = Card.parse_hand_string(combo_str)
                    if all(any(card.rank == dcard.rank and card.suit == dcard.suit for dcard in deck.cards) for card in cards):
                        valid_combos.append((cards, weight))
                except Exception:
                    continue
            if not valid_combos:
                return None
            # Weighted random choice
            hands, weights = zip(*valid_combos)
            selected = random.choices(hands, weights=weights, k=1)[0]
            return selected
        # Fallback to previous logic
        if isinstance(opponent_range, list):
            if not opponent_range:
                return None
            hand_str = random.choice(opponent_range)
            try:
                hand_cards = Card.parse_hand_string(hand_str)
                for card in hand_cards:
                    card_found = False
                    for deck_card in deck.cards:
                        if card.rank == deck_card.rank and card.suit == deck_card.suit:
                            card_found = True
                            break
                    if not card_found:
                        return None
                return hand_cards
            except ValueError:
                return None
        elif hasattr(opponent_range, 'get_weighted_hands'):
            weighted_hands = opponent_range.get_weighted_hands()
            if not weighted_hands:
                return None
            hands = list(weighted_hands.keys())
            weights = list(weighted_hands.values())
            try:
                selected_hand = random.choices(hands, weights=weights, k=1)[0]
                hand_cards = Card.parse_hand_string(selected_hand)
                for card in hand_cards:
                    card_found = False
                    for deck_card in deck.cards:
                        if card.rank == deck_card.rank and card.suit == deck_card.suit:
                            card_found = True
                            break
                    if not card_found:
                        return None
                return hand_cards
            except (ValueError, IndexError):
                return None
        else:
            if len(deck.cards) < 2:
                return None
            return deck.deal(2) 