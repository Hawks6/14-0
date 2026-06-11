import os
import pytest
from httpx import AsyncClient, ASGITransport
import uuid

# Configure test environment
os.environ["REDIS_URL"] = "redis://localhost:6379/2"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft_test"

from app.main import app
from app.models.draft import DraftSession
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
        draft_session_id = uuid.uuid4()
        draft = DraftSession(
            id=draft_session_id,
            status="COMPLETED",
            budget_remaining=10.0
        )
        db_session.add(draft)
        await db_session.commit()

        response = await ac.post(f"/api/league/start/{draft_session_id}")
        assert response.status_code == 201
        data = response.json()
        assert data["draft_session_id"] == str(draft_session_id)
        assert len(data["matches"]) == 14
        assert data["matches"][0]["status"] == "SCHEDULED"

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
