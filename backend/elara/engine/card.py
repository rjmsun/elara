"""
Card representation for Elara poker engine.

Supports both human-readable string representation and internal integer representation
for performance optimization.
"""

RANKS = '23456789TJQKA'
SUITS = 'shdc'  # spades, hearts, diamonds, clubs

class Card:
    """
    Represents a single playing card with rank and suit.
    
    Internal representation uses integers for performance, but provides
    human-readable string representations for display and input.
    """
    
    def __init__(self, rank_suit_str=None, rank=None, suit=None):
        """
        Initialize a card from either a string representation or separate rank/suit.
        
        Args:
            rank_suit_str: String like 'As', 'Td', 'Kh' (rank + suit)
            rank: Individual rank character ('2'-'9', 'T', 'J', 'Q', 'K', 'A')
            suit: Individual suit character ('s', 'h', 'd', 'c')
        """
        if rank_suit_str:
            if len(rank_suit_str) != 2:
                raise ValueError("Card string must be 2 characters long, e.g., 'As', 'Td'")
            
            rank = rank_suit_str[0].upper()
            suit = rank_suit_str[1].lower()
        
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
            
        self.rank = rank
        self.suit = suit
        self.val = RANKS.index(self.rank)
        
        # Internal integer representation for performance
        self._int_val = self.val * 4 + SUITS.index(self.suit)
    
    @classmethod
    def from_int(cls, int_val):
        """Create a card from its internal integer representation."""
        rank_idx = int_val // 4
        suit_idx = int_val % 4
        return cls(rank=RANKS[rank_idx], suit=SUITS[suit_idx])
    
    def to_int(self):
        """Return the internal integer representation."""
        return self._int_val
    
    def __str__(self):
        """Human-readable string representation."""
        return f"{self.rank}{self.suit}"
    
    def __repr__(self):
        return f"Card('{self.rank}{self.suit}')"
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
    
    def __lt__(self, other):
        """Compare cards by rank (suit doesn't matter for ordering)."""
        return self.val < other.val
    
    def __le__(self, other):
        return self.val <= other.val
    
    def __gt__(self, other):
        return self.val > other.val
    
    def __ge__(self, other):
        return self.val >= other.val
    
    @property
    def display_name(self):
        """Get a display-friendly name with suit symbols."""
        suit_symbols = {
            's': '♠',
            'h': '♥', 
            'd': '♦',
            'c': '♣'
        }
        return f"{self.rank}{suit_symbols[self.suit]}"
    
    @classmethod
    def parse_hand_string(cls, hand_str):
        """
        Parse a poker hand string into Card objects.
        
        Args:
            hand_str: String like 'AsKh' or 'As Kh' (with or without spaces)
            
        Returns:
            List of Card objects
        """
        # Remove spaces and convert to uppercase
        hand_str = hand_str.replace(' ', '').upper()
        
        if len(hand_str) % 2 != 0:
            raise ValueError("Hand string must have even number of characters")
        
        cards = []
        for i in range(0, len(hand_str), 2):
            card_str = hand_str[i:i+2]
            cards.append(cls(card_str))
        
        return cards 