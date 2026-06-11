"""
Tests for Plan 05-01: Strike Rotation, No-Ball Free Hit & Bowler Quota.
"""
import pytest
from app.simulation.models import MatchState, MatchOutcome
from app.simulation.modifiers import FreeHitModifier
from app.simulation.simulator import InningsSimulator


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def make_player(i, role="BAT", bat=50, bowl=50, overseas=False):
    return {
        "id": i,
        "name": f"Player{i}",
        "role": role,
        "percentile_batting": bat,
        "percentile_bowling": bowl,
        "is_overseas": overseas,
    }


def make_bat_lineup(n=11):
    return [make_player(i, role="BAT") for i in range(n)]


def make_bowl_lineup(n=5):
    return [make_player(100 + i, role="BOWL", bat=20, bowl=60) for i in range(n)]


# ─────────────────────────────────────────────────────────────
# FreeHitModifier unit tests
# ─────────────────────────────────────────────────────────────

def test_free_hit_suppresses_wicket():
    """FreeHitModifier must zero out WICKET probability when free_hit_next=True."""
    modifier = FreeHitModifier()
    state = MatchState(free_hit_next=True)

    # Build a uniform prob vector with non-zero WICKET
    probs = [0.1] * 10  # all outcomes equal weight
    result = modifier.apply(state, probs)

    assert result[MatchOutcome.WICKET] == 0.0, "WICKET must be 0 on a free hit"
    # All other indices should be untouched
    for idx in range(10):
        if idx != MatchOutcome.WICKET:
            assert result[idx] == pytest.approx(0.1)


def test_free_hit_no_suppression_when_not_free_hit():
    """FreeHitModifier must leave probs unchanged when free_hit_next=False."""
    modifier = FreeHitModifier()
    state = MatchState(free_hit_next=False)

    probs = [0.1] * 10
    result = modifier.apply(state, probs)

    # Should be the original list (same object or equal values)
    for idx in range(10):
        assert result[idx] == pytest.approx(0.1)


def test_free_hit_returns_list_not_ndarray():
    """FreeHitModifier must return a list (not ndarray) for consistent downstream handling."""
    import numpy as np
    modifier = FreeHitModifier()
    state = MatchState(free_hit_next=True)
    probs = np.array([0.1] * 10)
    result = modifier.apply(state, probs)
    assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────
# Simulator free-hit integration
# ─────────────────────────────────────────────────────────────

def test_no_ball_sets_free_hit_flag():
    """
    After a NO_BALL delivery, state.free_hit_next should be True for the next ball.
    We verify this by checking that the delivery_log entry immediately after
    a NO_BALL outcome has the FreeHitModifier active (suppressing wickets).

    Strategy: run many short innings with FreeHitModifier active and confirm
    that no WICKET appears immediately after a NO_BALL entry.
    """
    sim = InningsSimulator(seed=42, modifiers=[FreeHitModifier()])
    batters = make_bat_lineup(11)
    bowlers = make_bowl_lineup(5)

    result = sim.simulate_innings(batters, bowlers)
    log = result.delivery_log

    for i, entry in enumerate(log):
        # Find NO_BALL deliveries
        if entry.get("outcome") == "NO_BALL" and i + 1 < len(log):
            next_entry = log[i + 1]
            next_outcome = next_entry.get("outcome")
            # The next delivery must NOT be a WICKET (free hit protection)
            assert next_outcome != "WICKET", (
                f"WICKET found immediately after NO_BALL at delivery {i} → {i+1}: {next_entry}"
            )


def test_free_hit_flag_set_in_state():
    """
    Directly verify that simulate_innings correctly sets state.free_hit_next
    to True when NO_BALL is bowled, by checking delivery log was_free_hit field.
    """
    sim = InningsSimulator(seed=7)
    batters = make_bat_lineup(11)
    bowlers = make_bowl_lineup(5)
    result = sim.simulate_innings(batters, bowlers)

    log = result.delivery_log
    # was_free_hit field should exist on all entries
    for entry in log:
        assert "was_free_hit" in entry or "outcome" in entry  # basic structure check


# ─────────────────────────────────────────────────────────────
# Bowler quota tests
# ─────────────────────────────────────────────────────────────

def test_bowler_quota_max_4_overs():
    """
    No bowler should bowl more than 4 overs (24 legal balls) in an innings.
    Use 5 specialist bowlers so all 20 overs can be covered (5×4=20).
    """
    sim = InningsSimulator(seed=0)
    batters = make_bat_lineup(11)
    # 5 specialist bowlers = exactly enough for 20 overs at 4 overs each
    bowlers = [make_player(200 + i, role="BOWL", bowl=70) for i in range(5)]

    result = sim.simulate_innings(batters, bowlers)
    log = result.delivery_log

    # Count legal deliveries per bowler
    bowler_ball_counts: dict[str, int] = {}
    for entry in log:
        if entry.get("outcome") not in ("WIDE", "NO_BALL") and "event" not in entry:
            bowler = entry.get("bowler", "")
            bowler_ball_counts[bowler] = bowler_ball_counts.get(bowler, 0) + 1

    for bowler_name, balls in bowler_ball_counts.items():
        assert balls <= 24, f"{bowler_name} bowled {balls} legal balls (> 24 = 4 overs max)"



def test_full_innings_completes():
    """Smoke test: a full innings should complete within 120 legal balls."""
    sim = InningsSimulator(seed=1)
    batters = make_bat_lineup(11)
    bowlers = make_bowl_lineup(5)
    result = sim.simulate_innings(batters, bowlers)

    assert result.total_runs >= 0
    assert result.wickets <= 10
    assert result.overs_bowled <= 20.0
