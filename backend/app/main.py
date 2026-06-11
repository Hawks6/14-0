from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.core.redis import init_redis_pool, close_redis_pool
from app.api.draft import router as draft_router
from app.api.league import router as league_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing application services...")
    # Initialize Redis Connection pool
    await init_redis_pool()
    yield
    # Shutdown actions
    logger.info("Shutting down application services...")
    await close_redis_pool()
    from app.core.database import engine
    await engine.dispose()



from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="14-0: IPL Draft & Simulation Platform",
    description="Markov Chain based IPL Match Simulation and Draft solver backend.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(draft_router)
app.include_router(league_router)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy"}
