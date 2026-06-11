import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft')
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
        rows = result.fetchall()
        print("=== ALL TABLES ===")
        for r in rows:
            print(r[0])
        
        # Check franchise codes
        try:
            result2 = await conn.execute(text("SELECT DISTINCT code, name FROM franchises ORDER BY code"))
            print("\n=== FRANCHISE CODES ===")
            for r in result2.fetchall():
                print(f"{r[0]}: {r[1]}")
        except Exception as e:
            print(f"franchises table error: {e}")

asyncio.run(main())
