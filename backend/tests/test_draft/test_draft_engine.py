import os
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

# Configure test Redis and Database URLs before importing application modules
os.environ["REDIS_URL"] = "redis://localhost:6379/2"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft_test"

from app.main import app
from app.models.player import Season, Franchise, Player, PlayerSeason
from app.models.squad import FranchiseSeason
from app.core.redis import get_redis, init_redis_pool, close_redis_pool


pytestmark = pytest.mark.anyio


@pytest.fixture(autouse=True)
async def setup_redis():
    # Ensure Redis is initialized for the test execution
    await init_redis_pool()
    redis = get_redis()
    await redis.flushdb() # Clear test Redis DB
    yield
    await redis.flushdb()
    await close_redis_pool()


@pytest.fixture
async def seed_data(db_session):
    """Seed database with dummy seasons, franchises, players, and ratings."""
    # Clear existing tables to ensure clean state
    await db_session.execute(text("TRUNCATE TABLE draft_picks CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE draft_sessions CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE player_seasons CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE franchise_seasons CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE players CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE franchises CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE seasons CASCADE"))
    await db_session.commit()

    # Create a Season
    season = Season(id=uuid.uuid4(), year=2024, name="IPL 2024")
    db_session.add(season)
    
    # Create Franchises
    rcb = Franchise(id=uuid.uuid4(), name="Royal Challengers Bangalore", code="RCB")
    mi = Franchise(id=uuid.uuid4(), name="Mumbai Indians", code="MI")
    db_session.add_all([rcb, mi])
    await db_session.flush()
    
    # Create FranchiseSeasons
    fs_rcb = FranchiseSeason(id=uuid.uuid4(), franchise_id=rcb.id, season_id=season.id)
    fs_mi = FranchiseSeason(id=uuid.uuid4(), franchise_id=mi.id, season_id=season.id)
    db_session.add_all([fs_rcb, fs_mi])
    
    # Create Players
    players_data = [
        # RCB Squad: 6 players (1 WK, 2 Bowlers, 1 Overseas WK, 2 Overseas Bowlers/BAT)
        ("Virat Kohli", "India", "BAT", False, 11.5, 99, 10),
        ("Faf du Plessis", "South Africa", "BAT", True, 9.0, 80, 5),
        ("Dinesh Karthik", "India", "WK", False, 8.5, 75, 5),
        ("Mohammed Siraj", "India", "BOWL", False, 9.0, 10, 85),
        ("Lockie Ferguson", "New Zealand", "BOWL", True, 8.0, 5, 75),
        ("Glenn Maxwell", "Australia", "ALLROUNDER", True, 9.5, 85, 70),
        
        # MI Squad: 6 players
        ("Rohit Sharma", "India", "BAT", False, 10.5, 95, 5),
        ("Jasprit Bumrah", "India", "BOWL", False, 12.0, 5, 99),
        ("Ishan Kishan", "India", "WK", False, 9.5, 85, 5),
        ("Hardik Pandya", "India", "ALLROUNDER", False, 10.0, 85, 85),
        ("Gerald Coetzee", "South Africa", "BOWL", True, 8.5, 10, 80),
        ("Tim David", "Australia", "BAT", True, 8.0, 75, 20),
    ]
    
    db_players = []
    db_player_seasons = []
    
    for name, country, role, is_overseas, cost, bat_pct, bowl_pct in players_data:
        p = Player(id=uuid.uuid4(), name=name, country=country, role=role, is_overseas=is_overseas)
        db_session.add(p)
        db_players.append(p)
        await db_session.flush()
        
        # Associate with franchise (RCB for first 6, MI for last 6)
        franchise_id = rcb.id if len(db_players) <= 6 else mi.id
        ps = PlayerSeason(
            id=uuid.uuid4(),
            player_id=p.id,
            season_id=season.id,
            franchise_id=franchise_id,
            credit_cost=cost,
            percentile_batting=bat_pct,
            percentile_bowling=bowl_pct
        )
        db_session.add(ps)
        db_player_seasons.append(ps)
        
    await db_session.commit()
    return {
        "season": season,
        "franchises": [rcb, mi],
        "franchise_seasons": [fs_rcb, fs_mi],
        "players": db_players,
        "player_seasons": db_player_seasons
    }


async def test_create_session(seed_data):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/draft/session", json={})
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "IN_PROGRESS"
        assert data["budget_remaining"] == 100.0
        assert data["picks"] == []


async def test_trigger_spin(seed_data):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create session
        res_create = await ac.post("/api/draft/session", json={})
        session_id = res_create.json()["id"]

        # Trigger spin
        res_spin = await ac.post(f"/api/draft/session/{session_id}/spin")
        assert res_spin.status_code == 200
        spin_data = res_spin.json()
        assert "franchise_name" in spin_data
        assert "year" in spin_data
        assert len(spin_data["players"]) == 6


async def test_draft_pick_success(seed_data):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create session
        res_create = await ac.post("/api/draft/session", json={})
        session_id = res_create.json()["id"]

        # Spin to get pool
        res_spin = await ac.post(f"/api/draft/session/{session_id}/spin")
        spin_data = res_spin.json()
        picked_player = spin_data["players"][0] # pick first player

        # Pick player
        res_pick = await ac.post(
            f"/api/draft/session/{session_id}/pick",
            json={"player_season_id": picked_player["player_season_id"]}
        )
        assert res_pick.status_code == 200
        pick_data = res_pick.json()
        assert len(pick_data["picks"]) == 1
        assert pick_data["picks"][0]["name"] == picked_player["name"]
        expected_budget = 100.0 - picked_player["credit_cost"]
        assert pick_data["budget_remaining"] == round(expected_budget, 1)


async def test_draft_pick_invalid_player(seed_data):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_create = await ac.post("/api/draft/session", json={})
        session_id = res_create.json()["id"]

        # Spin
        await ac.post(f"/api/draft/session/{session_id}/spin")

        # Pick an invalid/random player UUID
        random_uuid = str(uuid.uuid4())
        res_pick = await ac.post(
            f"/api/draft/session/{session_id}/pick",
            json={"player_season_id": random_uuid}
        )
        assert res_pick.status_code == 400
        assert "not part of the current spin pool" in res_pick.json()["detail"]


async def test_draft_pick_overseas_constraint(seed_data):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_create = await ac.post("/api/draft/session", json={})
        session_id = res_create.json()["id"]

        # Force add 4 overseas players into picks via Redis cache manually to test constraint boundary,
        # or simulate spinning and drafting overseas. Let's do it via spin-draft mock.
        # To make it fast, we can spin, draft an overseas, then spin again, etc.
        # But wait, seed data has Glenn Maxwell (overseas), Lockie Ferguson (overseas), Faf du Plessis (overseas) in RCB,
        # and Gerald Coetzee (overseas), Tim David (overseas) in MI.
        # We can draft 4 overseas players successfully, then trying to draft a 5th overseas should fail.
        
        # Let's draft 4 overseas players:
        overseas_drafted = 0
        for _ in range(10): # up to 10 spins/picks to find overseas
            res_spin = await ac.post(f"/api/draft/session/{session_id}/spin")
            spin_data = res_spin.json()
            
            # Find an overseas player in the spin pool who hasn't been drafted yet
            redis = get_redis()
            sess = await redis.get(f"draft:session:{session_id}")
            import json
            drafted_names = {p["name"] for p in json.loads(sess)["picks"]}
            
            target = None
            for p in spin_data["players"]:
                if p["is_overseas"] and p["name"] not in drafted_names:
                    target = p
                    break
            
            if target:
                res_pick = await ac.post(
                    f"/api/draft/session/{session_id}/pick",
                    json={"player_season_id": target["player_season_id"]}
                )
                assert res_pick.status_code == 200
                overseas_drafted += 1
                if overseas_drafted == 4:
                    break

        assert overseas_drafted == 4
        
        # Now try to draft a 5th overseas player
        res_spin = await ac.post(f"/api/draft/session/{session_id}/spin")
        spin_data = res_spin.json()
        
        sess = await get_redis().get(f"draft:session:{session_id}")
        drafted_names = {p["name"] for p in json.loads(sess)["picks"]}
        
        target_5th = None
        for p in spin_data["players"]:
            if p["is_overseas"] and p["name"] not in drafted_names:
                target_5th = p
                break
                
        if target_5th:
            res_pick = await ac.post(
                f"/api/draft/session/{session_id}/pick",
                json={"player_season_id": target_5th["player_season_id"]}
            )
            assert res_pick.status_code == 400
            assert "overseas" in res_pick.json()["detail"].lower()


async def test_draft_pick_unsolvable_warning(seed_data):
    """
    Test that the solver detects when a pick leaves the draft unsolvable.
    For example:
    If a user has 2 remaining slots and has not drafted a Wicketkeeper (WK).
    But they pick a player which leaves them with only 4.0 credits.
    If the cheapest Wicketkeeper in the database costs 8.5 credits,
    this pick should make the draft mathematically impossible and be blocked.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_create = await ac.post("/api/draft/session", json={})
        session_id = res_create.json()["id"]

        # Manually alter the Redis draft state to simulate having drafted 9 players
        # with remaining budget = 10.0 credits, and NO Wicketkeeper (WK) drafted.
        # The only WK in seed_data are Dinesh Karthik (cost 8.5) and Ishan Kishan (cost 9.5).
        # We will set budget_remaining to 12.0.
        # If they pick a player costing 6.0, budget_remaining becomes 6.0, leaving 1 slot left (which MUST be a WK),
        # but the cheapest WK is 8.5, which is > 6.0. This is unsolvable!
        redis = get_redis()
        session_state = await get_draft_session(str(session_id))
        
        # Build 9 dummy picks (none of them are WK, and none are duplicate player IDs of the ones in seed_data)
        # We can use the players from seed_data but change their roles to 'BAT' to ensure they don't count as WK.
        # Let's add 9 picks costing a total of 88.0 credits.
        dummy_picks = []
        for i in range(9):
            dummy_picks.append({
                "pick_number": i + 1,
                "player_id": str(uuid.uuid4()),
                "player_season_id": str(uuid.uuid4()),
                "name": f"Dummy Player {i}",
                "role": "BAT", # No WK
                "is_overseas": False,
                "credit_cost": 9.5
            })
            
        session_state["picks"] = dummy_picks
        session_state["budget_remaining"] = 12.0 # 100.0 - 9.5*9 = 85.5, but let's override to 12.0
        
        # Now set the spin pool to contain:
        # A player costing 6.0 credits (role: BAT)
        # A player costing 11.5 credits (role: BAT)
        spin_player_1 = {
            "player_season_id": str(seed_data["player_seasons"][0].id), # Virat Kohli
            "player_id": str(seed_data["player_seasons"][0].player_id),
            "name": "Virat Kohli",
            "country": "India",
            "role": "BAT",
            "is_overseas": False,
            "credit_cost": 6.0, # override cost
            "percentile_batting": 99,
            "percentile_bowling": 10
        }
        
        session_state["current_spin_players"] = [spin_player_1]
        session_state["current_spin_franchise_id"] = str(seed_data["franchises"][0].id)
        session_state["current_spin_season_id"] = str(seed_data["season"].id)
        
        await save_draft_session(str(session_id), session_state)
        
        # Attempt to draft Virat Kohli (cost 6.0). 
        # This leaves 12.0 - 6.0 = 6.0 credits, and 1 slot.
        # Since we have NO Wicketkeeper in the 10 picks, the last slot MUST be a Wicketkeeper.
        # However, the cheapest WK in the DB (seed_data) is Dinesh Karthik at 8.5 credits, which exceeds 6.0 credits.
        # The solver should catch this and return 400 Bad Request!
        res_pick = await ac.post(
            f"/api/draft/session/{session_id}/pick",
            json={"player_season_id": spin_player_1["player_season_id"]}
        )
        assert res_pick.status_code == 400
        assert "mathematically impossible" in res_pick.json()["detail"].lower()
