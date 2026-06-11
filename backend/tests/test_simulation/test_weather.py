"""
Tests for Plan 05-03: Stochastic weather generator and DLS resource model.
"""
import math
import pytest

from app.simulation.weather import (
    generate_weather_event,
    get_resource_percentage,
    calculate_par_score,
    DLS_RESOURCES,
)


# ─────────────────────────────────────────────────────────────
# generate_weather_event
# ─────────────────────────────────────────────────────────────

def test_no_interruption_at_zero_prob():
    """With interruption_prob=0.0, must always return None."""
    for seed in range(20):
        assert generate_weather_event(seed=seed, interruption_prob=0.0) is None


def test_always_interruption_at_prob_one():
    """With interruption_prob=1.0, must always return a positive integer."""
    for seed in range(20):
        result = generate_weather_event(seed=seed, interruption_prob=1.0)
        assert result is not None, f"Expected interruption with seed={seed}"
        assert isinstance(result, int)
        assert 1 <= result <= 5, f"Overs lost {result} not in [1, 5]"


def test_overs_lost_within_valid_range():
    """Overs lost must never leave fewer than 5 overs remaining."""
    total_overs = 20
    overs_bowled = 0
    for seed in range(50):
        result = generate_weather_event(
            seed=seed,
            interruption_prob=1.0,
            total_overs=total_overs,
            overs_bowled=overs_bowled,
        )
        if result is not None:
            remaining_after = total_overs - overs_bowled - result
            assert remaining_after >= 5, (
                f"Only {remaining_after} overs left after weather with seed={seed}"
            )


def test_no_interruption_when_too_few_overs():
    """If already 15 overs bowled (only 5 left), no reduction is possible → None."""
    result = generate_weather_event(
        seed=0,
        interruption_prob=1.0,
        total_overs=20,
        overs_bowled=15,
    )
    # max_loss = 20-15-5 = 0, so no valid interruption
    assert result is None


def test_weather_deterministic_with_seed():
    """Same seed must always produce same result."""
    r1 = generate_weather_event(seed=42, interruption_prob=0.5)
    r2 = generate_weather_event(seed=42, interruption_prob=0.5)
    assert r1 == r2


# ─────────────────────────────────────────────────────────────
# get_resource_percentage
# ─────────────────────────────────────────────────────────────

def test_resource_percentage_full_overs_no_wickets():
    """Standard lookup: 20 overs remaining, 0 wickets → 56.6."""
    pct = get_resource_percentage(20, 0)
    assert pct == pytest.approx(56.6)


def test_resource_percentage_15_overs_no_wickets():
    """15 overs, 0 wickets → 45.2."""
    pct = get_resource_percentage(15, 0)
    assert pct == pytest.approx(45.2)


def test_resource_percentage_clamped_wickets_above_9():
    """wickets_lost=10 should be clamped to 9 → same as w=9 at 20 overs (2.9)."""
    pct_9 = get_resource_percentage(20, 9)
    pct_10 = get_resource_percentage(20, 10)
    assert pct_9 == pytest.approx(pct_10)
    assert pct_10 == pytest.approx(2.9)


def test_resource_percentage_clamped_wickets_below_0():
    """wickets_lost=-1 should be clamped to 0."""
    pct_0 = get_resource_percentage(20, 0)
    pct_neg = get_resource_percentage(20, -1)
    assert pct_0 == pytest.approx(pct_neg)


def test_resource_percentage_decreases_with_wickets():
    """More wickets lost → fewer resources remaining at same overs."""
    overs = 20
    prev = get_resource_percentage(overs, 0)
    for w in range(1, 10):
        curr = get_resource_percentage(overs, w)
        assert curr < prev, f"Resource % did not decrease at wicket {w}"
        prev = curr


def test_resource_percentage_decreases_with_fewer_overs():
    """Fewer overs → fewer resources remaining at same wickets."""
    w = 0
    prev = get_resource_percentage(20, w)
    for overs in [15, 10, 5, 3, 1]:
        curr = get_resource_percentage(overs, w)
        assert curr < prev, f"Resource % did not decrease at {overs} overs"
        prev = curr


# ─────────────────────────────────────────────────────────────
# calculate_par_score
# ─────────────────────────────────────────────────────────────

def test_par_score_no_reduction():
    """If revised_overs == team1_total_overs and 0 wickets, par ≈ team1_score."""
    par = calculate_par_score(
        team1_score=160,
        team1_total_overs=20,
        revised_overs=20,
        wickets_at_interruption=0,
    )
    # R1 == R2, so par = 160 * (R2/R1) = 160
    assert par == 160


def test_par_score_basic_reduction():
    """15 revised overs at 0 wickets from 160 should give a sensible par score."""
    par = calculate_par_score(
        team1_score=160,
        team1_total_overs=20,
        revised_overs=15,
        wickets_at_interruption=0,
    )
    # R1=56.6, R2=45.2 → par = ceil(160 × 45.2/56.6) ≈ 128
    assert isinstance(par, int)
    assert 100 < par < 160, f"Par score {par} outside expected range"


def test_par_score_is_ceiling():
    """Par score must be the ceiling, not floor."""
    par = calculate_par_score(
        team1_score=100,
        team1_total_overs=20,
        revised_overs=10,
        wickets_at_interruption=0,
    )
    # R1=56.6, R2=32.1 → raw = 100 × 32.1/56.6 ≈ 56.71 → ceil = 57
    expected = math.ceil(100 * (32.1 / 56.6))
    assert par == expected


def test_par_score_higher_wickets_means_lower_par():
    """More wickets at interruption → fewer team2 resources → lower par target."""
    par_0w = calculate_par_score(160, 20, 15, 0)
    par_5w = calculate_par_score(160, 20, 15, 5)
    assert par_5w < par_0w, (
        f"Par with 5 wickets ({par_5w}) should be < par with 0 wickets ({par_0w})"
    )


def test_dls_resource_table_coverage():
    """Spot-check that the full DLS table has correct number of entries."""
    # 10 over buckets × 10 wicket values = 100 entries
    assert len(DLS_RESOURCES) == 100
