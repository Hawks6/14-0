"""
Tests for the IPL Impact Player substitution rule.

The Impact Player rule lets one team swap a player mid-match at a fall of
wicket AFTER `impact_trigger_over` overs have been completed.  Depending on
the substitute's role the logic either:
  - Inserts the impact player into the batting order (BAT / WK / ALLROUNDER)
  - Adds the impact player to the bowling pool             (BOWL / ALLROUNDER)
  - Does both for an ALLROUNDER
"""

import pytest
from app.simulation.simulator import InningsSimulator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bat(id_: int, name: str, *, bat_pct: int = 60, bowl_pct: int = 30) -> dict:
    return {
        "id": id_,
        "name": name,
        "role": "BAT",
        "percentile_batting": bat_pct,
        "percentile_bowling": bowl_pct,
    }


def _bowl(id_: int, name: str, *, bat_pct: int = 25, bowl_pct: int = 70) -> dict:
    return {
        "id": id_,
        "name": name,
        "role": "BOWL",
        "percentile_batting": bat_pct,
        "percentile_bowling": bowl_pct,
    }


def _allrounder(id_: int, name: str, *, bat_pct: int = 55, bowl_pct: int = 55) -> dict:
    return {
        "id": id_,
        "name": name,
        "role": "ALLROUNDER",
        "percentile_batting": bat_pct,
        "percentile_bowling": bowl_pct,
    }


def _make_batting_lineup(n: int = 11) -> list:
    """Build a simple batting lineup of n players."""
    return [_bat(i, f"Batter{i}") for i in range(n)]


def _make_bowling_lineup(n: int = 5) -> list:
    """Build a simple bowling lineup (all bowlers, each can bowl up to 24 balls)."""
    return [_bowl(100 + i, f"Bowler{i}", bowl_pct=60) for i in range(n)]


# ---------------------------------------------------------------------------
# Test 1: Batting impact player is inserted into lineup
# ---------------------------------------------------------------------------

def test_impact_player_bat_inserted():
    """
    A BAT impact player must be inserted at next_batsman_idx after the first
    wicket that falls at or after over 6.  result.impact_player_used should be
    True and the delivery_log must contain an IMPACT_PLAYER event.
    """
    sim = InningsSimulator(seed=42)
    batting = _make_batting_lineup(11)
    bowling = _make_bowling_lineup(5)
    impact = _bat(99, "ImpactBatter", bat_pct=90, bowl_pct=10)

    result = sim.simulate_innings(
        batting_lineup=batting,
        bowling_lineup=bowling,
        impact_player=impact,
        impact_trigger_over=6,
    )

    assert result.impact_player_used is True, (
        "impact_player_used should be True when a wicket fell after over 6"
    )

    impact_events = [
        e for e in result.delivery_log if e.get("event") == "IMPACT_PLAYER"
    ]
    assert len(impact_events) == 1, (
        f"Expected exactly 1 IMPACT_PLAYER event, got {len(impact_events)}"
    )
    assert impact_events[0]["player"] == "ImpactBatter"


# ---------------------------------------------------------------------------
# Test 2: Bowling impact player is added to the bowling pool
# ---------------------------------------------------------------------------

def test_impact_player_bowl_added():
    """
    A BOWL impact player must be added to the bowling pool.  After the
    substitution, the impact player's name should appear in at least one
    subsequent delivery logged as bowler (given enough balls remain).
    We run many seeds until we find one where the impact bowler actually
    bowls at least one delivery, confirming pool membership.
    """
    impact_name = "ImpactBowler"
    impact = _bowl(99, impact_name, bowl_pct=90)

    found_bowling = False
    for seed in range(200):
        sim = InningsSimulator(seed=seed)
        batting = _make_batting_lineup(11)
        bowling = _make_bowling_lineup(5)

        result = sim.simulate_innings(
            batting_lineup=batting,
            bowling_lineup=bowling,
            impact_player=impact,
            impact_trigger_over=6,
        )

        if not result.impact_player_used:
            continue  # No wicket after PP — try next seed

        # Check if ImpactBowler delivered at least one ball after the substitution
        impact_event_idx = next(
            (i for i, e in enumerate(result.delivery_log) if e.get("event") == "IMPACT_PLAYER"),
            None,
        )
        if impact_event_idx is None:
            continue

        post_sub_deliveries = result.delivery_log[impact_event_idx + 1 :]
        bowled_by_impact = [d for d in post_sub_deliveries if d.get("bowler") == impact_name]
        if bowled_by_impact:
            found_bowling = True
            break

    assert found_bowling, (
        "ImpactBowler never appeared as bowler after substitution across 200 seeds"
    )


# ---------------------------------------------------------------------------
# Test 3: Impact player NOT used when wicket falls before trigger over
# ---------------------------------------------------------------------------

def test_impact_player_not_used_before_trigger_over():
    """
    With impact_trigger_over=12, if all wickets fall in overs 0-11 the impact
    player must NOT be activated (impact_player_used == False).

    We use a lineup of only 3 batters so all wickets fall quickly (in the first
    few overs), guaranteeing they are exhausted before over 12.
    """
    sim = InningsSimulator(seed=7)
    # Only 3 batters → all wickets fall well before over 12
    batting = _make_batting_lineup(3)
    bowling = _make_bowling_lineup(5)
    impact = _bat(99, "LateImpactBatter", bat_pct=80)

    result = sim.simulate_innings(
        batting_lineup=batting,
        bowling_lineup=bowling,
        impact_player=impact,
        impact_trigger_over=12,
    )

    # All wickets fall early, so impact_player should never trigger
    assert result.impact_player_used is False, (
        "impact_player_used must be False when all wickets fall before impact_trigger_over"
    )

    impact_events = [e for e in result.delivery_log if e.get("event") == "IMPACT_PLAYER"]
    assert len(impact_events) == 0, (
        f"No IMPACT_PLAYER events expected, got {len(impact_events)}"
    )


# ---------------------------------------------------------------------------
# Test 4: No impact player — result.impact_player_used stays False
# ---------------------------------------------------------------------------

def test_no_impact_player_unchanged():
    """
    When impact_player=None (the default), the innings should run normally and
    impact_player_used must remain False.
    """
    sim = InningsSimulator(seed=0)
    batting = _make_batting_lineup(11)
    bowling = _make_bowling_lineup(5)

    result = sim.simulate_innings(
        batting_lineup=batting,
        bowling_lineup=bowling,
        # impact_player omitted → defaults to None
    )

    assert result.impact_player_used is False, (
        "impact_player_used must be False when no impact_player was provided"
    )

    impact_events = [e for e in result.delivery_log if e.get("event") == "IMPACT_PLAYER"]
    assert len(impact_events) == 0
