import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft')
    async with engine.connect() as conn:
        # Check actual column definitions for matches table
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name='matches'
            ORDER BY ordinal_position
        """))
        rows = result.fetchall()
        print("=== matches table columns ===")
        for r in rows:
            print(f"{r[0]}: type={r[1]}, default={r[2]}, nullable={r[3]}")

asyncio.run(main())
