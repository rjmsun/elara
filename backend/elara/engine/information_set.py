"""
Information set representation for Elara's CFR implementation.

An information set represents a decision point in the game where a player
knows their own cards and the public board, but not the opponent's cards.
This is the fundamental unit for CFR training and strategy lookup.
"""

from .card import Card
from .game_state import Street, Position, Action

class InformationSet:
    """
    Represents an information set in the poker game tree.
    
    An information set is a unique identifier for a decision point that
    includes the player's hole cards, the public board, and the action
    history up to that point. This class supports both concrete and
    abstracted representations for CFR algorithms.
    """
    
    def __init__(self, hole_cards, board=None, action_history=None, position=None, 
                 use_abstraction=False):
        """
        Initialize an information set.
        
        Args:
            hole_cards: List of 2 Card objects (player's hole cards)
            board: List of Card objects (community cards)
            action_history: List of action records
            position: Player position (button or big blind)
            use_abstraction: Whether to use abstracted representation for CFR
        """
        self.hole_cards = sorted(hole_cards, key=lambda c: (c.val, c.suit))
        self.board = sorted(board) if board else []
        self.action_history = action_history or []
        self.position = position
        self.use_abstraction = use_abstraction
        
        # Create a unique identifier for this information set
        self.identifier = self._create_identifier()
    
    def _create_identifier(self):
        """
        Create a unique string identifier for this information set.
        
        Returns:
            str: Unique identifier
        """
        if self.use_abstraction:
            # Use abstracted representation for CFR
            hole_str = self._get_abstracted_hole_cards()
            board_str = self._get_abstracted_board()
        else:
            # Use concrete card representation
            hole_str = ''.join(str(card) for card in self.hole_cards)
            board_str = ''.join(str(card) for card in self.board)
        
        # Convert action history to string
        action_str = self._action_history_to_string()
        
        # Combine all components
        return f"{hole_str}|{board_str}|{action_str}|{self.position}"
    
    def _get_abstracted_hole_cards(self):
        """
        Get abstracted representation of hole cards for CFR.
        
        This method maps specific hole cards to strategic buckets
        based on their strength and characteristics.
        
        Returns:
            str: Abstracted hole card representation
        """
        if not self.hole_cards or len(self.hole_cards) != 2:
            return "XX"
        
        card1, card2 = self.hole_cards
        
        # Determine if suited
        suited = card1.suit == card2.suit
        
        # Get ranks
        rank1, rank2 = card1.val, card2.val
        high_rank, low_rank = max(rank1, rank2), min(rank1, rank2)
        
        # Map to strategic buckets
        if high_rank == low_rank:  # Pocket pair
            if high_rank >= 10:  # TT+
                return f"PP_HIGH"
            elif high_rank >= 7:  # 77-TT
                return f"PP_MED"
            else:  # 22-66
                return f"PP_LOW"
        else:
            # Unpaired hands
            if suited:
                if high_rank >= 12:  # AKs, AQs
                    return f"SUITED_BROADWAY"
                elif high_rank >= 10:  # KQs, KJs, QJs
                    return f"SUITED_KING"
                elif high_rank >= 8:  # JTs, T9s
                    return f"SUITED_CONNECTOR"
                else:
                    return f"SUITED_OTHER"
            else:
                if high_rank >= 12:  # AKo, AQo
                    return f"OFFSUIT_BROADWAY"
                elif high_rank >= 10:  # KQo, KJo
                    return f"OFFSUIT_KING"
                else:
                    return f"OFFSUIT_OTHER"
    
    def _get_abstracted_board(self):
        """
        Get abstracted representation of board texture for CFR.
        
        This method maps specific board cards to texture buckets
        based on their strategic characteristics.
        
        Returns:
            str: Abstracted board representation
        """
        if not self.board:
            return "PREFLOP"
        
        board_size = len(self.board)
        
        if board_size == 3:  # Flop
            return self._abstract_flop_texture()
        elif board_size == 4:  # Turn
            return self._abstract_turn_texture()
        elif board_size == 5:  # River
            return self._abstract_river_texture()
        else:
            return "UNKNOWN"
    
    def _abstract_flop_texture(self):
        """Abstract flop texture based on strategic characteristics."""
        if len(self.board) != 3:
            return "UNKNOWN"
        
        # Extract ranks and suits
        ranks = [card.val for card in self.board]
        suits = [card.suit for card in self.board]
        
        # Check for paired board
        if len(set(ranks)) == 2:
            return "PAIRED"
        
        # Check for monotone (3 same suit)
        if len(set(suits)) == 1:
            return "MONOTONE"
        
        # Check for connected (consecutive or close ranks)
        ranks.sort()
        if ranks[2] - ranks[0] <= 2:
            return "CONNECTED"
        
        # Check for high cards (T or higher)
        high_cards = sum(1 for rank in ranks if rank >= 8)
        if high_cards >= 2:
            return "HIGH"
        
        return "DRY"
    
    def _abstract_turn_texture(self):
        """Abstract turn texture (simplified for now)."""
        return "TURN"
    
    def _abstract_river_texture(self):
        """Abstract river texture (simplified for now)."""
        return "RIVER"
    
    def _action_history_to_string(self):
        """Convert action history to a compact string representation."""
        if not self.action_history:
            return ""
        
        action_strings = []
        for action in self.action_history:
            player = action['player'][0]  # 'h' for hero, 'v' for villain
            action_type = action['action'].value[0]  # 'f', 'c', 'b', 'r'
            amount = int(action['amount'] * 100)  # Convert to integer
            action_strings.append(f"{player}{action_type}{amount}")
        
        return "".join(action_strings)
    
    def get_available_actions(self, game_state):
        """
        Get the available actions at this information set.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of Action enums
        """
        actions = []
        
        # Always can fold
        actions.append(Action.FOLD)
        
        # Can check if no bet to call
        if game_state.current_bet == 0:
            actions.append(Action.CHECK)
        else:
            # Can call if there's a bet
            actions.append(Action.CALL)
        
        # Can bet/raise if we have chips
        if game_state.hero_stack > 0:
            actions.append(Action.BET)
            actions.append(Action.RAISE)
        
        return actions
    
    def get_bet_sizings(self, game_state, action_type):
        """
        Get available bet sizes for a given action type.
        
        Args:
            game_state: Current game state
            action_type: Type of betting action
            
        Returns:
            List of bet sizes (in big blinds)
        """
        if action_type not in [Action.BET, Action.RAISE]:
            return []
        
        pot_size = game_state.pot_size
        stack = game_state.hero_stack
        
        # Standard bet sizings
        sizings = []
        
        # Small bet (1/3 pot)
        small_bet = max(0.5, pot_size / 3)
        if small_bet <= stack:
            sizings.append(small_bet)
        
        # Medium bet (2/3 pot)
        medium_bet = max(1.0, pot_size * 2 / 3)
        if medium_bet <= stack:
            sizings.append(medium_bet)
        
        # Pot-sized bet
        pot_bet = pot_size
        if pot_bet <= stack:
            sizings.append(pot_bet)
        
        # Overbet (1.5x pot)
        overbet = pot_size * 1.5
        if overbet <= stack:
            sizings.append(overbet)
        
        # All-in
        if stack > 0:
            sizings.append(stack)
        
        return sizings
    
    def get_street(self):
        """
        Get the current street based on board size.
        
        Returns:
            Street enum
        """
        board_size = len(self.board)
        if board_size == 0:
            return Street.PREFLOP
        elif board_size == 3:
            return Street.FLOP
        elif board_size == 4:
            return Street.TURN
        elif board_size == 5:
            return Street.RIVER
        else:
            raise ValueError(f"Invalid board size: {board_size}")
    
    def is_terminal(self):
        """
        Check if this information set represents a terminal state.
        
        Returns:
            bool: True if terminal state
        """
        # Terminal if someone folded or hand is complete
        if not self.action_history:
            return False
        
        last_action = self.action_history[-1]
        if last_action['action'] == Action.FOLD:
            return True
        
        # Terminal if we're at river and betting is complete
        if self.get_street() == Street.RIVER:
            # Check if betting round is complete
            # This is a simplified check
            return len(self.action_history) >= 2
        
        return False
    
    def get_pot_odds(self, call_amount):
        """
        Calculate pot odds for a call.
        
        Args:
            call_amount: Amount needed to call
            
        Returns:
            float: Pot odds ratio
        """
        # This would need to be calculated from the game state
        # For now, return a placeholder
        return 2.0 if call_amount > 0 else float('inf')
    
    def __eq__(self, other):
        if not isinstance(other, InformationSet):
            return False
        return self.identifier == other.identifier
    
    def __hash__(self):
        return hash(self.identifier)
    
    def __repr__(self):
        return f"InformationSet('{self.identifier}')"
    
    def __str__(self):
        return self.__repr__() 