import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft')
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT AVG(credit_cost), MIN(credit_cost), MAX(credit_cost) FROM player_seasons;"))
        row = res.fetchone()
        print(f'Average cost: {row[0]:.2f}')
        print(f'Min cost: {row[1]}')
        print(f'Max cost: {row[2]}')

asyncio.run(main())
