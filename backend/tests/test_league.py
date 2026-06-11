import os
import pytest
from httpx import AsyncClient, ASGITransport
import uuid

# Configure test environment
os.environ["REDIS_URL"] = "redis://localhost:6379/2"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft_test"

from app.main import app
from app.models.draft import DraftSession, DraftPick
from app.models.player import Season, Franchise, Player, PlayerSeason
from app.models.squad import FranchiseSeason
from app.core.redis import get_redis, init_redis_pool, close_redis_pool

pytestmark = pytest.mark.anyio

@pytest.fixture(autouse=True)
async def setup_redis():
    await init_redis_pool()
    redis = get_redis()
    await redis.flushdb()
    yield
    await redis.flushdb()
    await close_redis_pool()

async def test_start_league(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Seed Season and Franchise
        season = Season(id=uuid.uuid4(), year=2024, name="IPL 2024")
        db_session.add(season)
        rcb = Franchise(id=uuid.uuid4(), name="Royal Challengers Bangalore", code="RCB")
        db_session.add(rcb)
        await db_session.flush()
        
        fs_rcb = FranchiseSeason(id=uuid.uuid4(), franchise_id=rcb.id, season_id=season.id)
        db_session.add(fs_rcb)
        
        # We need 11 players for the roster, including at least 1 WK and 3 bowlers
        players_info = [
            ("Player 1", "WK", False),
            ("Player 2", "BOWL", False),
            ("Player 3", "BOWL", False),
            ("Player 4", "BOWL", False),
            ("Player 5", "BAT", False),
            ("Player 6", "BAT", False),
            ("Player 7", "BAT", False),
            ("Player 8", "BAT", False),
            ("Player 9", "BAT", False),
            ("Player 10", "BAT", False),
            ("Player 11", "BAT", False),
        ]
        
        draft_session_id = uuid.uuid4()
        draft = DraftSession(
            id=draft_session_id,
            status="COMPLETED",
            budget_remaining=10.0
        )
        db_session.add(draft)
        await db_session.flush()
        
        for idx, (name, role, is_overseas) in enumerate(players_info):
            p = Player(id=uuid.uuid4(), name=name, country="India", role=role, is_overseas=is_overseas)
            db_session.add(p)
            await db_session.flush()
            
            ps = PlayerSeason(
                id=uuid.uuid4(),
                player_id=p.id,
                season_id=season.id,
                franchise_id=rcb.id,
                credit_cost=6.0,
                percentile_batting=80,
                percentile_bowling=80
            )
            db_session.add(ps)
            await db_session.flush()
            
            pick = DraftPick(
                id=uuid.uuid4(),
                draft_session_id=draft_session_id,
                player_id=p.id,
                player_season_id=ps.id,
                pick_number=idx + 1
            )
            db_session.add(pick)
            
        await db_session.commit()

        response = await ac.post(f"/api/league/start/{draft_session_id}")
        assert response.status_code == 201
        data = response.json()
        assert data["draft_session_id"] == str(draft_session_id)
        assert len(data["matches"]) == 14
        assert data["matches"][0]["status"] == "completed"

        # Test get league
        get_response = await ac.get(f"/api/league/{draft_session_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert len(get_data["matches"]) == 14

async def test_start_league_in_progress_draft(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        draft_session_id = uuid.uuid4()
        draft = DraftSession(
            id=draft_session_id,
            status="IN_PROGRESS",
            budget_remaining=10.0
        )
        db_session.add(draft)
        await db_session.commit()

        response = await ac.post(f"/api/league/start/{draft_session_id}")
        assert response.status_code == 400
        assert "not COMPLETED" in response.json()["detail"]
