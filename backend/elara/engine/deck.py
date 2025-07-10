"""
Deck management for Elara poker engine.

Provides efficient card dealing and deck manipulation for poker simulations.
"""

import random
from .card import Card, RANKS, SUITS

class Deck:
    """
    Represents a standard 52-card deck for poker simulations.
    
    Provides efficient card dealing and deck manipulation with support for
    removing known cards (hero's hand, board cards) from the deck.
    """
    
    def __init__(self, cards=None):
        """
        Initialize a deck with either a custom set of cards or a full 52-card deck.
        
        Args:
            cards: Optional list of Card objects. If None, creates a full deck.
        """
        if cards is None:
            self.cards = [Card(rank=rank, suit=suit) 
                         for rank in RANKS for suit in SUITS]
        else:
            self.cards = cards.copy()
        
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def deal(self, num_cards):
        """
        Deal a specified number of cards from the deck.
        
        Args:
            num_cards: Number of cards to deal
            
        Returns:
            List of Card objects
            
        Raises:
            ValueError: If not enough cards remain
        """
        if num_cards > len(self.cards):
            raise ValueError(f"Not enough cards in deck. Requested: {num_cards}, Available: {len(self.cards)}")
        
        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self.cards.pop())
        
        return dealt_cards
    
    def remove_cards(self, cards_to_remove):
        """
        Remove specific cards from the deck.
        
        Args:
            cards_to_remove: List of Card objects or card strings to remove
            
        Raises:
            ValueError: If any card is not found in the deck
        """
        for card in cards_to_remove:
            if isinstance(card, str):
                card = Card(card)
            
            try:
                self.cards.remove(card)
            except ValueError:
                raise ValueError(f"Card {card} not found in deck")
    
    def reset(self):
        """Reset the deck to a full 52-card deck and shuffle."""
        self.cards = [Card(rank=rank, suit=suit) 
                     for rank in RANKS for suit in SUITS]
        self.shuffle()
    
    def __len__(self):
        return len(self.cards)
    
    def __str__(self):
        return f"Deck with {len(self.cards)} cards"
    
    def __repr__(self):
        return f"Deck({len(self.cards)} cards)"
    
    @classmethod
    def create_from_excluded_cards(cls, excluded_cards):
        """
        Create a deck with specific cards excluded.
        
        Args:
            excluded_cards: List of Card objects or card strings to exclude
            
        Returns:
            Deck instance with excluded cards removed
        """
        deck = cls()
        deck.remove_cards(excluded_cards)
        return deck 