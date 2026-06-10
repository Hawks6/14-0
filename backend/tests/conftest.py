import os
import sys
import pytest
import subprocess
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft_test"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Set the DATABASE_URL environment variable to ensure Alembic and app models use the test database
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_DATABASE_URL
    
    # Run migrations using Alembic
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Run upgrade head to apply all migrations
    upgrade_result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        env=env,
        capture_output=True,
        text=True,
        cwd=backend_dir
    )
    if upgrade_result.returncode != 0:
        raise RuntimeError(f"Alembic upgrade failed:\n{upgrade_result.stderr}\n{upgrade_result.stdout}")
        
    yield
    
    # Optional cleanup (can be skipped or we can drop/downgrade)

from sqlalchemy.pool import NullPool

@pytest.fixture(scope="session")
def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    yield engine
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        # if the loop is already running, run it as a task
        loop.create_task(engine.dispose())
    else:
        loop.run_until_complete(engine.dispose())

@pytest.fixture
async def db_session(db_engine):
    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        yield session
        await session.close()
        await transaction.rollback()
