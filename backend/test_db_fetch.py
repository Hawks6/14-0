import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, func
from app.core.database import SessionLocal, engine
from app.models.player import Season, Franchise, Player, PlayerSeason
from app.models.squad import FranchiseSeason
from app.models.draft import DraftPick, DraftSession
from app.models.match import Match, MatchEvent

async def check_db():
    async with SessionLocal() as session:
        seasons_count = await session.scalar(select(func.count(Season.id)))
        franchises_count = await session.scalar(select(func.count(Franchise.id)))
        players_count = await session.scalar(select(func.count(Player.id)))
        player_seasons_count = await session.scalar(select(func.count(PlayerSeason.id)))
        franchise_seasons_count = await session.scalar(select(func.count(FranchiseSeason.id)))
        
        print("--- Database Counts ---")
        print(f"Seasons: {seasons_count}")
        print(f"Franchises: {franchises_count}")
        print(f"Players: {players_count}")
        print(f"Franchise Seasons: {franchise_seasons_count}")
        print(f"Player Seasons: {player_seasons_count}")
        
        print("\n--- Sample Data ---")
        # Fetch one player season with relations
        stmt = select(PlayerSeason).limit(1)
        result = await session.execute(stmt)
        ps = result.scalar_one_or_none()
        
        if ps:
            # Need to eager load or just fetch relations manually since we are async
            pass
            
        # Let's just fetch directly with joins to prove relationships work
        stmt2 = (
            select(Player.name, Season.year, Franchise.name, PlayerSeason.credit_cost)
            .join(PlayerSeason.player)
            .join(PlayerSeason.season)
            .join(PlayerSeason.franchise)
            .limit(3)
        )
        result2 = await session.execute(stmt2)
        print("Sample Player Seasons:")
        for row in result2:
            print(f" - {row[0]} | {row[1]} | {row[2]} | {row[3]} credits")

async def main():
    try:
        await check_db()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
