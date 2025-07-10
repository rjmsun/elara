"""
Game state tracking for Elara poker engine.

Tracks the complete state of a poker hand including betting history,
pot size, board cards, and street progression.
"""

from enum import Enum
from .card import Card

class Street(Enum):
    """Enumeration of poker streets."""
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"

class Position(Enum):
    """Enumeration of player positions in heads-up play."""
    BUTTON = "button"  # Small blind, acts first preflop, last postflop
    BIG_BLIND = "big_blind"  # Big blind, acts last preflop, first postflop

class Action(Enum):
    """Enumeration of possible poker actions."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"

class GameState:
    """
    Tracks the complete state of a heads-up poker hand.
    
    Maintains detailed information about betting history, pot size,
    board cards, and street progression for use in range modeling
    and equity calculations.
    """
    
    def __init__(self, hero_stack=100, villain_stack=100, bb_size=1):
        """
        Initialize a new game state.
        
        Args:
            hero_stack: Starting stack for hero (in big blinds)
            villain_stack: Starting stack for villain (in big blinds)
            bb_size: Big blind size (default 1 for normalized calculations)
        """
        # Stack information
        self.hero_stack = hero_stack
        self.villain_stack = villain_stack
        self.bb_size = bb_size
        
        # Pot and betting information
        self.pot_size = 0
        self.current_bet = 0
        self.last_raise_amount = 0
        
        # Board and street information
        self.board = []
        self.street = Street.PREFLOP
        
        # Position information (in heads-up, button is small blind)
        self.hero_position = None
        self.villain_position = None
        
        # Detailed action history
        self.action_history = []
        
        # Street-specific information
        self.street_actions = {
            Street.PREFLOP: [],
            Street.FLOP: [],
            Street.TURN: [],
            Street.RIVER: []
        }
        
        # Betting round state
        self.current_player = None  # 'hero' or 'villain'
        self.last_aggressor = None  # Last player to bet/raise
        
    def set_positions(self, hero_position):
        """
        Set the positions for both players.
        
        Args:
            hero_position: Position enum for hero
        """
        self.hero_position = hero_position
        self.villain_position = Position.BIG_BLIND if hero_position == Position.BUTTON else Position.BUTTON
    
    def add_action(self, player, action, amount=0, street=None):
        """
        Record an action in the game state.
        
        Args:
            player: 'hero' or 'villain'
            action: Action enum
            amount: Bet/raise amount (in big blinds)
            street: Optional street override
        """
        if street is None:
            street = self.street
        
        action_record = {
            'player': player,
            'action': action,
            'amount': amount,
            'street': street,
            'pot_before': self.pot_size,
            'stack_before': self.hero_stack if player == 'hero' else self.villain_stack
        }
        
        # Update game state based on action
        self._process_action(action_record)
        
        # Record the action
        self.action_history.append(action_record)
        self.street_actions[street].append(action_record)
        
        # Update current player
        self.current_player = 'villain' if player == 'hero' else 'hero'
        
        # Update last aggressor for betting actions
        if action in [Action.BET, Action.RAISE]:
            self.last_aggressor = player
    
    def _process_action(self, action_record):
        """Process an action and update game state accordingly."""
        player = action_record['player']
        action = action_record['action']
        amount = action_record['amount']
        
        if player == 'hero':
            stack = self.hero_stack
        else:
            stack = self.villain_stack
        
        if action == Action.FOLD:
            # No stack change for fold
            pass
        elif action == Action.CHECK:
            # No stack change for check
            pass
        elif action == Action.CALL:
            call_amount = min(amount, stack)
            if player == 'hero':
                self.hero_stack -= call_amount
            else:
                self.villain_stack -= call_amount
            self.pot_size += call_amount
        elif action == Action.BET:
            bet_amount = min(amount, stack)
            if player == 'hero':
                self.hero_stack -= bet_amount
            else:
                self.villain_stack -= bet_amount
            self.pot_size += bet_amount
            self.current_bet = bet_amount
        elif action == Action.RAISE:
            raise_amount = min(amount, stack)
            if player == 'hero':
                self.hero_stack -= raise_amount
            else:
                self.villain_stack -= raise_amount
            self.pot_size += raise_amount
            self.current_bet = raise_amount
            self.last_raise_amount = raise_amount
        elif action == Action.ALL_IN:
            all_in_amount = stack
            if player == 'hero':
                self.hero_stack = 0
            else:
                self.villain_stack = 0
            self.pot_size += all_in_amount
    
    def deal_flop(self, flop_cards):
        """Deal the flop and advance to flop street."""
        if len(flop_cards) != 3:
            raise ValueError("Flop must contain exactly 3 cards")
        
        self.board = flop_cards
        self.street = Street.FLOP
        self.current_bet = 0
        self.last_raise_amount = 0
    
    def deal_turn(self, turn_card):
        """Deal the turn and advance to turn street."""
        if self.street != Street.FLOP:
            raise ValueError("Can only deal turn after flop")
        
        self.board.append(turn_card)
        self.street = Street.TURN
        self.current_bet = 0
        self.last_raise_amount = 0
    
    def deal_river(self, river_card):
        """Deal the river and advance to river street."""
        if self.street != Street.TURN:
            raise ValueError("Can only deal river after turn")
        
        self.board.append(river_card)
        self.street = Street.RIVER
        self.current_bet = 0
        self.last_raise_amount = 0
    
    def get_street_actions(self, street=None):
        """
        Get actions for a specific street.
        
        Args:
            street: Street enum, or None for current street
            
        Returns:
            List of action records
        """
        if street is None:
            street = self.street
        return self.street_actions[street]
    
    def get_last_action(self, street=None):
        """
        Get the last action on a specific street.
        
        Args:
            street: Street enum, or None for current street
            
        Returns:
            Action record or None
        """
        actions = self.get_street_actions(street)
        return actions[-1] if actions else None
    
    def get_betting_round_complete(self):
        """
        Check if the current betting round is complete.
        
        Returns:
            bool: True if betting round is complete
        """
        if not self.street_actions[self.street]:
            return False
        
        # Check if both players have acted and no pending action
        actions = self.street_actions[self.street]
        if len(actions) < 2:
            return False
        
        last_action = actions[-1]
        second_last_action = actions[-2]
        
        # If last action was a bet/raise, need a response
        if last_action['action'] in [Action.BET, Action.RAISE]:
            return False
        
        # If last action was check/call and previous was also check/call, round is complete
        if (last_action['action'] in [Action.CHECK, Action.CALL] and 
            second_last_action['action'] in [Action.CHECK, Action.CALL]):
            return True
        
        return False
    
    def get_pot_odds(self, call_amount):
        """
        Calculate pot odds for a call.
        
        Args:
            call_amount: Amount needed to call
            
        Returns:
            float: Pot odds ratio
        """
        if call_amount <= 0:
            return float('inf')
        return self.pot_size / call_amount
    
    def get_effective_stack(self):
        """Get the smaller of the two stacks (effective stack)."""
        return min(self.hero_stack, self.villain_stack)
    
    def get_canonical_history(self):
        """
        Transform action history into a compact, standardized string representation.
        
        This method creates a canonical string that can be used as part of
        an information set key for CFR algorithms. The format is designed
        to be compact and standardized.
        
        Examples:
            - "r3c" (button raises to 3bb, big blind calls)
            - "r3c/b5c/b15f" (preflop action / flop action / turn action)
        
        Returns:
            str: Canonical action history string
        """
        if not self.action_history:
            return ""
        
        # Group actions by street
        street_histories = {}
        for action in self.action_history:
            street = action['street']
            if street not in street_histories:
                street_histories[street] = []
            street_histories[street].append(action)
        
        # Build canonical string for each street
        canonical_parts = []
        
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            if street in street_histories:
                street_actions = street_histories[street]
                street_string = self._canonicalize_street_actions(street_actions)
                if street_string:
                    canonical_parts.append(street_string)
        
        return "/".join(canonical_parts)
    
    def _canonicalize_street_actions(self, actions):
        """
        Convert a list of actions on a single street to canonical format.
        
        Args:
            actions: List of action records for a single street
            
        Returns:
            str: Canonical string for the street
        """
        if not actions:
            return ""
        
        action_strings = []
        for action in actions:
            # Player indicator: 'h' for hero, 'v' for villain
            player = 'h' if action['player'] == 'hero' else 'v'
            
            # Action type: 'f' for fold, 'c' for call/check, 'b' for bet, 'r' for raise
            action_type = action['action'].value[0]
            
            # Amount (in big blinds, rounded to nearest integer)
            amount = int(round(action['amount']))
            
            # Build action string
            if action['action'] == Action.FOLD:
                action_strings.append(f"{player}f")
            elif action['action'] == Action.CHECK:
                action_strings.append(f"{player}c")
            elif action['action'] == Action.CALL:
                action_strings.append(f"{player}c")
            elif action['action'] == Action.BET:
                action_strings.append(f"{player}b{amount}")
            elif action['action'] == Action.RAISE:
                action_strings.append(f"{player}r{amount}")
            elif action['action'] == Action.ALL_IN:
                action_strings.append(f"{player}a")
        
        return "".join(action_strings)
    
    def get_state_key(self):
        """
        Generate a unique key representing the current public state.
        
        This key combines the board cards and canonical action history
        for use in caching and strategy lookup.
        
        Returns:
            str: Unique state key
        """
        # Board representation
        board_str = "".join(str(card) for card in self.board)
        
        # Canonical history
        history_str = self.get_canonical_history()
        
        # Combine with street indicator
        street_str = self.street.value[0]  # 'p', 'f', 't', 'r'
        
        return f"{street_str}:{board_str}:{history_str}"
    
    def __repr__(self):
        return (f"GameState(Street: {self.street.value}, Pot: {self.pot_size}, "
                f"Board: {[str(c) for c in self.board]}, "
                f"Hero: {self.hero_stack}, Villain: {self.villain_stack})")
    
    def __str__(self):
        return self.__repr__() 