import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/ipl_draft')
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT p.name, ps.credit_cost FROM player_seasons ps JOIN players p ON ps.player_id = p.id WHERE p.role != 'WK' ORDER BY ps.credit_cost ASC LIMIT 8;"))
        rows = res.fetchall()
        print('8 cheapest non-WK players:')
        total = 0
        for r in rows:
            print(f'{r[0]}: {r[1]}')
            total += r[1]
        print(f'Total cost of 8 cheapest: {total}')

asyncio.run(main())
