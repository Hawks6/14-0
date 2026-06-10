import numpy as np
import pytest
from app.simulation.models import MatchState, MatchOutcome
from app.simulation.modifiers import (
    PowerplayModifier,
    RequiredRunRateModifier,
    MomentumModifier,
    BowlingPressureModifier
)
from app.simulation.simulator import InningsSimulator
from tests.test_simulation.test_simulator import create_mock_team

def test_powerplay_modifier():
    modifier = PowerplayModifier()
    base_probs = np.array([0.35, 0.38, 0.06, 0.005, 0.11, 0.0, 0.04, 0.045, 0.008, 0.002])
    
    # Within Powerplay (balls < 36)
    state_in = MatchState(overs_completed=5, balls_completed=5)  # 35 balls completed
    assert state_in.total_balls < 36
    probs_in = modifier.apply(state_in, base_probs)
    assert probs_in[MatchOutcome.FOUR] == pytest.approx(base_probs[MatchOutcome.FOUR] * 1.25)
    assert probs_in[MatchOutcome.SIX] == pytest.approx(base_probs[MatchOutcome.SIX] * 1.15)
    assert probs_in[MatchOutcome.DOT] == pytest.approx(base_probs[MatchOutcome.DOT] * 0.90)
    
    # Outside Powerplay (balls >= 36)
    state_out = MatchState(overs_completed=6, balls_completed=0)  # 36 balls completed
    assert state_out.total_balls == 36
    probs_out = modifier.apply(state_out, base_probs)
    assert np.array_equal(probs_out, base_probs)

def test_required_run_rate_modifier():
    modifier = RequiredRunRateModifier()
    base_probs = np.array([0.35, 0.38, 0.06, 0.005, 0.11, 0.0, 0.04, 0.045, 0.008, 0.002])
    
    # 1. No target set
    state_no_target = MatchState(target=None, overs_completed=10, balls_completed=0)
    assert np.array_equal(modifier.apply(state_no_target, base_probs), base_probs)
    
    # 2. Target set, but low RRR (<= 8.0)
    state_low_rrr = MatchState(target=100, runs=60, overs_completed=10, balls_completed=0)
    assert np.array_equal(modifier.apply(state_low_rrr, base_probs), base_probs)
    
    # 3. High RRR (> 8.0)
    state_high_rrr = MatchState(target=100, runs=40, overs_completed=15, balls_completed=0)
    probs_high = modifier.apply(state_high_rrr, base_probs)
    rrr = 12.0
    aggression = min((rrr - 8.0) * 0.08, 0.5)
    assert probs_high[MatchOutcome.SIX] == pytest.approx(base_probs[MatchOutcome.SIX] * (1.0 + aggression))
    assert probs_high[MatchOutcome.FOUR] == pytest.approx(base_probs[MatchOutcome.FOUR] * (1.0 + aggression * 0.5))
    assert probs_high[MatchOutcome.WICKET] == pytest.approx(base_probs[MatchOutcome.WICKET] * (1.0 + aggression * 0.8))
    assert probs_high[MatchOutcome.DOT] == pytest.approx(base_probs[MatchOutcome.DOT] * (1.0 - aggression * 0.6))
    
    # 4. Capped aggression (aggression = 0.5)
    state_capped_rrr = MatchState(target=100, runs=0, overs_completed=15, balls_completed=0)
    probs_capped = modifier.apply(state_capped_rrr, base_probs)
    assert probs_capped[MatchOutcome.SIX] == pytest.approx(base_probs[MatchOutcome.SIX] * 1.5)
    assert probs_capped[MatchOutcome.FOUR] == pytest.approx(base_probs[MatchOutcome.FOUR] * 1.25)
    assert probs_capped[MatchOutcome.WICKET] == pytest.approx(base_probs[MatchOutcome.WICKET] * 1.4)
    assert probs_capped[MatchOutcome.DOT] == pytest.approx(base_probs[MatchOutcome.DOT] * 0.7)

def test_momentum_modifier():
    modifier = MomentumModifier()
    base_probs = np.array([0.35, 0.38, 0.06, 0.005, 0.11, 0.0, 0.04, 0.045, 0.008, 0.002])
    
    # 1. balls_since_boundary = 0
    state_0 = MatchState(balls_since_boundary=0)
    probs_0 = modifier.apply(state_0, base_probs)
    assert probs_0[MatchOutcome.FOUR] == pytest.approx(base_probs[MatchOutcome.FOUR] * 1.4)
    assert probs_0[MatchOutcome.SIX] == pytest.approx(base_probs[MatchOutcome.SIX] * 1.4)
    assert probs_0[MatchOutcome.WICKET] == pytest.approx(base_probs[MatchOutcome.WICKET] * 0.7)
    
    # 2. balls_since_boundary = 2
    state_2 = MatchState(balls_since_boundary=2)
    probs_2 = modifier.apply(state_2, base_probs)
    decay = 0.65 ** 2
    assert probs_2[MatchOutcome.FOUR] == pytest.approx(base_probs[MatchOutcome.FOUR] * (1.0 + 0.40 * decay))
    assert probs_2[MatchOutcome.WICKET] == pytest.approx(base_probs[MatchOutcome.WICKET] * (1.0 - 0.30 * decay))
    
    # 3. balls_since_boundary = 4 (inactive)
    state_4 = MatchState(balls_since_boundary=4)
    probs_4 = modifier.apply(state_4, base_probs)
    assert np.array_equal(probs_4, base_probs)

def test_bowling_pressure_modifier():
    modifier = BowlingPressureModifier()
    base_probs = np.array([0.35, 0.38, 0.06, 0.005, 0.11, 0.0, 0.04, 0.045, 0.008, 0.002])
    
    # 1. consecutive_dots = 0
    state_0 = MatchState(consecutive_dots=0)
    assert np.array_equal(modifier.apply(state_0, base_probs), base_probs)
    
    # 2. consecutive_dots = 3
    state_3 = MatchState(consecutive_dots=3)
    probs_3 = modifier.apply(state_3, base_probs)
    pressure = 3 * 0.05
    assert probs_3[MatchOutcome.WICKET] == pytest.approx(base_probs[MatchOutcome.WICKET] * (1.0 + pressure))
    assert probs_3[MatchOutcome.FOUR] == pytest.approx(base_probs[MatchOutcome.FOUR] * (1.0 - pressure * 0.5))
    
    # 3. consecutive_dots = 10 (capped at 0.25)
    state_10 = MatchState(consecutive_dots=10)
    probs_10 = modifier.apply(state_10, base_probs)
    assert probs_10[MatchOutcome.WICKET] == pytest.approx(base_probs[MatchOutcome.WICKET] * 1.25)
    assert probs_10[MatchOutcome.FOUR] == pytest.approx(base_probs[MatchOutcome.FOUR] * 0.875)

def test_simulator_state_updates_and_modifiers():
    # Setup simulator with modifiers
    modifiers = [
        PowerplayModifier(),
        RequiredRunRateModifier(),
        MomentumModifier(),
        BowlingPressureModifier()
    ]
    sim = InningsSimulator(seed=42, modifiers=modifiers)
    
    batting_team = create_mock_team("Bat")
    bowling_team = create_mock_team("Bowl")
    
    # Run simulation
    res = sim.simulate_innings(batting_team, bowling_team)
    
    # Verify innings completed successfully
    assert res.total_runs > 0
    assert len(res.delivery_log) > 0
