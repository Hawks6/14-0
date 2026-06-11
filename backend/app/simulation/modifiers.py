from typing import Protocol
import numpy as np
from app.simulation.models import MatchState, MatchOutcome

class SimulationModifier(Protocol):
    def apply(self, state: MatchState, probs: np.ndarray) -> np.ndarray:
        """
        Applies context-specific changes to the outcome probability vector.
        """
        ...

class PowerplayModifier:
    def apply(self, state: MatchState, probs: np.ndarray) -> np.ndarray:
        # Check if total legal balls < 36
        if state.total_balls < 36:
            new_probs = probs.copy()
            new_probs[MatchOutcome.FOUR] *= 1.25
            new_probs[MatchOutcome.SIX] *= 1.15
            new_probs[MatchOutcome.DOT] *= 0.90
            return new_probs
        return probs

class RequiredRunRateModifier:
    def apply(self, state: MatchState, probs: np.ndarray) -> np.ndarray:
        if state.target is not None and state.total_balls < 120:
            runs_needed = state.target - state.runs
            balls_remaining = 120 - state.total_balls
            if balls_remaining > 0:
                rrr = (runs_needed / balls_remaining) * 6
                if rrr > 8.0:
                    aggression_factor = min((rrr - 8.0) * 0.08, 0.5)
                    new_probs = probs.copy()
                    new_probs[MatchOutcome.SIX] *= (1.0 + aggression_factor)
                    new_probs[MatchOutcome.FOUR] *= (1.0 + aggression_factor * 0.5)
                    new_probs[MatchOutcome.WICKET] *= (1.0 + aggression_factor * 0.8)
                    new_probs[MatchOutcome.DOT] *= (1.0 - aggression_factor * 0.6)
                    return new_probs
        return probs

class MomentumModifier:
    def apply(self, state: MatchState, probs: np.ndarray) -> np.ndarray:
        if state.balls_since_boundary <= 3:
            decay_factor = 0.65 ** state.balls_since_boundary
            boost = min(1.0 + 0.40 * decay_factor, 1.4)
            suppress = max(1.0 - 0.30 * decay_factor, 0.7)
            
            new_probs = probs.copy()
            new_probs[MatchOutcome.FOUR] *= boost
            new_probs[MatchOutcome.SIX] *= boost
            new_probs[MatchOutcome.WICKET] *= suppress
            return new_probs
        return probs

class BowlingPressureModifier:
    def apply(self, state: MatchState, probs: np.ndarray) -> np.ndarray:
        if state.consecutive_dots > 0:
            pressure = min(state.consecutive_dots * 0.05, 0.25)
            
            new_probs = probs.copy()
            new_probs[MatchOutcome.WICKET] *= (1.0 + pressure)
            new_probs[MatchOutcome.FOUR] *= (1.0 - pressure * 0.5)
            new_probs[MatchOutcome.SIX] *= (1.0 - pressure * 0.5)
            return new_probs
        return probs

class FreeHitModifier:
    """
    IPL Rule: On a no-ball, the next delivery is a 'free hit'.
    The batter cannot be dismissed off a free hit (except run out).
    Zeroes out the WICKET probability when state.free_hit_next is True.
    """
    def apply(self, state: MatchState, probs: np.ndarray) -> np.ndarray:
        if state.free_hit_next:
            new_probs = list(probs) if not isinstance(probs, list) else list(probs)
            new_probs[MatchOutcome.WICKET] = 0.0
            return new_probs
        return probs

