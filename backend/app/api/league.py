import uuid
import logging
import random
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.models.draft import DraftSession, DraftPick
from app.models.match import Match, MatchEvent
from app.models.player import Player, PlayerSeason
from app.simulation.ai_squads import generate_tournament_schedule
from app.simulation.league import Team, LeagueOrchestrator

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
    user_team: Optional[str] = None
    opponent_team: Optional[str] = None
    user_overs: Optional[float] = None
    opponent_overs: Optional[float] = None

class MatchWithEvents(MatchDetail):
    events: List[MatchEventDetail]

class LeagueResponse(BaseModel):
    draft_session_id: uuid.UUID
    matches: List[MatchDetail]

@router.post("/start/{draft_session_id}", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
async def start_league(draft_session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Starts a 14-match league for a completed draft session.
    Generates and simulates 14 matches against AI opponent squads.
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

    # 3. Retrieve user drafted players
    picks_stmt = select(DraftPick).where(DraftPick.draft_session_id == draft_session_id).order_by(DraftPick.pick_number)
    picks_res = await db.execute(picks_stmt)
    db_picks = picks_res.scalars().all()
    
    if not db_picks or len(db_picks) < 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roster is incomplete (only {len(db_picks)}/11 players drafted)"
        )
        
    user_players = []
    for pick in db_picks:
        ps_stmt = select(PlayerSeason).where(PlayerSeason.id == pick.player_season_id).options(joinedload(PlayerSeason.player))
        ps_res = await db.execute(ps_stmt)
        ps = ps_res.scalar_one()
        user_players.append({
            "player_id": str(ps.player_id),
            "name": ps.player.name,
            "role": ps.player.role,
            "is_overseas": ps.player.is_overseas,
            "percentile_batting": ps.percentile_batting,
            "percentile_bowling": ps.percentile_bowling,
            "credit_cost": ps.credit_cost
        })

    # 4. Generate 14-match AI opponent schedule
    schedule_data = await generate_tournament_schedule(db, num_matches=14)
    if not schedule_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI opponent squads. Check if database is seeded."
        )

    # 5. Simulate matches and create db records
    new_matches = []
    for match_data in schedule_data:
        match_num = match_data["match_number"]
        opp_name = f"{match_data['franchise_name']} ({match_data['season_year']})"
        opp_squad = match_data["squad"]
        
        # Convert rosters to Team objects
        user_team = Team(
            id="user",
            name="Your XI",
            batting_lineup=[{**p, "id": p["player_id"]} for p in user_players],
            bowling_lineup=[{**p, "id": p["player_id"]} for p in user_players]
        )
        
        opponent_team = Team(
            id="opponent",
            name=opp_name,
            batting_lineup=[{**p, "id": p["player_id"]} for p in opp_squad],
            bowling_lineup=[{**p, "id": p["player_id"]} for p in opp_squad]
        )
        
        # Build striker/bowler name to player_id lookup mapping
        name_to_id = {}
        for p in user_players:
            name_to_id[p["name"]] = uuid.UUID(p["player_id"])
        for p in opp_squad:
            name_to_id[p["name"]] = uuid.UUID(p["player_id"])
            
        # Instantiate orchestrator with randomized seed for variance
        match_seed = random.randint(1, 100000)
        orchestrator = LeagueOrchestrator(teams=[user_team, opponent_team], seed=match_seed)
        
        # Odd match number: user bats first. Even: opponent bats first.
        if match_num % 2 == 1:
            sim_res = orchestrator.simulate_match("user", "opponent")
        else:
            sim_res = orchestrator.simulate_match("opponent", "user")
            
        # Determine winner string
        if sim_res.is_tie:
            winner_str = "tie"
        elif sim_res.winner_id == "user":
            winner_str = "user"
        else:
            winner_str = "opponent"
            
        # Extract user/opponent scores, wickets, overs based on who batted first
        if match_num % 2 == 1:
            user_score = sim_res.team1_innings.total_runs
            user_wickets = sim_res.team1_innings.wickets
            user_overs = round(sim_res.team1_innings.overs_bowled, 1)
            
            opponent_score = sim_res.team2_innings.total_runs
            opponent_wickets = sim_res.team2_innings.wickets
            opponent_overs = round(sim_res.team2_innings.overs_bowled, 1)
        else:
            opponent_score = sim_res.team1_innings.total_runs
            opponent_wickets = sim_res.team1_innings.wickets
            opponent_overs = round(sim_res.team1_innings.overs_bowled, 1)
            
            user_score = sim_res.team2_innings.total_runs
            user_wickets = sim_res.team2_innings.wickets
            user_overs = round(sim_res.team2_innings.overs_bowled, 1)
            
        m_id = uuid.UUID(sim_res.match_id)
        
        m = Match(
            id=m_id,
            draft_session_id=draft_session_id,
            match_number=match_num,
            status="completed",
            user_score=user_score,
            user_wickets=user_wickets,
            user_overs=user_overs,
            opponent_score=opponent_score,
            opponent_wickets=opponent_wickets,
            opponent_overs=opponent_overs,
            opponent_team=opp_name,
            user_team="Your XI",
            winner=winner_str
        )
        db.add(m)
        new_matches.append(m)
        
        # Save delivery events for Innings 1
        for ball_log in sim_res.team1_innings.delivery_log:
            if "outcome" not in ball_log:
                continue
            outcome_str = ball_log["outcome"]
            runs_scored = 0
            extras = 0
            if outcome_str in ("WIDE", "NO_BALL"):
                extras = 1
            elif outcome_str in ("ONE", "TWO", "THREE", "FOUR", "SIX"):
                mapping = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "SIX": 6}
                runs_scored = mapping[outcome_str]
            
            wicket_type = "OUT" if outcome_str == "WICKET" else None
            
            b_id = name_to_id.get(ball_log["striker"])
            bw_id = name_to_id.get(ball_log["bowler"])
            if b_id is None or bw_id is None:
                b_id = b_id or list(name_to_id.values())[0]
                bw_id = bw_id or list(name_to_id.values())[1]
                
            evt = MatchEvent(
                id=uuid.uuid4(),
                match_id=m_id,
                ball_number=ball_log["ball"],
                over_number=ball_log["over"],
                batter_id=b_id,
                bowler_id=bw_id,
                runs_scored=runs_scored,
                extras=extras,
                wicket_type=wicket_type,
                event_meta=ball_log
            )
            db.add(evt)
            
        # Save delivery events for Innings 2
        for ball_log in sim_res.team2_innings.delivery_log:
            if "outcome" not in ball_log:
                continue
            outcome_str = ball_log["outcome"]
            runs_scored = 0
            extras = 0
            if outcome_str in ("WIDE", "NO_BALL"):
                extras = 1
            elif outcome_str in ("ONE", "TWO", "THREE", "FOUR", "SIX"):
                mapping = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "SIX": 6}
                runs_scored = mapping[outcome_str]
            
            wicket_type = "OUT" if outcome_str == "WICKET" else None
            
            b_id = name_to_id.get(ball_log["striker"])
            bw_id = name_to_id.get(ball_log["bowler"])
            if b_id is None or bw_id is None:
                b_id = b_id or list(name_to_id.values())[0]
                bw_id = bw_id or list(name_to_id.values())[1]
                
            evt = MatchEvent(
                id=uuid.uuid4(),
                match_id=m_id,
                ball_number=ball_log["ball"],
                over_number=ball_log["over"],
                batter_id=b_id,
                bowler_id=bw_id,
                runs_scored=runs_scored,
                extras=extras,
                wicket_type=wicket_type,
                event_meta=ball_log
            )
            db.add(evt)

    await db.commit()

    match_details = [
        MatchDetail(
            id=m.id,
            draft_session_id=m.draft_session_id,
            match_number=m.match_number,
            status=m.status,
            user_score=m.user_score,
            user_wickets=m.user_wickets,
            user_overs=m.user_overs,
            opponent_score=m.opponent_score,
            opponent_wickets=m.opponent_wickets,
            opponent_overs=m.opponent_overs,
            opponent_team=m.opponent_team,
            user_team=m.user_team,
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
            user_overs=m.user_overs,
            opponent_score=m.opponent_score,
            opponent_wickets=m.opponent_wickets,
            opponent_overs=m.opponent_overs,
            opponent_team=m.opponent_team,
            user_team=m.user_team,
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
        user_overs=match_obj.user_overs,
        opponent_score=match_obj.opponent_score,
        opponent_wickets=match_obj.opponent_wickets,
        opponent_overs=match_obj.opponent_overs,
        opponent_team=match_obj.opponent_team,
        user_team=match_obj.user_team,
        winner=match_obj.winner,
        events=events
    )
