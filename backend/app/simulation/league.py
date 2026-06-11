import uuid
from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, computed_field
from dataclasses import dataclass
from app.simulation.simulator import InningsSimulator, InningsResult
from app.simulation.modifiers import SimulationModifier

@dataclass
class Team:
    id: str
    name: str
    batting_lineup: List[Any]
    bowling_lineup: List[Any]

class TeamStanding(BaseModel):
    team_id: str
    team_name: str
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    points: int = 0
    runs_scored: int = 0
    overs_faced: float = 0.0
    runs_conceded: int = 0
    overs_bowled: float = 0.0

    @computed_field
    @property
    def net_run_rate(self) -> float:
        if self.overs_faced == 0 or self.overs_bowled == 0:
            return 0.0
        # For NRR, calculate average runs per over
        # overs_faced is typically in standard format, wait! 
        # Actually 19.3 overs = 19 + 3/6 overs in NRR calculation.
        # But our simulator returns overs as e.g. 19.5 which means 19 overs + 3 balls (since 3/6 = 0.5).
        # Let's confirm how simulator.py calculates overs_bowled.
        # total_overs = state.overs_completed + (state.balls_completed / 6.0)
        # So overs_faced is already a float like 19.5 for 19.3 overs.
        
        return (self.runs_scored / self.overs_faced) - (self.runs_conceded / self.overs_bowled)

@dataclass
class MatchSimulationResult:
    match_id: str
    team1_id: str
    team2_id: str
    team1_innings: InningsResult
    team2_innings: InningsResult
    winner_id: Optional[str]
    is_tie: bool
    margin_runs: Optional[int]
    margin_wickets: Optional[int]

class LeagueOrchestrator:
    def __init__(self, teams: List[Team], seed: Optional[int] = None, modifiers: Optional[List[SimulationModifier]] = None):
        self.teams = {str(t.id): t for t in teams}
        self.standings = {
            str(t.id): TeamStanding(team_id=str(t.id), team_name=t.name)
            for t in teams
        }
        self.seed = seed
        self.modifiers = modifiers
        self.match_results: List[MatchSimulationResult] = []

    def simulate_match(self, team1_id: str, team2_id: str, match_id: Optional[str] = None) -> MatchSimulationResult:
        if match_id is None:
            match_id = str(uuid.uuid4())
            
        team1 = self.teams[team1_id]
        team2 = self.teams[team2_id]
        
        sim = InningsSimulator(seed=self.seed, modifiers=self.modifiers)
        
        # Innings 1: Team 1 bats, Team 2 bowls
        team1_innings = sim.simulate_innings(
            batting_lineup=team1.batting_lineup,
            bowling_lineup=team2.bowling_lineup
        )
        
        target = team1_innings.total_runs + 1
        
        # Innings 2: Team 2 bats, Team 1 bowls
        # Provide target
        team2_innings = sim.simulate_innings(
            batting_lineup=team2.batting_lineup,
            bowling_lineup=team1.bowling_lineup,
            target=target
        )
        
        # Determine winner
        winner_id = None
        is_tie = False
        margin_runs = None
        margin_wickets = None
        
        if team2_innings.total_runs >= target:
            winner_id = team2_id
            margin_wickets = 10 - team2_innings.wickets
        elif team2_innings.total_runs == team1_innings.total_runs:
            is_tie = True
        else:
            winner_id = team1_id
            margin_runs = team1_innings.total_runs - team2_innings.total_runs
            
        result = MatchSimulationResult(
            match_id=match_id,
            team1_id=team1_id,
            team2_id=team2_id,
            team1_innings=team1_innings,
            team2_innings=team2_innings,
            winner_id=winner_id,
            is_tie=is_tie,
            margin_runs=margin_runs,
            margin_wickets=margin_wickets
        )
        
        self.match_results.append(result)
        self._update_standings(result)
        
        # alter the seed for variance across matches
        if self.seed is not None:
            self.seed += 1
            
        return result

    def _update_standings(self, result: MatchSimulationResult):
        t1_standing = self.standings[result.team1_id]
        t2_standing = self.standings[result.team2_id]
        
        t1_standing.matches_played += 1
        t2_standing.matches_played += 1
        
        if result.is_tie:
            t1_standing.ties += 1
            t2_standing.ties += 1
            t1_standing.points += 1
            t2_standing.points += 1
        elif result.winner_id == result.team1_id:
            t1_standing.wins += 1
            t2_standing.losses += 1
            t1_standing.points += 2
        else:
            t2_standing.wins += 1
            t1_standing.losses += 1
            t2_standing.points += 2
            
        # Update runs and overs for NRR
        # Note on NRR: if a team is bowled out, their overs faced is 20.0
        
        t1_overs_faced = 20.0 if result.team1_innings.wickets == 10 else result.team1_innings.overs_bowled
        t2_overs_faced = 20.0 if result.team2_innings.wickets == 10 else result.team2_innings.overs_bowled
        
        t1_overs_bowled = t2_overs_faced
        t2_overs_bowled = t1_overs_faced
        
        # Add to T1
        t1_standing.runs_scored += result.team1_innings.total_runs
        t1_standing.overs_faced += t1_overs_faced
        t1_standing.runs_conceded += result.team2_innings.total_runs
        t1_standing.overs_bowled += t1_overs_bowled
        
        # Add to T2
        t2_standing.runs_scored += result.team2_innings.total_runs
        t2_standing.overs_faced += t2_overs_faced
        t2_standing.runs_conceded += result.team1_innings.total_runs
        t2_standing.overs_bowled += t2_overs_bowled

    def simulate_season(self, schedule: List[Tuple[str, str]]) -> List[MatchSimulationResult]:
        results = []
        for t1, t2 in schedule:
            res = self.simulate_match(t1, t2)
            results.append(res)
        return results

    def get_standings(self) -> List[TeamStanding]:
        return sorted(
            self.standings.values(),
            key=lambda x: (x.points, x.net_run_rate),
            reverse=True
        )
