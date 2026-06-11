import uuid
import pytest
from app.simulation.league import Team, LeagueOrchestrator, TeamStanding
from app.simulation.simulator import InningsResult

class MockPlayer:
    def __init__(self, id, name, role, percentile_batting, percentile_bowling):
        self.id = id
        self.name = name
        self.role = role
        self.percentile_batting = percentile_batting
        self.percentile_bowling = percentile_bowling

def create_mock_team(prefix, team_id):
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
    return Team(
        id=team_id,
        name=prefix,
        batting_lineup=players,
        bowling_lineup=players
    )

def test_league_initialization():
    t1 = create_mock_team("Team 1", "t1")
    t2 = create_mock_team("Team 2", "t2")
    
    league = LeagueOrchestrator(teams=[t1, t2])
    
    assert len(league.teams) == 2
    assert "t1" in league.standings
    assert "t2" in league.standings
    assert league.standings["t1"].team_name == "Team 1"

def test_single_match_simulation():
    t1 = create_mock_team("Team 1", "t1")
    t2 = create_mock_team("Team 2", "t2")
    
    league = LeagueOrchestrator(teams=[t1, t2], seed=42)
    result = league.simulate_match("t1", "t2")
    
    assert result.team1_id == "t1"
    assert result.team2_id == "t2"
    assert result.winner_id in ["t1", "t2", None]
    
    standings = league.get_standings()
    assert standings[0].matches_played == 1
    assert standings[1].matches_played == 1
    
    # 1 win, 1 loss (assuming no tie for this seed)
    if not result.is_tie:
        assert standings[0].points == 2
        assert standings[1].points == 0
        assert standings[0].wins == 1
        assert standings[1].losses == 1

def test_season_simulation():
    teams = [create_mock_team(f"Team {i}", f"t{i}") for i in range(4)]
    league = LeagueOrchestrator(teams=teams, seed=100)
    
    # Round robin schedule (each plays each other once)
    schedule = [
        ("t0", "t1"),
        ("t2", "t3"),
        ("t0", "t2"),
        ("t1", "t3"),
        ("t0", "t3"),
        ("t1", "t2")
    ]
    
    results = league.simulate_season(schedule)
    assert len(results) == 6
    
    standings = league.get_standings()
    
    # Check that each team played 3 matches
    for st in standings:
        assert st.matches_played == 3
        assert st.wins + st.losses + st.ties == 3
        
    # Total points should be 12 (6 matches * 2 pts per match)
    total_points = sum(st.points for st in standings)
    assert total_points == 12

def test_net_run_rate_calculation():
    # Construct synthetic standings to test NRR math directly
    st = TeamStanding(team_id="t1", team_name="T1")
    
    # 20 overs scored 160 (run rate = 8.0)
    # 20 overs conceded 140 (run rate = 7.0)
    # NRR = +1.0
    st.runs_scored = 160
    st.overs_faced = 20.0
    st.runs_conceded = 140
    st.overs_bowled = 20.0
    
    assert st.net_run_rate == 1.0
    
    # Bowled out scenarios (overs_faced implicitly 20.0 when 10 wickets)
    # In league code, if bowled out, overs_faced is set to 20.0 before adding to standings
    # We will test the actual simulator update for bowled out scenario
    
    t1 = create_mock_team("Team 1", "t1")
    t2 = create_mock_team("Team 2", "t2")
    league = LeagueOrchestrator(teams=[t1, t2])
    
    # Create fake match result where T1 is bowled out for 100 in 15.0 overs
    # T2 chases it in 10.0 overs
    
    t1_innings = InningsResult(
        total_runs=100,
        wickets=10,
        overs_bowled=15.0,
        extras=0,
        delivery_log=[]
    )
    
    t2_innings = InningsResult(
        total_runs=102,
        wickets=2,
        overs_bowled=10.0,
        extras=0,
        delivery_log=[]
    )
    
    from app.simulation.league import MatchSimulationResult
    
    fake_result = MatchSimulationResult(
        match_id="m1",
        team1_id="t1",
        team2_id="t2",
        team1_innings=t1_innings,
        team2_innings=t2_innings,
        winner_id="t2",
        is_tie=False,
        margin_runs=None,
        margin_wickets=8
    )
    
    league._update_standings(fake_result)
    
    st1 = league.standings["t1"]
    st2 = league.standings["t2"]
    
    # For T1 (bowled out): overs_faced = 20.0, runs_scored = 100. RR = 5.0
    # overs_bowled = 10.0, runs_conceded = 102. Conceded RR = 10.2
    # NRR = 5.0 - 10.2 = -5.2
    
    assert st1.overs_faced == 20.0
    assert st1.runs_scored == 100
    assert st1.overs_bowled == 10.0
    assert st1.runs_conceded == 102
    assert pytest.approx(st1.net_run_rate) == -5.2
    
    # For T2: overs_faced = 10.0, runs_scored = 102. RR = 10.2
    # overs_bowled = 20.0 (since T1 bowled out), runs_conceded = 100. Conceded RR = 5.0
    # NRR = +5.2
    assert st2.overs_faced == 10.0
    assert st2.runs_scored == 102
    assert st2.overs_bowled == 20.0
    assert st2.runs_conceded == 100
    assert pytest.approx(st2.net_run_rate) == 5.2
