import uuid
import itertools
from unittest.mock import patch
import numpy as np
import pytest

from app.simulation.models import MatchOutcome, synthesize_base_matchup, MatchState
from app.simulation.simulator import InningsSimulator

class MockPlayer:
    def __init__(self, id, name, role, percentile_batting, percentile_bowling):
        self.id = id
        self.name = name
        self.role = role
        self.percentile_batting = percentile_batting
        self.percentile_bowling = percentile_bowling

def create_mock_team(prefix):
    roles = ["BAT"] * 5 + ["WK"] + ["ALLROUNDER"] * 2 + ["BOWL"] * 3
    players = []
    for i, role in enumerate(roles):
        players.append(MockPlayer(
            id=uuid.uuid4(),
            name=f"{prefix}_Player_{i+1}",
            role=role,
            percentile_batting=10 if role == "BOWL" else 80,
            percentile_bowling=80 if role in ("BOWL", "ALLROUNDER") else 10
        ))
    return players

def test_percentile_blending():
    """Verify sum of probabilities is 1.0, and high ratings favor batsman/bowler correctly."""
    # 1. Normalization check
    p1 = synthesize_base_matchup(50, 50, "BAT")
    assert np.isclose(p1.sum(), 1.0)
    
    # 2. Strong batter vs weak bowler
    p_strong_bat = synthesize_base_matchup(90, 10, "BAT")
    # 3. Weak batter vs strong bowler
    p_weak_bat = synthesize_base_matchup(10, 90, "BAT")
    
    # High batting percentile should favor runs and boundaries
    boundaries_strong = p_strong_bat[MatchOutcome.FOUR] + p_strong_bat[MatchOutcome.SIX]
    boundaries_weak = p_weak_bat[MatchOutcome.FOUR] + p_weak_bat[MatchOutcome.SIX]
    assert boundaries_strong > boundaries_weak

    # High bowling percentile should favor dots and wickets
    dots_wickets_strong_bowl = p_weak_bat[MatchOutcome.DOT] + p_weak_bat[MatchOutcome.WICKET]
    dots_wickets_weak_bowl = p_strong_bat[MatchOutcome.DOT] + p_strong_bat[MatchOutcome.WICKET]
    assert dots_wickets_strong_bowl > dots_wickets_weak_bowl

def test_tailender_penalty():
    """Verify tailenders have heavily suppressed boundary rates."""
    # Tailender: BOWL role and percentile < 25
    p_tailender = synthesize_base_matchup(10, 50, "BOWL")
    # Specialist batter with same low batting percentile
    p_batter = synthesize_base_matchup(10, 50, "BAT")
    
    # Boundary rates for tailender must be heavily suppressed
    assert p_tailender[MatchOutcome.FOUR] < p_batter[MatchOutcome.FOUR]
    assert p_tailender[MatchOutcome.SIX] < p_batter[MatchOutcome.SIX]
    assert p_tailender[MatchOutcome.WICKET] > p_batter[MatchOutcome.WICKET]

def test_bowler_allocation():
    """Verify bowler quotas (max 4 overs/24 balls) and bowler alternation."""
    sim = InningsSimulator(seed=123)
    batting_team = create_mock_team("Bat")
    bowling_team = create_mock_team("Bowl")
    
    res = sim.simulate_innings(batting_team, bowling_team)
    
    # Check that no bowler exceeded 24 legal balls
    bowler_balls = {}
    for log in res.delivery_log:
        if log["outcome"] not in ("WIDE", "NO_BALL"):
            bowler = log["bowler"]
            bowler_balls[bowler] = bowler_balls.get(bowler, 0) + 1
            
    for bowler, balls in bowler_balls.items():
        assert balls <= 24, f"Bowler {bowler} bowled {balls} legal balls, exceeding quota of 24"

    # Check bowler alternation (no bowler bowls consecutive overs)
    last_over_bowler = {}
    for log in res.delivery_log:
        over = log["over"]
        bowler = log["bowler"]
        if over in last_over_bowler:
            assert last_over_bowler[over] == bowler
        else:
            last_over_bowler[over] = bowler
            
    for over in range(1, len(last_over_bowler)):
        assert last_over_bowler[over] != last_over_bowler[over - 1], f"Bowler bowled consecutive overs at over {over}"

def test_strike_rotation():
    """Verify striker swaps on 1/3 runs, end of overs, and wickets."""
    sim = InningsSimulator(seed=42)
    batting_team = create_mock_team("Bat")
    bowling_team = create_mock_team("Bowl")
    
    # Sequences of deterministic outcomes
    outcomes = [
        MatchOutcome.ONE,      # ball 1, striker rotates: Bat_Player_1 -> Bat_Player_2
        MatchOutcome.DOT,      # ball 2, no rotation: Bat_Player_2 faces
        MatchOutcome.TWO,      # ball 3, no rotation: Bat_Player_2 faces
        MatchOutcome.THREE,    # ball 4, striker rotates: Bat_Player_2 -> Bat_Player_1
        MatchOutcome.DOT,      # ball 5, no rotation: Bat_Player_1 faces
        MatchOutcome.DOT,      # ball 6, over completes, striker rotates: Bat_Player_1 -> Bat_Player_2
        MatchOutcome.DOT       # ball 7 (Over 1, Ball 1), Bat_Player_2 faces
    ]
    
    with patch.object(sim, '_sample_outcome', side_effect=itertools.cycle(outcomes)):
        res = sim.simulate_innings(batting_team, bowling_team)
        
        # Verify log match
        assert res.delivery_log[0]["striker"] == "Bat_Player_1"
        assert res.delivery_log[1]["striker"] == "Bat_Player_2"
        assert res.delivery_log[2]["striker"] == "Bat_Player_2"
        assert res.delivery_log[3]["striker"] == "Bat_Player_2"
        assert res.delivery_log[4]["striker"] == "Bat_Player_1"
        assert res.delivery_log[5]["striker"] == "Bat_Player_1"
        # Over completion rotation causes Bat_Player_2 to face ball 7 (index 6)
        assert res.delivery_log[6]["striker"] == "Bat_Player_2"

def test_wicket_strike_rotation():
    """Verify new batsman takes striker end and does not rotate with non-striker under modern rules."""
    sim = InningsSimulator(seed=42)
    batting_team = create_mock_team("Bat")
    bowling_team = create_mock_team("Bowl")
    
    outcomes = [
        MatchOutcome.WICKET,   # ball 1, striker (Bat_Player_1) is out, replaced by Bat_Player_3. No swap with non-striker (Bat_Player_2).
        MatchOutcome.DOT       # ball 2, Bat_Player_3 faces.
    ]
    
    with patch.object(sim, '_sample_outcome', side_effect=itertools.cycle(outcomes)):
        res = sim.simulate_innings(batting_team, bowling_team)
        assert res.delivery_log[0]["striker"] == "Bat_Player_1"
        assert res.delivery_log[1]["striker"] == "Bat_Player_3"

def test_innings_termination_overs():
    """Verify innings terminates after 20 overs (120 legal deliveries)."""
    sim = InningsSimulator(seed=42)
    batting_team = create_mock_team("Bat")
    bowling_team = create_mock_team("Bowl")
    
    # 120 dot balls
    outcomes = [MatchOutcome.DOT] * 125
    with patch.object(sim, '_sample_outcome', side_effect=itertools.cycle(outcomes)):
        res = sim.simulate_innings(batting_team, bowling_team)
        assert res.overs_bowled == 20.0
        assert len(res.delivery_log) == 120

def test_innings_termination_wickets():
    """Verify innings terminates when 10 wickets fall."""
    sim = InningsSimulator(seed=42)
    batting_team = create_mock_team("Bat")
    bowling_team = create_mock_team("Bowl")
    
    # 10 wickets
    outcomes = [MatchOutcome.WICKET] * 12
    with patch.object(sim, '_sample_outcome', side_effect=itertools.cycle(outcomes)):
        res = sim.simulate_innings(batting_team, bowling_team)
        assert res.wickets == 10
        # Should stop after exactly 10 wickets
        assert len(res.delivery_log) == 10

def test_innings_termination_target():
    """Verify innings terminates when target is reached."""
    sim = InningsSimulator(seed=42)
    batting_team = create_mock_team("Bat")
    bowling_team = create_mock_team("Bowl")
    
    # Target is 5 runs.
    # Deliveries: 4 runs, 2 runs. Total = 6 runs. Should terminate on 2nd delivery.
    outcomes = [MatchOutcome.FOUR, MatchOutcome.TWO, MatchOutcome.ONE]
    with patch.object(sim, '_sample_outcome', side_effect=itertools.cycle(outcomes)):
        res = sim.simulate_innings(batting_team, bowling_team, target=5)
        assert res.total_runs == 6
        assert len(res.delivery_log) == 2
