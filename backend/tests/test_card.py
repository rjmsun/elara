"""
Tests for the Card class.
"""

import unittest
from elara.engine.card import Card

class TestCard(unittest.TestCase):
    """Test cases for the Card class."""
    
    def test_card_creation(self):
        """Test creating cards from string representation."""
        # Test valid cards
        card1 = Card('As')
        self.assertEqual(card1.rank, 'A')
        self.assertEqual(card1.suit, 's')
        self.assertEqual(card1.val, 12)  # A is index 12
        
        card2 = Card('Kh')
        self.assertEqual(card2.rank, 'K')
        self.assertEqual(card2.suit, 'h')
        self.assertEqual(card2.val, 11)  # K is index 11
        
        card3 = Card('2c')
        self.assertEqual(card3.rank, '2')
        self.assertEqual(card3.suit, 'c')
        self.assertEqual(card3.val, 0)  # 2 is index 0
    
    def test_card_creation_separate(self):
        """Test creating cards with separate rank and suit."""
        card = Card(rank='Q', suit='d')
        self.assertEqual(card.rank, 'Q')
        self.assertEqual(card.suit, 'd')
        self.assertEqual(card.val, 10)  # Q is index 10
    
    def test_invalid_card(self):
        """Test that invalid cards raise ValueError."""
        with self.assertRaises(ValueError):
            Card('Xx')  # Invalid rank
        
        with self.assertRaises(ValueError):
            Card('Ax')  # Invalid suit
        
        with self.assertRaises(ValueError):
            Card('AsK')  # Too long
    
    def test_card_string_representation(self):
        """Test card string representation."""
        card = Card('Ts')
        self.assertEqual(str(card), 'Ts')
        self.assertEqual(repr(card), "Card('Ts')")
    
    def test_card_comparison(self):
        """Test card comparison by rank."""
        card1 = Card('2s')
        card2 = Card('As')
        card3 = Card('Kh')
        
        self.assertTrue(card1 < card2)
        self.assertTrue(card3 < card2)
        self.assertTrue(card1 < card3)
        self.assertFalse(card2 < card1)
    
    def test_card_equality(self):
        """Test card equality."""
        card1 = Card('As')
        card2 = Card('As')
        card3 = Card('Ah')
        
        self.assertEqual(card1, card2)
        self.assertNotEqual(card1, card3)
    
    def test_parse_hand_string(self):
        """Test parsing hand strings."""
        cards = Card.parse_hand_string('AsKh')
        self.assertEqual(len(cards), 2)
        self.assertEqual(str(cards[0]), 'As')
        self.assertEqual(str(cards[1]), 'Kh')
        
        # Test with spaces
        cards = Card.parse_hand_string('As Kh')
        self.assertEqual(len(cards), 2)
        self.assertEqual(str(cards[0]), 'As')
        self.assertEqual(str(cards[1]), 'Kh')
    
    def test_display_name(self):
        """Test display name with suit symbols."""
        card = Card('Ah')
        self.assertEqual(card.display_name, 'A♥')

if __name__ == '__main__':
    unittest.main() 