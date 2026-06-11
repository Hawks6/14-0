import asyncio
import uuid
import traceback
from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.api.league import start_league
from app.models.draft import DraftSession, DraftPick
from app.models.player import PlayerSeason, Player, Season
from app.models.squad import FranchiseSeason
from app.models.match import Match, MatchEvent

async def main():
    async with SessionLocal() as db_session:
        res = await db_session.execute(text("SELECT id, status FROM draft_sessions ORDER BY id DESC LIMIT 5"))
        rows = res.fetchall()
        for r in rows:
            print('Session:', r[0], 'status:', r[1])
            
        session_id = uuid.UUID('c9b85f15-4f54-4b25-86eb-1e2471026cb4')
        print('Testing start_league for session:', session_id)
        try:
            res = await start_league(session_id, db_session)
            print('Success!', res)
        except Exception as e:
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
