import pytest
from sqlalchemy import text
from app.models.player import Season, Franchise, Player, PlayerSeason
from app.models.squad import FranchiseSeason
from app.models.match import MatchLog
from app.models.draft import DraftSession, DraftPick

pytestmark = pytest.mark.anyio

async def test_db_connection(db_session):
    """Verify that database connection is active and can execute simple statements."""
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()
    assert value == 1

async def test_models_queryable(db_session):
    """Verify that SQLAlchemy schema mapping is correct by querying all defined tables."""
    from sqlalchemy import select
    
    models = [
        Season,
        Franchise,
        Player,
        PlayerSeason,
        FranchiseSeason,
        MatchLog,
        DraftSession,
        DraftPick
    ]
    
    for model in models:
        stmt = select(model).limit(1)
        result = await db_session.execute(stmt)
        assert result is not None

async def test_alembic_migration_applied(db_session):
    """Verify that Alembic migrations have been successfully applied up to the initial schema."""
    result = await db_session.execute(text("SELECT version_num FROM alembic_version"))
    version = result.scalar()
    assert version in ("9fcd2f7f1839", "4b825b3f4516")

