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
    
    # Use the venv alembic binary directly to avoid uv's file-lock
    # deadlocking when called from inside a `uv run pytest` session.
    import sys as _sys
    alembic_bin = os.path.join(
        os.path.dirname(_sys.executable), "alembic"
    )
    # Fallback: try alembic.exe on Windows
    if not os.path.exists(alembic_bin) and os.name == "nt":
        alembic_bin = alembic_bin + ".exe"

#    upgrade_result = subprocess.run(
#        [alembic_bin, "upgrade", "head"],
#        env=env,
#        capture_output=True,
#        text=True,
#        cwd=backend_dir
#    )
#    if upgrade_result.returncode != 0:
#        # Don't hard-fail if the DB is already at head or unreachable —
#        # simulation tests are pure-Python and don't need the DB.
#        import warnings
#        warnings.warn(
#            f"Alembic upgrade returned non-zero: {upgrade_result.returncode}\n"
#            f"{upgrade_result.stderr}\n{upgrade_result.stdout}",
#            stacklevel=2,
#        )
        
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

@pytest.fixture(autouse=True)
def override_db_dependency(request):
    import inspect
    if inspect.iscoroutinefunction(request.node.obj):
        db_session = request.getfixturevalue("db_session")
        from app.main import app
        from app.core.database import get_db
        async def _get_db_override():
            yield db_session
        app.dependency_overrides[get_db] = _get_db_override
        yield
        app.dependency_overrides.pop(get_db, None)
    else:
        yield
