"""
weather.py — Stochastic weather generator and DLS resource model.

Plan 05-03: Advanced Cricket Rules — Phase 5
"""
from __future__ import annotations

import bisect
import math
import random
from typing import Optional

# ─────────────────────────────────────────────────────────────
# DLS Resource Percentage Table
# Source: Simplified ICC D/L resource table (10-over buckets)
# Keys: (overs_remaining_bucket, wickets_lost) → resource_percentage
# ─────────────────────────────────────────────────────────────

_OVER_BUCKETS = [1, 3, 5, 10, 15, 20, 25, 30, 40, 50]

# Raw table rows: [w0, w1, w2, w3, w4, w5, w6, w7, w8, w9]
_RAW: dict[int, list[float]] = {
    50: [100.0, 93.4, 85.1, 74.9, 62.7, 49.0, 34.9, 22.0, 11.9,  4.7],
    40: [ 89.3, 83.8, 76.7, 67.3, 56.0, 43.3, 30.5, 19.0, 10.2,  4.0],
    30: [ 75.1, 70.8, 65.1, 57.2, 47.6, 36.8, 26.1, 16.4,  8.8,  3.5],
    25: [ 66.5, 62.8, 57.9, 51.0, 42.6, 33.1, 23.7, 14.9,  8.0,  3.2],
    20: [ 56.6, 53.6, 49.6, 43.9, 37.0, 29.1, 21.1, 13.4,  7.3,  2.9],
    15: [ 45.2, 43.0, 39.9, 35.6, 30.2, 23.9, 17.5, 11.2,  6.1,  2.5],
    10: [ 32.1, 30.7, 28.6, 25.7, 21.9, 17.5, 13.0,  8.4,  4.7,  1.9],
     5: [ 17.2, 16.5, 15.5, 14.0, 12.1,  9.8,  7.4,  4.9,  2.8,  1.1],
     3: [ 10.9, 10.5,  9.9,  9.0,  7.8,  6.4,  4.9,  3.3,  1.9,  0.8],
     1: [  3.6,  3.5,  3.3,  3.0,  2.7,  2.2,  1.7,  1.2,  0.7,  0.3],
}

# Flatten into a (bucket, wickets) → pct lookup
DLS_RESOURCES: dict[tuple[int, int], float] = {
    (bucket, wickets): pct
    for bucket, row in _RAW.items()
    for wickets, pct in enumerate(row)
}


def _snap_to_bucket(overs_remaining: float) -> int:
    """Snap an arbitrary overs value to the nearest DLS bucket."""
    overs_int = int(math.floor(overs_remaining))
    # bisect finds insertion point; we want the closest bucket
    idx = bisect.bisect_left(_OVER_BUCKETS, overs_int)
    if idx == 0:
        return _OVER_BUCKETS[0]
    if idx >= len(_OVER_BUCKETS):
        return _OVER_BUCKETS[-1]
    # Pick the closer of the two neighbours
    lo = _OVER_BUCKETS[idx - 1]
    hi = _OVER_BUCKETS[idx]
    return hi if (overs_int - lo) >= (hi - overs_int) else lo


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def generate_weather_event(
    seed: Optional[int] = None,
    interruption_prob: float = 0.15,
    total_overs: int = 20,
    overs_bowled: int = 0,
) -> Optional[int]:
    """
    Simulate a weather interruption before/during innings 2.

    Returns the number of overs LOST due to rain, or None if no interruption.
    - Overs lost: uniform random 1–5.
    - Ensures at least 5 overs remain playable for a valid match result.

    Args:
        seed: RNG seed for reproducibility.
        interruption_prob: Probability that a weather event occurs (default 15%).
        total_overs: Total overs in the match format (default 20 for T20).
        overs_bowled: Overs already bowled at interruption (default 0 = before innings).

    Returns:
        Number of overs lost, or None.
    """
    rng = random.Random(seed)

    if rng.random() >= interruption_prob:
        return None

    overs_remaining = total_overs - overs_bowled
    min_playable = 5
    max_loss = overs_remaining - min_playable

    if max_loss <= 0:
        # Not enough overs left to have a valid reduction
        return None

    overs_lost = rng.randint(1, min(5, max_loss))
    return overs_lost


def get_resource_percentage(overs_remaining: float, wickets_lost: int) -> float:
    """
    Return the DLS resource percentage for a given match state.

    Args:
        overs_remaining: Overs still available to the batting team.
        wickets_lost: Wickets lost by the batting team so far.

    Returns:
        Resource percentage (0.0–100.0).
    """
    # Clamp wickets to 0–9 range
    w = max(0, min(9, wickets_lost))
    bucket = _snap_to_bucket(overs_remaining)
    return DLS_RESOURCES[(bucket, w)]


def calculate_par_score(
    team1_score: int,
    team1_total_overs: int,
    revised_overs: int,
    wickets_at_interruption: int,
) -> int:
    """
    Calculate the DLS par score for team 2 after a weather interruption
    reduces their available overs.

    Formula:
        R1 = resources for team 1 (full innings, 0 wickets lost)
        R2 = resources remaining for team 2 after interruption
        par = ceil(team1_score × R2 / R1)

    Args:
        team1_score: Runs scored by team 1 in their innings.
        team1_total_overs: Overs team 1 had available (usually 20).
        revised_overs: Reduced overs available to team 2.
        wickets_at_interruption: Wickets already lost by team 2 when rain stops play.

    Returns:
        Par score team 2 must surpass to win.
    """
    r1 = get_resource_percentage(team1_total_overs, 0)
    r2 = get_resource_percentage(revised_overs, wickets_at_interruption)

    if r1 == 0:
        return team1_score  # Fallback: no reduction possible

    par = team1_score * (r2 / r1)
    return math.ceil(par)
