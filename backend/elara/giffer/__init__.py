"""
Giffer module: GTO & CFR components for Elara.

Contains Game Theory Optimal strategy components, range modeling,
and Counterfactual Regret Minimization logic.
"""

from .range_handler import Range, GTOCharts
from ..engine.information_set import InformationSet

__all__ = ['Range', 'GTOCharts', 'InformationSet'] 