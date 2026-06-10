# Phase 01: Data Model & Ingestion Engine — Research Document

## 1. Summary
Phase 01 establishes the foundational data model, database schema, and ingestion pipeline for the 14-0 IPL Draft & Simulation Platform. This phase translates historical IPL player statistics and franchise rosters into a normalized, database-backed format, preparing the data for consumption by the simulation and draft engines. 

The core challenges are:
1. **Era Calibration**: Normalizing player statistics across seasons (e.g. comparing 2008 ratings to 2024 ratings) using season-relative percentile rankings on a 0–99 scale.
2. **Data Integrity**: Filtering out noise by enforcing a 30-ball minimum threshold for rating calculation, falling back to a baseline rating of 50 for low-sample players.
3. **Ingestion Speed**: Building a high-performance Python CLI loader that validates raw datasets against Pydantic schemas and bulk-inserts them into PostgreSQL 18 using `asyncpg` binary `COPY` streams.

---

## 2. Standard Stack

### PostgreSQL 18
- **Role**: Durable, relational storage for player profiles, ratings, active draft sessions, and event-sourced ball-by-ball match logs.
- **Key Configuration**:
  - **Memory Tuning**: Allocate standard development limits (`shared_buffers` to 25% of system RAM, `work_mem` to 16MB to allow rapid in-memory sorting of windowed ranking queries).
  - **JSONB Optimization**: Utilize `JSONB` for storing flexible match statistics or draft selections, with `GIN` indexing to speed up search.
  - **Partitioning**: Structure `match_logs` as a partitioned table by `season_id` or `year` to optimize query performance during large-scale historical analysis.

### SQLAlchemy 2.0 (Async)
- **Role**: Modern, type-safe Object Relational Mapper (ORM).
- **Core Patterns**:
  - **Async Dialect**: Use the `postgresql+asyncpg` dialect.
  - **Type-safe Declarative mapping**: Use `Mapped[...]` and `mapped_column` to declare database fields.
  - **Async Session Management**: Manage connection lifecycles via `async_sessionmaker` and `AsyncSession`, ensuring connections are pooled using `create_async_engine(pool_size=10, max_overflow=20, pool_pre_ping=True)`.

### Alembic 1.18
- **Role**: Database schema migrations.
- **Setup Pattern**:
  - Initialize the project using the asynchronous template: `alembic init -t async alembic`.
  - Configure `env.py` to read connection parameters dynamically from the app configuration and leverage `run_async()` to apply schema alterations safely.

### pandas 3.0
- **Role**: Data normalization and processing engine.
- **Important v3.0 Features**:
  - **Copy-on-Write (CoW)**: Now enabled by default, improving memory consumption and preventing silent side-effect modifications during normalization operations.
  - **Arrow Integration**: Utilize PyArrow backends (`dtype_backend="pyarrow"`) for faster, more memory-efficient string and integer parsing of CSV datasets.

---

## 3. Architecture Patterns

### Database Schema Design
We design the schema to reflect the relational nature of players, seasons, and match historical contexts:

```mermaid
erDiagram
    SEASONS ||--o{ FRANCHISE_SEASONS : "belongs to"
    FRANCHISES ||--o{ FRANCHISE_SEASONS : "belongs to"
    PLAYERS ||--o{ PLAYER_SEASONS : "has statistical record for"
    SEASONS ||--o{ PLAYER_SEASONS : "contains stats for"
    FRANCHISES ||--o{ PLAYER_SEASONS : "rosters player in"
    DRAFT_SESSIONS ||--o{ DRAFT_PICKS : "contains picks"
    PLAYERS ||--o{ DRAFT_PICKS : "is selected in"
    MATCH_LOGS ||--|| PLAYERS : "records striker"
    MATCH_LOGS ||--|| PLAYERS : "records bowler"
```

#### Table Definitions
1. **`seasons`**: Defines the historical IPL seasons.
   - `id` (UUID, PK)
   - `year` (INT, Unique)
   - `name` (VARCHAR)
2. **`franchises`**: Historical franchises (e.g. RCB, CSK).
   - `id` (UUID, PK)
   - `name` (VARCHAR)
   - `code` (VARCHAR, Unique - e.g. "RCB")
3. **`franchise_seasons`**: Map franchises to specific years and credit settings.
   - `id` (UUID, PK)
   - `franchise_id` (UUID, FK)
   - `season_id` (UUID, FK)
4. **`players`**: General player profiles.
   - `id` (UUID, PK)
   - `name` (VARCHAR)
   - `country` (VARCHAR)
   - `role` (ENUM: 'BAT', 'BOWL', 'ALLROUNDER', 'WK')
   - `is_overseas` (BOOLEAN)
5. **`player_seasons`**: Season-specific ratings and statistics.
   - `id` (UUID, PK)
   - `player_id` (UUID, FK)
   - `season_id` (UUID, FK)
   - `franchise_id` (UUID, FK)
   - `balls_faced` (INT), `runs_scored` (INT), `balls_bowled` (INT), `wickets_taken` (INT)
   - `raw_batting_rating` (FLOAT), `raw_bowling_rating` (FLOAT)
   - `percentile_batting` (INT) — *Normalized rating [0-99]*
   - `percentile_bowling` (INT) — *Normalized rating [0-99]*
   - `credit_cost` (INT) — *Calculated using exponential rating-to-cost scaling*
6. **`draft_sessions`**: Tracks active draft instances.
   - `id` (UUID, PK)
   - `user_id` (UUID, Nullable)
   - `status` (VARCHAR - e.g. "IN_PROGRESS", "COMPLETED")
   - `budget_remaining` (INT)
   - `created_at` (TIMESTAMP)
7. **`draft_picks`**: Maps selected players to draft sessions.
   - `id` (UUID, PK)
   - `draft_session_id` (UUID, FK)
   - `player_id` (UUID, FK)
   - `pick_number` (INT)
8. **`match_logs`**: Event-sourced ball-by-ball database logs for playback verification.
   - `id` (UUID, PK)
   - `match_id` (UUID)
   - `ball_number` (INT)
   - `over_number` (INT)
   - `batter_id` (UUID, FK)
   - `bowler_id` (UUID, FK)
   - `runs_scored` (INT)
   - `extras` (INT)
   - `wicket_type` (VARCHAR, Nullable)
   - `event_meta` (JSONB)

### Bulk Loading Strategy
To load large player files efficiently (5,000+ records), we bypass standard ORM overhead:
1. **Schema Validation**: Parse raw JSON/CSV inputs into a list of Pydantic models.
2. **Normalization Engine**: Feed data to a pandas pipeline that calculates relative percentiles and costs.
3. **COPY Protocol**: Use SQLAlchemy to retrieve the raw `asyncpg` DBAPI connection and call `copy_records_to_table()` to stream records directly into PostgreSQL in a single round-trip.

---

## 4. Don't Hand-Roll

- **Bulk Insertion**: Do not loop over model creation or execute multiple `session.add()` statements. Use asyncpg's `copy_records_to_table()` method.
- **Percentile Calculation**: Avoid manually iterating over lists to calculate rank percentiles. Use pandas' built-in vector group-by operations: `.groupby('season_id')['rating'].transform('rank', pct=True)`.
- **Alembic Async Migrations**: Do not write custom event loop runners for Alembic. Use the default async template: `alembic init -t async <directory_name>`, which uses greenlet/asyncio mappings built into SQLAlchemy.

---

## 5. Common Pitfalls

- **SQLAlchemy Async N+1 Traps**: Accessing relations (e.g. `player_season.player`) in async environments without explicit eager loading (`selectinload` or `joinedload`) throws a `MissingGreenlet` error. Always join tables explicitly or declare relationships with async-compatible loading strategies.
- **Percentile Skewing on Low Samples**: A player who faces 2 balls and hits one for six has an astronomical strike rate. If ranked without filtering, they skew the percentile ranks of top-tier batsmen. Filtering out players with `< 30` balls faced/bowled is critical before ranking.
- **Database Schema Locks**: Standard migration commands on live databases (like adding foreign keys or indexes) can lock tables and block FastAPI traffic. Ensure migrations are backward-compatible, define indexes concurrently where applicable, and run operations within targeted transactions.

---

## 6. Code Examples

### 6.1 Async SQLAlchemy DB Initialization

```python
# app/core/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft"

# Async engine with connection pool configurations
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 6.2 pandas Normalization Pipeline

```python
# app/ingestion/normalizer.py
import pandas as pd
import numpy as np

def normalize_ratings_pipeline(df: pd.DataFrame, min_threshold: int = 30) -> pd.DataFrame:
    """
    Normalizes statistical performance into relative season percentiles.
    Enforces minimum sample sizes, falling back to a baseline rating of 50.
    """
    df = df.copy()
    
    # Identify active subsets based on threshold
    bat_mask = df["balls_faced"] >= min_threshold
    bowl_mask = df["balls_bowled"] >= min_threshold
    
    # 1. Batting Percentiles (0-99 Scale)
    df.loc[bat_mask, "percentile_batting"] = (
        df[bat_mask]
        .groupby("season_id")["raw_batting_rating"]
        .transform("rank", pct=True)
        .mul(99)
        .round()
        .astype(int)
    )
    # Low-sample fallback
    df.loc[~bat_mask, "percentile_batting"] = 50
    
    # 2. Bowling Percentiles (0-99 Scale)
    df.loc[bowl_mask, "percentile_bowling"] = (
        df[bowl_mask]
        .groupby("season_id")["raw_bowling_rating"]
        .transform("rank", pct=True)
        .mul(99)
        .round()
        .astype(int)
    )
    # Low-sample fallback
    df.loc[~bowl_mask, "percentile_bowling"] = 50
    
    # 3. Credit Cost Calculation
    # Cost uses an exponential curve based on the max of player's percentiles
    max_rating = np.maximum(df["percentile_batting"], df["percentile_bowling"])
    base_cost = 4.0
    # Scaling factor maps rating 99 to ~15.0 credits, and rating 50 to ~6.0 credits
    df["credit_cost"] = base_cost + (max_rating / 99.0) ** 1.8 * 11.0
    df["credit_cost"] = df["credit_cost"].round(1)
    
    return df
```

### 6.3 Bulk COPY Loader Script

```python
# app/ingestion/loader.py
import asyncio
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.database import engine

async def bulk_copy_records(
    db_engine: AsyncEngine, 
    table_name: str, 
    columns: List[str], 
    records: List[Tuple]
) -> None:
    """
    Executes a high-performance COPY operation using raw asyncpg.
    """
    async with db_engine.connect() as conn:
        # Obtain raw asyncpg connection
        raw_conn = await conn.get_raw_connection()
        asyncpg_conn = raw_conn.driver_connection
        
        # Execute copy inside a transaction block
        async with conn.begin():
            await asyncpg_conn.copy_records_to_table(
                table_name,
                records=records,
                columns=columns
            )
```

---

## 7. Sources
1. **SQLAlchemy 2.0 Async documentation**: [https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
2. **asyncpg bulk data loading guide**: [https://magicstack.github.io/asyncpg/current/api/index.html#copy-data](https://magicstack.github.io/asyncpg/current/api/index.html#copy-data)
3. **pandas 3.0 Release Notes**: [https://pandas.pydata.org/docs/whatsnew/v3.0.0.html](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
4. **PostgreSQL 18 Performance Features**: PostgreSQL 18 Release Notes and memory tuning checklists.

---

## 8. Metadata
- **Author**: Research Subagent
- **Phase**: 01-data-model-ingestion-engine
- **Status**: Complete
- **Date**: 2026-06-11
- **Targets**: `DATA-01`, `DATA-02`, `DATA-03`
- **Stack Version Mapping**:
  - PostgreSQL: 18.x
  - SQLAlchemy: 2.0.50
  - asyncpg: 0.31.0
  - Alembic: 1.18.4
  - pandas: 3.0.0
  - python: 3.14.6
