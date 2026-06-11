import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.simulation.ai_squads import generate_optimal_squad, generate_tournament_schedule
from app.models.player import Player, Season, Franchise, PlayerSeason
from app.models.squad import FranchiseSeason
import app.models.draft  # Import to register DraftPick in SQLAlchemy

def test_generate_optimal_squad_success():
    candidates = []
    # Create 15 candidates
    for i in range(15):
        role = "BOWL" if i < 6 else ("WK" if i == 6 else "BAT")
        candidates.append({
            "player_id": str(uuid.uuid4()),
            "player_season_id": str(uuid.uuid4()),
            "name": f"Player {i}",
            "role": role,
            "is_overseas": False,
            "credit_cost": 8.5,
            "percentile_batting": 50,
            "percentile_bowling": 50
        })
        
    squad = generate_optimal_squad(candidates)
    assert len(squad) == 11
    
    # Check constraints
    wk_count = sum(1 for p in squad if p["role"] == "WK")
    bowl_count = sum(1 for p in squad if p["role"] == "BOWL")
    cost = sum(p["credit_cost"] for p in squad)
    
    assert wk_count == 1
    assert bowl_count >= 3
    assert cost <= 100.0

def test_generate_optimal_squad_infeasible():
    candidates = []
    # Only 10 candidates -> infeasible
    for i in range(10):
        candidates.append({
            "player_id": str(uuid.uuid4()),
            "role": "BAT",
            "is_overseas": False,
            "credit_cost": 8.0,
            "percentile_batting": 50,
            "percentile_bowling": 50
        })
        
    squad = generate_optimal_squad(candidates)
    assert len(squad) == 0

class MockResult:
    def __init__(self, data):
        self._data = data
    def scalars(self):
        class MockScalars:
            def all(self_inner):
                return self._data
        return MockScalars()

@pytest.mark.anyio
async def test_generate_tournament_schedule_mocked():
    class MockSession:
        async def execute(self, query):
            # If querying FranchiseSeason
            if "franchise_seasons" in str(query).lower():
                fs = FranchiseSeason(id=uuid.uuid4(), franchise_id=uuid.uuid4(), season_id=uuid.uuid4())
                fs.franchise = Franchise(name="Mock Franchise")
                fs.season = Season(year=2020)
                return MockResult([fs])
            # If querying PlayerSeason
            if "player_seasons" in str(query).lower():
                players = []
                for i in range(15):
                    role = "BOWL" if i < 6 else ("WK" if i == 6 else "BAT")
                    p = Player(name=f"Player {i}", role=role, is_overseas=False)
                    ps = PlayerSeason(
                        id=uuid.uuid4(),
                        player_id=uuid.uuid4(),
                        credit_cost=8.5,
                        percentile_batting=50,
                        percentile_bowling=50
                    )
                    ps.player = p
                    players.append(ps)
                return MockResult(players)
            return MockResult([])

    session = MockSession()
    schedule = await generate_tournament_schedule(session, num_matches=2)
    assert len(schedule) == 2
    assert schedule[0]["franchise_name"] == "Mock Franchise"
    assert len(schedule[0]["squad"]) == 11
    assert schedule[1]["franchise_name"] == "Mock Franchise"
