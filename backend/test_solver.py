import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import SessionLocal, engine
from app.models.draft import DraftPick, DraftSession
from app.models.match import Match, MatchEvent
from app.simulation.ai_squads import generate_tournament_schedule

async def test():
    async with SessionLocal() as db:
        schedule = await generate_tournament_schedule(db, num_matches=14)
        print(f"Generated {len(schedule)} valid squads")

if __name__ == "__main__":
    asyncio.run(test())
