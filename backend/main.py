#!/usr/bin/env python3
"""
Elara Poker Calculator - Main Entry Point

A sophisticated poker calculator and bot designed for Heads-Up No-Limit Texas Hold'em
with 100 big blind starting stacks, built on Game Theory Optimal principles.
"""

from elara.engine.card import Card
from elara.engine.game_state import GameState, Position, Action
from elara.utils.hand_evaluator import ElaraHandEvaluator
from elara.giffer.range_handler import Range

def main():
    """Demonstrate Elara's core functionality."""
    print("🎰 Elara Poker Calculator")
    print("=" * 50)
    
    # Initialize the hand evaluator
    evaluator = ElaraHandEvaluator()
    
    # Example 1: Pre-flop analysis
    print("\n📊 Example 1: Pre-flop Analysis")
    print("-" * 30)
    
    # Create a game state
    game_state = GameState(hero_stack=100, villain_stack=100)
    game_state.set_positions(Position.BUTTON)  # Hero is button
    
    # Hero has AKs
    hero_hand = [Card('As'), Card('Ks')]
    
    # Villain raises to 3bb
    game_state.add_action('villain', Action.RAISE, 3.0)
    
    # Evaluate the hand
    evaluation = evaluator.evaluate_hand(hero_hand, game_state)
    
    print(f"Hero's hand: {evaluation['hero_hand']}")
    print(f"Street: {evaluation['street']}")
    print(f"Pot size: {evaluation['pot_size']} BB")
    print(f"Raw equity: {evaluation['equity']:.1%}")
    print(f"Equity realization: {evaluation['equity_realization']:.1%}")
    print(f"Realized equity: {evaluation['realized_equity']:.1%}")
    print(f"Opponent range size: {evaluation['opponent_range_size']} hands")
    
    # Range analysis
    range_analysis = evaluation['range_analysis']
    print(f"\nRange Analysis:")
    print(f"  Value targets: {range_analysis['value_targets']:.1%}")
    print(f"  Fold equity: {range_analysis['fold_equity']:.1%}")
    print(f"  Threats: {range_analysis['threats']:.1%}")
    
    # Strategic metrics
    metrics = evaluation['strategic_metrics']
    print(f"\nStrategic Metrics:")
    print(f"  Pot odds: {metrics['pot_odds']:.1f}:1")
    print(f"  Call EV: {metrics['call_ev']:.2f} BB")
    print(f"  Bet EV: {metrics['bet_ev']:.2f} BB")
    print(f"  Position advantage: {metrics['position_advantage']}")
    
    # Recommendations
    recs = evaluation['recommendations']
    print(f"\nRecommendations:")
    print(f"  Primary action: {recs['primary_action']}")
    if recs['bet_sizing']:
        print(f"  Bet sizing: {recs['bet_sizing']}")
    print(f"  Confidence: {recs['confidence']:.1%}")
    for reason in recs['reasoning']:
        print(f"  - {reason}")
    
    # Example 2: Post-flop analysis
    print("\n\n📊 Example 2: Post-flop Analysis")
    print("-" * 30)
    
    # Deal the flop
    flop = [Card('Ah'), Card('7d'), Card('2c')]
    game_state.deal_flop(flop)
    
    # Villain bets 5bb
    game_state.add_action('villain', Action.BET, 5.0)
    
    # Re-evaluate
    evaluation2 = evaluator.evaluate_hand(hero_hand, game_state)
    
    print(f"Board: {evaluation2['board']}")
    print(f"Street: {evaluation2['street']}")
    print(f"Pot size: {evaluation2['pot_size']} BB")
    print(f"Raw equity: {evaluation2['equity']:.1%}")
    print(f"Realized equity: {evaluation2['realized_equity']:.1%}")
    
    recs2 = evaluation2['recommendations']
    print(f"\nRecommendations:")
    print(f"  Primary action: {recs2['primary_action']}")
    for reason in recs2['reasoning']:
        print(f"  - {reason}")
    
    # Example 3: What-if analysis
    print("\n\n📊 Example 3: What-if Analysis")
    print("-" * 30)
    
    # Analyze what happens if we raise
    what_if = evaluator.analyze_what_if(hero_hand, game_state, 'raise', 15.0)
    
    print(f"Proposed action: {what_if['proposed_action']} {what_if['bet_size']} BB")
    print(f"Projected equity: {what_if['projected_equity']:.1%}")
    print(f"Projected realized equity: {what_if['projected_realized_equity']:.1%}")
    print(f"Projected EV: {what_if['projected_ev']:.2f} BB")
    
    print("\n🎯 Elara Analysis Complete!")

if __name__ == "__main__":
    main() 