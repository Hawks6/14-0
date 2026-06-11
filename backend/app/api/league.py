import uuid
import logging
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.models.draft import DraftSession
from app.models.match import Match, MatchEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/league", tags=["league"])

# Pydantic Schemas
class MatchEventDetail(BaseModel):
    id: uuid.UUID
    ball_number: int
    over_number: int
    batter_id: uuid.UUID
    bowler_id: uuid.UUID
    runs_scored: int
    extras: int
    wicket_type: Optional[str] = None
    event_meta: dict[str, Any]

class MatchDetail(BaseModel):
    id: uuid.UUID
    draft_session_id: uuid.UUID
    match_number: int
    status: str
    user_score: int
    user_wickets: int
    opponent_score: int
    opponent_wickets: int
    winner: Optional[str] = None

class MatchWithEvents(MatchDetail):
    events: List[MatchEventDetail]

class LeagueResponse(BaseModel):
    draft_session_id: uuid.UUID
    matches: List[MatchDetail]

@router.post("/start/{draft_session_id}", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
async def start_league(draft_session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Starts a 14-match league for a completed draft session.
    Generates 14 SCHEDULED matches.
    """
    # 1. Fetch DraftSession
    draft_stmt = select(DraftSession).where(DraftSession.id == draft_session_id)
    draft_res = await db.execute(draft_stmt)
    draft_session = draft_res.scalar_one_or_none()

    if not draft_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft session not found")
    
    if draft_session.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft session is not COMPLETED. Cannot start league."
        )

    # 2. Check if matches already exist
    matches_stmt = select(Match).where(Match.draft_session_id == draft_session_id)
    matches_res = await db.execute(matches_stmt)
    existing_matches = matches_res.scalars().all()

    if existing_matches:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League already started for this draft session."
        )

    # 3. Create 14 Matches
    new_matches = []
    for i in range(1, 15):
        m = Match(
            id=uuid.uuid4(),
            draft_session_id=draft_session_id,
            match_number=i,
            status="SCHEDULED",
            user_score=0,
            user_wickets=0,
            opponent_score=0,
            opponent_wickets=0,
            winner=None
        )
        db.add(m)
        new_matches.append(m)

    await db.flush()

    match_details = [
        MatchDetail(
            id=m.id,
            draft_session_id=m.draft_session_id,
            match_number=m.match_number,
            status=m.status,
            user_score=m.user_score,
            user_wickets=m.user_wickets,
            opponent_score=m.opponent_score,
            opponent_wickets=m.opponent_wickets,
            winner=m.winner
        )
        for m in new_matches
    ]

    return LeagueResponse(
        draft_session_id=draft_session_id,
        matches=match_details
    )

@router.get("/{draft_session_id}", response_model=LeagueResponse)
async def get_league(draft_session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieves the matches for a given draft session.
    """
    matches_stmt = select(Match).where(Match.draft_session_id == draft_session_id).order_by(Match.match_number)
    matches_res = await db.execute(matches_stmt)
    matches = matches_res.scalars().all()

    if not matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found for this draft session")

    match_details = [
        MatchDetail(
            id=m.id,
            draft_session_id=m.draft_session_id,
            match_number=m.match_number,
            status=m.status,
            user_score=m.user_score,
            user_wickets=m.user_wickets,
            opponent_score=m.opponent_score,
            opponent_wickets=m.opponent_wickets,
            winner=m.winner
        )
        for m in matches
    ]

    return LeagueResponse(
        draft_session_id=draft_session_id,
        matches=match_details
    )

@router.get("/match/{match_id}", response_model=MatchWithEvents)
async def get_match_results(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieves match details and its event logs for playback.
    """
    match_stmt = select(Match).where(Match.id == match_id).options(joinedload(Match.events))
    match_res = await db.execute(match_stmt)
    match_obj = match_res.unique().scalar_one_or_none()

    if not match_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    events = [
        MatchEventDetail(
            id=e.id,
            ball_number=e.ball_number,
            over_number=e.over_number,
            batter_id=e.batter_id,
            bowler_id=e.bowler_id,
            runs_scored=e.runs_scored,
            extras=e.extras,
            wicket_type=e.wicket_type,
            event_meta=e.event_meta
        )
        for e in sorted(match_obj.events, key=lambda x: (x.over_number, x.ball_number))
    ]

    return MatchWithEvents(
        id=match_obj.id,
        draft_session_id=match_obj.draft_session_id,
        match_number=match_obj.match_number,
        status=match_obj.status,
        user_score=match_obj.user_score,
        user_wickets=match_obj.user_wickets,
        opponent_score=match_obj.opponent_score,
        opponent_wickets=match_obj.opponent_wickets,
        winner=match_obj.winner,
        events=events
    )
