import asyncio
import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.core.database import SessionLocal, engine
from app.models.draft import DraftSession, DraftPick
from app.models.player import PlayerSeason
from app.api.league import start_league, get_league, get_match_results

async def create_synthetic_draft_session(session):
    # 1. Create a draft session
    ds = DraftSession(id=uuid.uuid4(), status="COMPLETED")
    session.add(ds)
    await session.flush()
    
    # 2. Find 11 players to draft (1 WK, 3 BOWL, 7 BAT/ALLROUNDER, max 4 overseas)
    # For simplicity, we just fetch 11 players. The `start_league` doesn't re-validate the draft logic natively 
    # except checking if count is 11, but let's grab exactly 11 PlayerSeason records.
    stmt = select(PlayerSeason).limit(11)
    res = await session.execute(stmt)
    players = res.scalars().all()
    
    if len(players) < 11:
        print("Not enough players in DB!")
        return None
        
    for i, p in enumerate(players):
        pick = DraftPick(
            id=uuid.uuid4(),
            draft_session_id=ds.id,
            pick_number=i+1,
            player_season_id=p.id,
            player_id=p.player_id
        )
        session.add(pick)
    
    await session.commit()
    return ds.id

async def test_league_flow():
    async with SessionLocal() as db:
        ds_id = await create_synthetic_draft_session(db)
        if not ds_id:
            return
            
        print(f"Created synthetic draft session: {ds_id}")
        
        # Start League
        print("Starting 14-match tournament simulation...")
        league_res = await start_league(ds_id, db)
        print(f"Tournament simulated! Found {len(league_res.matches)} matches.")
        
        # Fetch league
        fetched_league = await get_league(ds_id, db)
        print(f"Fetched {len(fetched_league.matches)} matches via API.")
        
        # Check first match scorecard
        first_match_id = fetched_league.matches[0].id
        print(f"Fetching scorecard for match: {first_match_id}")
        match_events = await get_match_results(first_match_id, db)
        print(f"Match status: {match_events.status}")
        print(f"Match winner: {match_events.winner}")
        print(f"{match_events.user_team}: {match_events.user_score}/{match_events.user_wickets} ({match_events.user_overs} overs)")
        print(f"{match_events.opponent_team}: {match_events.opponent_score}/{match_events.opponent_wickets} ({match_events.opponent_overs} overs)")
        print(f"Total events recorded: {len(match_events.events)}")

async def main():
    try:
        await test_league_flow()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
