"""
Tests for the ElaraHandEvaluator.
"""

import unittest
from elara.engine.card import Card
from elara.engine.game_state import GameState, Position, Action
from elara.utils.hand_evaluator import ElaraHandEvaluator

class TestElaraHandEvaluator(unittest.TestCase):
    """Test cases for the ElaraHandEvaluator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = ElaraHandEvaluator()
    
    def test_preflop_evaluation(self):
        """Test pre-flop hand evaluation."""
        # Create a game state
        game_state = GameState(hero_stack=100, villain_stack=100)
        game_state.set_positions(Position.BUTTON)
        
        # Hero has AKs
        hero_hand = [Card('As'), Card('Ks')]
        
        # Villain raises to 3bb
        game_state.add_action('villain', Action.RAISE, 3.0)
        
        # Evaluate the hand
        evaluation = self.evaluator.evaluate_hand(hero_hand, game_state)
        
        # Basic checks
        self.assertIn('equity', evaluation)
        self.assertIn('equity_realization', evaluation)
        self.assertIn('realized_equity', evaluation)
        self.assertIn('range_analysis', evaluation)
        self.assertIn('strategic_metrics', evaluation)
        self.assertIn('recommendations', evaluation)
        
        # Check that equity is reasonable (AKs should be strong pre-flop)
        self.assertGreater(evaluation['equity'], 0.5)
        self.assertLess(evaluation['equity'], 0.9)
        
        # Check that we have recommendations
        self.assertIsNotNone(evaluation['recommendations']['primary_action'])
        self.assertGreater(evaluation['recommendations']['confidence'], 0)

if __name__ == '__main__':
    unittest.main() 