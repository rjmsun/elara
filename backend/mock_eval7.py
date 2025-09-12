"""
Mock eval7 module for testing purposes.

This provides basic functionality to allow the enhanced features to be tested
without requiring the actual eval7 package installation.
"""

import random

def evaluate(cards):
    """
    Mock hand evaluation function.
    
    Args:
        cards: List of card strings
        
    Returns:
        int: Mock hand rank (lower is better)
    """
    # Simple mock evaluation based on card ranks
    if len(cards) < 5:
        return 7461  # High card
    
    # Extract ranks
    ranks = []
    for card in cards:
        if len(card) >= 2:
            rank = card[0]
            if rank == 'A':
                ranks.append(14)
            elif rank == 'K':
                ranks.append(13)
            elif rank == 'Q':
                ranks.append(12)
            elif rank == 'J':
                ranks.append(11)
            elif rank == 'T':
                ranks.append(10)
            else:
                try:
                    ranks.append(int(rank))
                except ValueError:
                    ranks.append(1)
    
    # Simple ranking logic
    if len(set(ranks)) == 1:  # All same rank
        return 1  # Four of a kind
    elif len(set(ranks)) == 2:
        return 7  # Full house
    elif len(set(ranks)) == 3:
        return 3  # Three of a kind
    elif len(set(ranks)) == 4:
        return 2  # Two pair
    else:
        return 7461  # High card

# Mock the eval7 module
class MockEval7:
    @staticmethod
    def evaluate(cards):
        return evaluate(cards)

# Create a mock module
import sys
sys.modules['eval7'] = MockEval7() 