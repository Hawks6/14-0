import numpy as np
from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

class MatchOutcome(IntEnum):
    DOT = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    SIX = 6
    WICKET = 7
    WIDE = 8
    NO_BALL = 9

# Default T20 league probabilities based on historical IPL averages
LEAGUE_BASE_PROBS = {
    MatchOutcome.DOT: 0.35,
    MatchOutcome.ONE: 0.38,
    MatchOutcome.TWO: 0.06,
    MatchOutcome.THREE: 0.005,
    MatchOutcome.FOUR: 0.11,
    MatchOutcome.SIX: 0.04,
    MatchOutcome.WICKET: 0.045,
    MatchOutcome.WIDE: 0.008,
    MatchOutcome.NO_BALL: 0.002,
}

@dataclass
class MatchState:
    runs: int = 0
    wickets: int = 0
    overs_completed: int = 0
    balls_completed: int = 0
    target: Optional[int] = None
    balls_since_boundary: int = 10
    consecutive_dots: int = 0
    last_event_was_wicket: bool = False

    @property
    def total_balls(self) -> int:
        return self.overs_completed * 6 + self.balls_completed

@dataclass
class InningsResult:
    total_runs: int
    wickets: int
    overs_bowled: float
    extras: int
    delivery_log: List[Dict[str, Any]]

def synthesize_base_matchup(
    batter_percentile: int,
    bowler_percentile: int,
    batter_role: str
) -> np.ndarray:
    """
    Synthesizes the base probability vector for a matchup.
    Blends percentiles using non-linear scaling and applies tailender penalties.
    """
    # 1. Clamp percentiles to valid ranges
    bat_p = max(1, min(100, batter_percentile))
    bowl_p = max(1, min(100, bowler_percentile))
    
    # 2. Transform percentiles to relative skill indices [0.1, 2.0]
    S_bat = 0.1 + 1.9 * (bat_p / 100.0)
    S_bowl = 0.1 + 1.9 * (bowl_p / 100.0)
    
    # 3. Calculate outcome-specific multipliers
    m_runs = (S_bat ** 1.2) * ((2.1 - S_bowl) ** 0.8)
    m_wicket = ((2.1 - S_bat) ** 1.5) * (S_bowl ** 1.2)
    m_dot = ((2.1 - S_bat) ** 0.5) * (S_bowl ** 0.8)
    m_extras = (2.1 - S_bowl) ** 1.0
    
    # 4. Construct vector based on multipliers
    raw_probs = np.zeros(10)
    for outcome in MatchOutcome:
        base_p = LEAGUE_BASE_PROBS[outcome]
        if outcome in {MatchOutcome.ONE, MatchOutcome.TWO, MatchOutcome.THREE, MatchOutcome.FOUR, MatchOutcome.SIX}:
            raw_probs[outcome] = base_p * m_runs
        elif outcome == MatchOutcome.WICKET:
            raw_probs[outcome] = base_p * m_wicket
        elif outcome == MatchOutcome.DOT:
            raw_probs[outcome] = base_p * m_dot
        else: # WIDE, NO_BALL
            raw_probs[outcome] = base_p * m_extras
            
    # 5. Apply tailender boundaries penalty
    if batter_role == "BOWL" and bat_p < 25:
        # Scale down boundaries, scale up wickets/dots
        raw_probs[MatchOutcome.FOUR] *= 0.2
        raw_probs[MatchOutcome.SIX] *= 0.1
        raw_probs[MatchOutcome.WICKET] *= 1.5
        raw_probs[MatchOutcome.DOT] *= 1.3
        
    # 6. Normalize vector safely
    raw_probs = np.clip(raw_probs, a_min=1e-7, a_max=None)
    probs = raw_probs / np.sum(raw_probs)
    
    return probs
