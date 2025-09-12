"""
Main hand evaluator for Elara poker engine.

Implements the dynamic, range-aware hand evaluation system described in the blueprint.
This is the core component that provides sophisticated analysis of hand strength
against realistic opponent ranges that evolve based on betting actions.
"""

from ..engine.card import Card
from ..engine.game_state import GameState, Street, Position, Action
from ..engine.evaluator import HandEvaluator
from ..giffer.range_handler import Range, GTOCharts
from ..gto.strategy import GtoStrategy
from ..engine.player_profile import OpponentModeler
from .equity_calculator import EquityCalculator

class ElaraHandEvaluator:
    """
    Elara's main hand evaluator with dynamic range analysis.
    
    This class implements the sophisticated hand evaluation system that:
    1. Establishes opponent's current range based on GTO charts and action history
    2. Calculates core metrics (equity, equity realization)
    3. Partitions the opponent's range into strategic categories
    4. Provides actionable insights for decision making
    5. Integrates Monte Carlo simulation for post-flop analysis
    6. Uses dynamic opponent modeling for personalized strategy
    """
    
    def __init__(self):
        """Initialize the hand evaluator."""
        self.hand_evaluator = HandEvaluator()
        self.equity_calculator = EquityCalculator()
        self.gto_charts = GTOCharts()
        self.gto_strategy = GtoStrategy()
        self.opponent_modeler = OpponentModeler()
    
    def evaluate_hand(self, hero_hand, game_state, opponent_range=None, opponent_name=None):
        """
        Perform a comprehensive hand evaluation.
        
        Args:
            hero_hand: List of 2 Card objects (hero's hole cards)
            game_state: GameState object with current game information
            opponent_range: Optional Range object (if None, will be inferred)
            opponent_name: Optional opponent name for dynamic modeling
            
        Returns:
            dict: Comprehensive evaluation results
        """
        # Step 1: Establish opponent's current range
        if opponent_range is None:
            opponent_range = self._establish_opponent_range(game_state, opponent_name)
        
        # Step 2: Calculate core metrics using Monte Carlo for post-flop
        if game_state.board:
            # Use Monte Carlo for post-flop analysis
            opponent_range_str = self._range_to_string(opponent_range)
            equity = self.equity_calculator.monte_carlo_equity(
                hero_hand, opponent_range_str, game_state.board
            )
        else:
            # Use standard equity calculation for pre-flop
            equity = self.equity_calculator.calculate_equity(
                hero_hand, opponent_range, game_state.board
            )
        
        equity_realization = self.equity_calculator.calculate_equity_realization(
            hero_hand, opponent_range, game_state.board,
            position='in_position' if game_state.hero_position == Position.BUTTON else 'out_of_position'
        )
        
        # Step 3: Partition opponent's range
        range_analysis = self._partition_opponent_range(
            hero_hand, opponent_range, game_state
        )
        
        # Step 4: Calculate strategic metrics
        strategic_metrics = self._calculate_strategic_metrics(
            hero_hand, opponent_range, game_state, equity, equity_realization
        )
        
        # Step 5: Get GTO-based recommendations
        gto_recommendations = self._get_gto_recommendations(game_state, hero_hand)
        
        # Step 6: Get opponent-specific insights
        opponent_insights = self._get_opponent_insights(opponent_name, opponent_range)
        
        return {
            'hero_hand': [str(card) for card in hero_hand],
            'board': [str(card) for card in game_state.board],
            'street': game_state.street.value,
            'pot_size': game_state.pot_size,
            'equity': equity,
            'equity_realization': equity_realization,
            'realized_equity': equity * equity_realization,
            'range_analysis': range_analysis,
            'strategic_metrics': strategic_metrics,
            'opponent_range_size': len(opponent_range),
            'gto_recommendations': gto_recommendations,
            'opponent_insights': opponent_insights,
            'recommendations': self._generate_recommendations(
                equity, equity_realization, range_analysis, strategic_metrics, 
                game_state, gto_recommendations, opponent_insights
            )
        }
    
    def _establish_opponent_range(self, game_state, opponent_name=None):
        """
        Establish the opponent's current range based on GTO charts, action history, and opponent modeling.
        
        Args:
            game_state: GameState object
            opponent_name: Optional opponent name for dynamic modeling
            
        Returns:
            Range object representing opponent's likely holdings
        """
        # Start with a baseline GTO range based on position
        if game_state.hero_position == Position.BUTTON:
            # Hero is button, villain is big blind
            baseline_range = Range.from_gto_chart('big_blind', 'defend')
        else:
            # Hero is big blind, villain is button
            baseline_range = Range.from_gto_chart('button', 'raise')
        
        # Apply opponent-specific adjustments if available
        if opponent_name:
            baseline_range = self.opponent_modeler.get_adjusted_range_for_player(
                opponent_name, baseline_range
            )
        
        # Apply range filtering based on action history
        current_range = baseline_range
        
        for action_record in game_state.action_history:
            if action_record['player'] == 'villain':
                action = action_record['action'].value
                amount = action_record['amount']
                street = action_record['street']
                
                # Update range based on this action
                current_range = current_range.update_from_betting_action(
                    action, amount, 'villain', street
                )
        
        return current_range
    
    def _partition_opponent_range(self, hero_hand, opponent_range, game_state):
        """
        Partition the opponent's range into strategic categories using the new partitioning method.
        
        Args:
            hero_hand: Hero's hole cards
            opponent_range: Opponent's current range
            game_state: Current game state
            
        Returns:
            dict: Range partitioning analysis
        """
        if not game_state.board:
            # Pre-flop partitioning is simpler
            return self._partition_preflop_range(opponent_range)
        
        # Use the new range partitioning method for post-flop
        opponent_range_str = self._range_to_string(opponent_range)
        partitions = opponent_range.partition_range(opponent_range_str, game_state.board)
        
        # Calculate percentages
        total_hands = len(partitions['value']) + len(partitions['semi_bluff']) + len(partitions['bluff'])
        
        if total_hands == 0:
            return {
                'value_targets': 0.0,
                'fold_equity': 0.0,
                'threats': 0.0,
                'dominated_draws': 0.0,
                'total_hands': 0
            }
        
        return {
            'value_targets': len(partitions['value']) / total_hands,
            'fold_equity': len(partitions['bluff']) / total_hands,
            'threats': len(partitions['value']) / total_hands,  # Simplified
            'dominated_draws': len(partitions['semi_bluff']) / total_hands,
            'total_hands': total_hands,
            'partitions': partitions
        }
    
    def _partition_preflop_range(self, opponent_range):
        """Partition range for pre-flop situations."""
        weighted_hands = opponent_range.get_weighted_hands()
        
        value_targets = 0.0
        fold_equity = 0.0
        threats = 0.0
        dominated_draws = 0.0
        
        for hand_str, weight in weighted_hands.items():
            hand_strength = opponent_range._get_hand_strength(hand_str)
            
            if hand_strength > 0.7:
                value_targets += weight
            elif hand_strength < 0.3:
                fold_equity += weight
            else:
                dominated_draws += weight
        
        return {
            'value_targets': value_targets,
            'fold_equity': fold_equity,
            'threats': threats,
            'dominated_draws': dominated_draws,
            'total_hands': sum(weighted_hands.values())
        }
    
    def _get_gto_recommendations(self, game_state, hero_hand):
        """
        Get GTO-based recommendations for the current situation.
        
        Args:
            game_state: Current game state
            hero_hand: Hero's hole cards
            
        Returns:
            dict: GTO recommendations
        """
        if not game_state.board:  # Pre-flop
            position = self._game_position_to_gto_position(game_state.hero_position)
            action = self.gto_strategy.get_preflop_action(position, hero_hand)
            
            return {
                'action': action,
                'position': position,
                'confidence': 0.8,  # High confidence for pre-flop charts
                'reasoning': f"GTO chart recommendation for {position} position"
            }
        else:
            # Post-flop GTO recommendations would be more complex
            return {
                'action': 'ANALYZE',
                'confidence': 0.6,
                'reasoning': "Post-flop GTO analysis requires solver data"
            }
    
    def _get_opponent_insights(self, opponent_name, opponent_range):
        """
        Get insights about the opponent based on their profile.
        
        Args:
            opponent_name: Opponent name
            opponent_range: Opponent's current range
            
        Returns:
            dict: Opponent insights
        """
        if not opponent_name:
            return {
                'confidence': 0.0,
                'tendencies': 'Unknown opponent',
                'range_adjustment': 'None'
            }
        
        profile = self.opponent_modeler.get_profile(opponent_name)
        tendencies = self.opponent_modeler.get_player_tendencies(opponent_name)
        
        return {
            'confidence': profile.get_confidence_level(),
            'tendencies': tendencies,
            'range_adjustment': f"Tightness: {profile.tightness_factor:.2f}, Aggression: {profile.aggression_factor:.2f}",
            'vpip': profile.vpip,
            'pfr': profile.pfr,
            'aggression_factor': profile.aggression_factor
        }
    
    def _game_position_to_gto_position(self, game_position):
        """Convert game position to GTO position format."""
        if game_position == Position.BUTTON:
            return 'BTN'
        elif game_position == Position.BIG_BLIND:
            return 'BB'
        else:
            return 'BB'  # Default
    
    def _range_to_string(self, opponent_range):
        """Convert Range object to string format for Monte Carlo."""
        weighted_hands = opponent_range.get_weighted_hands()
        return ','.join(weighted_hands.keys())
    
    def _calculate_strategic_metrics(self, hero_hand, opponent_range, game_state, equity, equity_realization):
        """
        Calculate strategic metrics for decision making.
        
        Args:
            hero_hand: Hero's hole cards
            opponent_range: Opponent's range
            game_state: Game state
            equity: Raw equity
            equity_realization: Equity realization factor
            
        Returns:
            dict: Strategic metrics
        """
        # Calculate pot odds
        if game_state.current_bet > 0:
            pot_odds = game_state.get_pot_odds(game_state.current_bet)
        else:
            pot_odds = float('inf')
        
        # Calculate minimum defense frequency
        if game_state.current_bet > 0:
            mdf = self.gto_charts.get_minimum_defense_frequency(
                game_state.current_bet, game_state.pot_size
            )
        else:
            mdf = 1.0
        
        # Calculate expected value of calling
        call_ev = self._calculate_call_ev(equity, game_state)
        
        # Calculate expected value of betting
        bet_ev = self._calculate_bet_ev(equity, equity_realization, game_state)
        
        return {
            'pot_odds': pot_odds,
            'minimum_defense_frequency': mdf,
            'call_ev': call_ev,
            'bet_ev': bet_ev,
            'effective_stack': game_state.get_effective_stack(),
            'position_advantage': game_state.hero_position == Position.BUTTON
        }
    
    def _estimate_hero_strength(self, hero_hand, board):
        """
        Estimate hero's hand strength (0.0 to 1.0).
        
        Args:
            hero_hand: Hero's hole cards
            board: Community cards
            
        Returns:
            float: Hand strength estimate
        """
        if not board:
            # Pre-flop: estimate based on hole cards
            return self._estimate_preflop_strength(hero_hand)
        else:
            # Post-flop: use actual hand evaluation
            hand_strength = self.hand_evaluator.evaluate_hand(hero_hand + board)
            # Convert to 0-1 scale (this is approximate)
            return max(0.0, min(1.0, 1.0 - (hand_strength / 9000.0)))
    
    def _estimate_preflop_strength(self, hero_hand):
        """Estimate pre-flop hand strength."""
        if len(hero_hand) != 2:
            return 0.5
        
        card1, card2 = hero_hand
        
        # Pocket pair
        if card1.rank == card2.rank:
            rank_val = card1.val
            return (rank_val + 1) / 13.0
        
        # Suited or offsuit
        rank1_val = card1.val
        rank2_val = card2.val
        suited = card1.suit == card2.suit
        
        # Base strength on higher rank
        base_strength = max(rank1_val, rank2_val) / 13.0
        
        # Adjust for suitedness
        if suited:
            base_strength *= 1.1
        
        return min(base_strength, 1.0)
    
    def _calculate_call_ev(self, equity, game_state):
        """Calculate expected value of calling."""
        if game_state.current_bet <= 0:
            return 0.0
        
        call_amount = game_state.current_bet
        pot_size = game_state.pot_size
        
        # EV = (equity * pot_size) - call_amount
        return (equity * pot_size) - call_amount
    
    def _calculate_bet_ev(self, equity, equity_realization, game_state):
        """Calculate expected value of betting."""
        # Simplified calculation
        # In practice, this would consider fold equity and opponent's calling range
        
        pot_size = game_state.pot_size
        bet_size = pot_size * 0.75  # Assume 3/4 pot bet
        
        # Assume 50% fold equity for simplicity
        fold_equity = 0.5
        
        # EV = fold_equity * pot_size + (1 - fold_equity) * (equity_realization * (pot_size + bet_size) - bet_size)
        ev = (fold_equity * pot_size) + \
             ((1 - fold_equity) * (equity_realization * (pot_size + bet_size) - bet_size))
        
        return ev
    
    def _generate_recommendations(self, equity, equity_realization, range_analysis, strategic_metrics, game_state, gto_recommendations, opponent_insights):
        """
        Generate strategic recommendations based on the analysis.
        
        Args:
            equity: Raw equity
            equity_realization: Equity realization factor
            range_analysis: Range partitioning results
            strategic_metrics: Strategic metrics
            game_state: Game state
            gto_recommendations: GTO-based recommendations
            opponent_insights: Opponent-specific insights
            
        Returns:
            dict: Strategic recommendations
        """
        recommendations = {
            'primary_action': None,
            'bet_sizing': None,
            'confidence': 0.0,
            'reasoning': []
        }
        
        realized_equity = equity * equity_realization
        pot_odds = strategic_metrics['pot_odds']
        
        # Determine primary action
        if game_state.current_bet > 0:
            # Facing a bet
            if realized_equity > 0.5:
                recommendations['primary_action'] = 'call'
                recommendations['reasoning'].append(f"Strong realized equity: {realized_equity:.1%}")
            elif pot_odds > 3.0 and equity > 0.25:
                recommendations['primary_action'] = 'call'
                recommendations['reasoning'].append(f"Good pot odds: {pot_odds:.1f}:1")
            else:
                recommendations['primary_action'] = 'fold'
                recommendations['reasoning'].append("Insufficient equity or pot odds")
        else:
            # No bet to call
            if realized_equity > 0.6:
                recommendations['primary_action'] = 'bet'
                recommendations['bet_sizing'] = 'pot'
                recommendations['reasoning'].append(f"Strong value betting opportunity: {realized_equity:.1%}")
            elif realized_equity > 0.4 and range_analysis['fold_equity'] > 0.3:
                recommendations['primary_action'] = 'bet'
                recommendations['bet_sizing'] = '2/3_pot'
                recommendations['reasoning'].append("Good bluffing opportunity")
            else:
                recommendations['primary_action'] = 'check'
                recommendations['reasoning'].append("Weak hand, check to control pot")
        
        # Set confidence based on equity and range analysis
        if realized_equity > 0.7 or realized_equity < 0.3:
            recommendations['confidence'] = 0.9
        elif realized_equity > 0.6 or realized_equity < 0.4:
            recommendations['confidence'] = 0.7
        else:
            recommendations['confidence'] = 0.5
        
        return recommendations
    
    def analyze_what_if(self, hero_hand, game_state, proposed_action, bet_size=None):
        """
        Analyze the consequences of a proposed action.
        
        Args:
            hero_hand: Hero's hole cards
            game_state: Current game state
            proposed_action: Proposed action ('fold', 'call', 'bet', 'raise')
            bet_size: Bet size if applicable
            
        Returns:
            dict: Analysis of the proposed action
        """
        # Create a copy of the game state to simulate the action
        simulated_state = self._simulate_action(game_state, 'hero', proposed_action, bet_size)
        
        # Re-evaluate with the new game state
        evaluation = self.evaluate_hand(hero_hand, simulated_state)
        
        return {
            'proposed_action': proposed_action,
            'bet_size': bet_size,
            'projected_equity': evaluation['equity'],
            'projected_realized_equity': evaluation['realized_equity'],
            'projected_ev': evaluation['strategic_metrics']['call_ev'],
            'recommendations': evaluation['recommendations']
        }
    
    def _simulate_action(self, game_state, player, action, bet_size=None):
        """Simulate an action on a game state."""
        # Create a copy of the game state
        simulated_state = GameState(
            hero_stack=game_state.hero_stack,
            villain_stack=game_state.villain_stack,
            bb_size=game_state.bb_size
        )
        
        # Copy the current state
        simulated_state.pot_size = game_state.pot_size
        simulated_state.board = game_state.board.copy()
        simulated_state.street = game_state.street
        simulated_state.action_history = game_state.action_history.copy()
        simulated_state.street_actions = game_state.street_actions.copy()
        
        # Add the simulated action
        simulated_state.add_action(player, Action(action), bet_size or 0)
        
        return simulated_state 