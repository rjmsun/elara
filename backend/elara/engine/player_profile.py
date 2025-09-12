"""
Player profiling and opponent modeling for Elara poker engine.

Implements dynamic opponent modeling that tracks player statistics
and adjusts strategy based on observed tendencies.
"""

from typing import List, Dict, Optional
from ..giffer.range_handler import Range

class PlayerProfile:
    """
    Tracks statistics and tendencies for a specific opponent.
    
    This class maintains a comprehensive profile of an opponent's
    playing style, including VPIP, PFR, aggression factor, and
    other key metrics that influence strategy adjustments.
    """
    
    def __init__(self, player_name: str):
        """
        Initialize a new player profile.
        
        Args:
            player_name: Name/identifier of the player
        """
        self.player_name = player_name
        self.hands_played = 0
        self.vpip_count = 0
        self.pfr_count = 0
        self.aggressive_actions = 0
        self.passive_actions = 0
        
        # Post-flop statistics
        self.flop_actions = 0
        self.turn_actions = 0
        self.river_actions = 0
        
        # Betting patterns
        self.cbet_frequency = 0.0
        self.cbet_count = 0
        self.cbet_opportunities = 0
        
        # Range adjustments
        self.range_adjustment_factor = 1.0
        self.tightness_factor = 1.0
        self._aggression_factor = 1.0
    
    def update_hand_stats(self, did_vpip: bool, did_pfr: bool, postflop_actions: List[str]):
        """
        Update statistics after a hand is completed.
        
        Args:
            did_vpip: Whether the player voluntarily put money in pot
            did_pfr: Whether the player raised pre-flop
            postflop_actions: List of post-flop actions (e.g., ['BET', 'CALL', 'RAISE'])
        """
        self.hands_played += 1
        
        if did_vpip:
            self.vpip_count += 1
        
        if did_pfr:
            self.pfr_count += 1
        
        # Count post-flop actions
        for action in postflop_actions:
            if action in ['BET', 'RAISE']:
                self.aggressive_actions += 1
            elif action in ['CALL', 'CHECK']:
                self.passive_actions += 1
        
        # Update c-bet statistics
        if 'BET' in postflop_actions and self.pfr_count > 0:
            self.cbet_count += 1
        if self.pfr_count > 0:
            self.cbet_opportunities += 1
        
        # Update c-bet frequency
        if self.cbet_opportunities > 0:
            self.cbet_frequency = self.cbet_count / self.cbet_opportunities
        
        # Update range adjustment factors
        self._update_range_adjustments()
    
    def _update_range_adjustments(self):
        """Update range adjustment factors based on observed tendencies."""
        # Adjust tightness based on VPIP
        if self.hands_played >= 10:  # Need minimum sample size
            if self.vpip < 0.25:
                self.tightness_factor = 0.7  # Very tight
            elif self.vpip < 0.35:
                self.tightness_factor = 0.85  # Tight
            elif self.vpip < 0.45:
                self.tightness_factor = 1.0  # Normal
            elif self.vpip < 0.55:
                self.tightness_factor = 1.2  # Loose
            else:
                self.tightness_factor = 1.5  # Very loose
            
            # Adjust aggression based on aggression factor
            if self.passive_actions > 0:
                af = self._get_aggression_factor_value()
                if af < 0.5:
                    self._aggression_factor = 0.7  # Very passive
                elif af < 1.0:
                    self._aggression_factor = 0.85  # Passive
                elif af < 2.0:
                    self._aggression_factor = 1.0  # Normal
                elif af < 3.0:
                    self._aggression_factor = 1.2  # Aggressive
                else:
                    self._aggression_factor = 1.5  # Very aggressive
    
    @property
    def vpip(self) -> float:
        """Voluntarily Put In Pot percentage."""
        if self.hands_played == 0:
            return 0.0
        return self.vpip_count / self.hands_played
    
    @property
    def pfr(self) -> float:
        """Pre-Flop Raise percentage."""
        if self.hands_played == 0:
            return 0.0
        return self.pfr_count / self.hands_played
    
    @property
    def aggression_factor(self) -> float:
        """Ratio of aggressive actions to passive actions."""
        if self.passive_actions == 0:
            return float('inf') if self.aggressive_actions > 0 else 0.0
        return self.aggressive_actions / self.passive_actions
    
    @property
    def adjusted_aggression_factor(self) -> float:
        """Get the adjusted aggression factor for range modeling."""
        return self._aggression_factor
    
    def _get_aggression_factor_value(self) -> float:
        """Get the calculated aggression factor value."""
        if self.passive_actions == 0:
            return float('inf') if self.aggressive_actions > 0 else 0.0
        return self.aggressive_actions / self.passive_actions
    
    def get_adjusted_range(self, base_range: Range) -> Range:
        """
        Get an adjusted range based on observed player tendencies.
        
        Args:
            base_range: Base GTO range for the situation
            
        Returns:
            Range: Adjusted range reflecting player tendencies
        """
        adjusted_weights = {}
        base_weights = base_range.get_weighted_hands()
        
        for hand, weight in base_weights.items():
            # Apply tightness adjustment
            adjusted_weight = weight * self.tightness_factor
            
            # Apply aggression adjustment for certain hands
            if self.adjusted_aggression_factor > 1.2:  # Aggressive player
                # Increase weight of bluffing hands
                if self._is_bluff_hand(hand):
                    adjusted_weight *= 1.2
            elif self.adjusted_aggression_factor < 0.8:  # Passive player
                # Decrease weight of bluffing hands
                if self._is_bluff_hand(hand):
                    adjusted_weight *= 0.8
            
            adjusted_weights[hand] = min(1.0, adjusted_weight)
        
        return Range(adjusted_weights)
    
    def _is_bluff_hand(self, hand: str) -> bool:
        """
        Determine if a hand is typically used for bluffing.
        
        Args:
            hand: Hand string (e.g., 'AKs', 'QQ')
            
        Returns:
            bool: True if hand is typically used for bluffing
        """
        # Simplified logic - in practice, this would be more sophisticated
        if len(hand) == 2:  # Pocket pair
            rank = hand[0]
            return rank in ['2', '3', '4', '5', '6', '7']  # Small pairs
        elif len(hand) == 3:  # Suited or offsuit
            rank1, rank2 = hand[0], hand[1]
            return rank1 in ['2', '3', '4', '5', '6', '7'] and rank2 in ['2', '3', '4', '5', '6', '7']
        
        return False
    
    def get_confidence_level(self) -> float:
        """
        Get confidence level in the profile (0.0 to 1.0).
        
        Returns:
            float: Confidence level based on sample size
        """
        if self.hands_played < 10:
            return 0.1
        elif self.hands_played < 30:
            return 0.3
        elif self.hands_played < 50:
            return 0.5
        elif self.hands_played < 100:
            return 0.7
        else:
            return 0.9
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary for serialization."""
        return {
            'player_name': self.player_name,
            'hands_played': self.hands_played,
            'vpip': self.vpip,
            'pfr': self.pfr,
            'aggression_factor': self.aggression_factor,
            'adjusted_aggression_factor': self.adjusted_aggression_factor,
            'cbet_frequency': self.cbet_frequency,
            'tightness_factor': self.tightness_factor,
            'confidence_level': self.get_confidence_level()
        }


class OpponentModeler:
    """
    Manages player profiles and provides opponent modeling functionality.
    
    This class maintains a collection of PlayerProfile objects and
    provides methods for retrieving and updating player statistics.
    """
    
    def __init__(self):
        """Initialize the opponent modeler."""
        self.profiles: Dict[str, PlayerProfile] = {}
    
    def get_profile(self, player_name: str) -> PlayerProfile:
        """
        Get or create a player profile.
        
        Args:
            player_name: Name/identifier of the player
            
        Returns:
            PlayerProfile: Player profile object
        """
        if player_name not in self.profiles:
            self.profiles[player_name] = PlayerProfile(player_name)
        
        return self.profiles[player_name]
    
    def update_player_stats(self, player_name: str, did_vpip: bool, did_pfr: bool, 
                          postflop_actions: List[str]):
        """
        Update statistics for a specific player.
        
        Args:
            player_name: Name/identifier of the player
            did_vpip: Whether the player voluntarily put money in pot
            did_pfr: Whether the player raised pre-flop
            postflop_actions: List of post-flop actions
        """
        profile = self.get_profile(player_name)
        profile.update_hand_stats(did_vpip, did_pfr, postflop_actions)
    
    def get_adjusted_range_for_player(self, player_name: str, base_range: Range) -> Range:
        """
        Get an adjusted range for a specific player.
        
        Args:
            player_name: Name/identifier of the player
            base_range: Base GTO range for the situation
            
        Returns:
            Range: Adjusted range reflecting player tendencies
        """
        profile = self.get_profile(player_name)
        return profile.get_adjusted_range(base_range)
    
    def get_player_tendencies(self, player_name: str) -> Dict:
        """
        Get a summary of player tendencies.
        
        Args:
            player_name: Name/identifier of the player
            
        Returns:
            dict: Summary of player tendencies
        """
        profile = self.get_profile(player_name)
        return profile.to_dict()
    
    def get_all_profiles(self) -> Dict[str, Dict]:
        """
        Get all player profiles.
        
        Returns:
            dict: Dictionary of all player profiles
        """
        return {name: profile.to_dict() for name, profile in self.profiles.items()}
    
    def clear_profile(self, player_name: str):
        """
        Clear a player profile.
        
        Args:
            player_name: Name/identifier of the player
        """
        if player_name in self.profiles:
            del self.profiles[player_name]
    
    def clear_all_profiles(self):
        """Clear all player profiles."""
        self.profiles.clear()
    
    def get_most_active_players(self, limit: int = 5) -> List[str]:
        """
        Get the most active players based on hands played.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            list: List of player names sorted by activity
        """
        sorted_players = sorted(
            self.profiles.items(),
            key=lambda x: x[1].hands_played,
            reverse=True
        )
        return [player[0] for player in sorted_players[:limit]]
    
    def get_players_by_tendency(self, tendency: str, threshold: float = 0.5) -> List[str]:
        """
        Get players with specific tendencies.
        
        Args:
            tendency: Tendency to filter by ('tight', 'loose', 'aggressive', 'passive')
            threshold: Threshold for the tendency
            
        Returns:
            list: List of player names matching the tendency
        """
        matching_players = []
        
        for player_name, profile in self.profiles.items():
            if tendency == 'tight' and profile.vpip < threshold:
                matching_players.append(player_name)
            elif tendency == 'loose' and profile.vpip > threshold:
                matching_players.append(player_name)
            elif tendency == 'aggressive' and profile.aggression_factor > threshold:
                matching_players.append(player_name)
            elif tendency == 'passive' and profile.aggression_factor < threshold:
                matching_players.append(player_name)
        
        return matching_players 