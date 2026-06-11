import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft')
    async with engine.begin() as conn:
        # Fix user_team to have a proper server default
        print("Fixing DB column defaults...")
        await conn.execute(text("ALTER TABLE matches ALTER COLUMN user_team SET DEFAULT 'Your XI'"))
        await conn.execute(text("ALTER TABLE matches ALTER COLUMN user_overs SET DEFAULT 0.0"))
        await conn.execute(text("ALTER TABLE matches ALTER COLUMN opponent_overs SET DEFAULT 0.0"))
        print("Done! DB server defaults set.")

asyncio.run(main())
