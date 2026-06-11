import uuid
import logging
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.redis import get_draft_session, save_draft_session
from app.models.draft import DraftSession, DraftPick
from app.models.player import Season, Franchise, Player, PlayerSeason
from app.models.squad import FranchiseSeason
from app.simulation.draft_solver import check_draft_solvability

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/draft", tags=["draft"])

# Pydantic Schemas
class DraftSessionCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None

class DraftPickRequest(BaseModel):
    player_season_id: uuid.UUID

class PlayerDetail(BaseModel):
    player_season_id: uuid.UUID
    player_id: uuid.UUID
    name: str
    country: str
    role: str
    is_overseas: bool
    credit_cost: float
    percentile_batting: int
    percentile_bowling: int

class SpinResponse(BaseModel):
    franchise_name: str
    franchise_code: str
    year: int
    players: list[PlayerDetail]

class DraftPickDetail(BaseModel):
    pick_number: int
    player_id: uuid.UUID
    player_season_id: uuid.UUID
    name: str
    role: str
    is_overseas: bool
    credit_cost: float

class DraftSessionResponse(BaseModel):
    id: uuid.UUID
    status: str
    budget_remaining: float
    picks: list[DraftPickDetail]
    current_spin: Optional[dict[str, Any]] = None


# Helper to construct draft state
def build_session_response(session_state: dict[str, Any]) -> DraftSessionResponse:
    # Build list of pick details
    picks_detail = []
    for p in session_state.get("picks", []):
        picks_detail.append(
            DraftPickDetail(
                pick_number=p["pick_number"],
                player_id=uuid.UUID(p["player_id"]),
                player_season_id=uuid.UUID(p["player_season_id"]),
                name=p["name"],
                role=p["role"],
                is_overseas=p["is_overseas"],
                credit_cost=p["credit_cost"]
            )
        )
    
    current_spin = None
    if session_state.get("current_spin_players"):
        current_spin = {
            "franchise_id": session_state.get("current_spin_franchise_id"),
            "season_id": session_state.get("current_spin_season_id"),
            "players_count": len(session_state["current_spin_players"])
        }

    return DraftSessionResponse(
        id=uuid.UUID(session_state["id"]),
        status=session_state["status"],
        budget_remaining=session_state["budget_remaining"],
        picks=picks_detail,
        current_spin=current_spin
    )


@router.post("/session", response_model=DraftSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(body: DraftSessionCreate, db: AsyncSession = Depends(get_db)):
    """
    Initializes a new draft session in both PostgreSQL and Redis.
    """
    session_id = uuid.uuid4()
    
    # Create PostgreSQL record
    db_session = DraftSession(
        id=session_id,
        user_id=body.user_id,
        status="IN_PROGRESS",
        budget_remaining=100.0
    )
    db.add(db_session)
    await db.flush() # Flush to assign database state, commit is handled by get_db middleware or at the end

    # Initialize Redis State
    session_state = {
        "id": str(session_id),
        "status": "IN_PROGRESS",
        "budget_remaining": 100.0,
        "picks": [],
        "current_spin_franchise_id": None,
        "current_spin_season_id": None,
        "current_spin_players": None,
        "spun_franchise_season_ids": []
    }
    
    await save_draft_session(str(session_id), session_state)
    return build_session_response(session_state)


@router.post("/session/{session_id}/spin", response_model=SpinResponse)
async def trigger_spin(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Triggers a spin to serve a random historical franchise season pool of players.
    """
    session_state = await get_draft_session(str(session_id))
    if not session_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft session not found")
        
    if session_state["status"] != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Draft session is not in progress (current status: {session_state['status']})"
        )

    # 1. Select a random franchise season that hasn't been spun yet
    spun_ids = set(session_state.get("spun_franchise_season_ids", []))
    
    # Query all franchise seasons
    stmt = select(FranchiseSeason).join(Franchise).join(Season)
    result = await db.execute(stmt)
    franchise_seasons = result.scalars().all()
    
    if not franchise_seasons:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No FranchiseSeasons found in the database. Ensure ingestion loader has run."
        )

    available = [fs for fs in franchise_seasons if str(fs.id) not in spun_ids]
    
    # If all franchise seasons are spun, reset the history to allow repeats
    if not available:
        logger.info("All franchise seasons have been spun. Resetting spin history.")
        available = franchise_seasons
        spun_ids = set()

    # Get a random available franchise season
    import random
    chosen_fs = random.choice(available)

    # Fetch details
    franchise_stmt = select(Franchise).where(Franchise.id == chosen_fs.franchise_id)
    franchise_res = await db.execute(franchise_stmt)
    franchise = franchise_res.scalar_one()

    season_stmt = select(Season).where(Season.id == chosen_fs.season_id)
    season_res = await db.execute(season_stmt)
    season = season_res.scalar_one()

    # 2. Fetch all players for this franchise season
    players_stmt = (
        select(PlayerSeason)
        .where(
            PlayerSeason.franchise_id == chosen_fs.franchise_id,
            PlayerSeason.season_id == chosen_fs.season_id
        )
        .join(Player)
    )
    players_result = await db.execute(players_stmt)
    player_seasons = players_result.scalars().all()

    # Format players list
    players_list = []
    for ps in player_seasons:
        players_list.append(
            {
                "player_season_id": str(ps.id),
                "player_id": str(ps.player_id),
                "name": ps.player.name,
                "country": ps.player.country,
                "role": ps.player.role,
                "is_overseas": ps.player.is_overseas,
                "credit_cost": ps.credit_cost,
                "percentile_batting": ps.percentile_batting,
                "percentile_bowling": ps.percentile_bowling
            }
        )

    # 3. Update Redis state
    session_state["current_spin_franchise_id"] = str(chosen_fs.franchise_id)
    session_state["current_spin_season_id"] = str(chosen_fs.season_id)
    session_state["current_spin_players"] = players_list
    session_state["spun_franchise_season_ids"].append(str(chosen_fs.id))
    
    await save_draft_session(str(session_id), session_state)

    # Build Response
    return SpinResponse(
        franchise_name=franchise.name,
        franchise_code=franchise.code,
        year=season.year,
        players=[PlayerDetail(**p) for p in players_list]
    )


@router.post("/session/{session_id}/pick", response_model=DraftSessionResponse)
async def draft_player(session_id: uuid.UUID, body: DraftPickRequest, db: AsyncSession = Depends(get_db)):
    """
    Selects one player from the currently spun pool, runs constraint and solvability validation,
    and updates the active draft state.
    """
    session_state = await get_draft_session(str(session_id))
    if not session_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft session not found")

    if session_state["status"] != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Draft session is not in progress (current status: {session_state['status']})"
        )

    # 1. Validate that spin has occurred
    spin_players = session_state.get("current_spin_players")
    if not spin_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active spin pool. You must spin before making a pick."
        )

    # 2. Find player in spin pool
    picked_player = None
    target_id_str = str(body.player_season_id)
    for p in spin_players:
        if p["player_season_id"] == target_id_str:
            picked_player = p
            break

    if not picked_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected player is not part of the current spin pool."
        )

    # 3. Check immediate constraints:
    current_picks = session_state["picks"]
    if len(current_picks) >= 11:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Roster is already full (11 players drafted)")

    # Salary budget check
    picked_cost = picked_player["credit_cost"]
    remaining_budget = session_state["budget_remaining"]
    if picked_cost > remaining_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player cost ({picked_cost} credits) exceeds remaining budget ({remaining_budget} credits)."
        )

    # Overseas players check
    current_overseas = sum(1 for p in current_picks if p["is_overseas"])
    if picked_player["is_overseas"] and current_overseas >= 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot draft more than 4 overseas players."
        )

    # Unique physical players check
    drafted_player_ids = {p["player_id"] for p in current_picks}
    if picked_player["player_id"] in drafted_player_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player '{picked_player['name']}' is already drafted in a different season."
        )

    # 4. PuLP Solvability Verification
    # Fetch all candidate player seasons to check future solvability
    candidates_stmt = select(PlayerSeason).join(Player)
    candidates_res = await db.execute(candidates_stmt)
    db_candidates = candidates_res.scalars().all()
    
    candidate_pool = [
        {
            "player_id": str(c.player_id),
            "role": c.player.role,
            "is_overseas": c.player.is_overseas,
            "credit_cost": c.credit_cost
        }
        for c in db_candidates
    ]

    # Prepare potential picks list including the new pick
    potential_picks = current_picks + [{
        "player_id": picked_player["player_id"],
        "role": picked_player["role"],
        "is_overseas": picked_player["is_overseas"],
        "credit_cost": picked_player["credit_cost"]
    }]
    
    remaining_budget_after_pick = remaining_budget - picked_cost
    remaining_slots = 11 - len(potential_picks)

    # Check feasibility
    solvable = check_draft_solvability(
        current_picks=potential_picks,
        remaining_budget=remaining_budget_after_pick,
        remaining_slots=remaining_slots,
        candidate_players=candidate_pool
    )

    if not solvable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Picking this player makes it mathematically impossible to satisfy roster constraints (WK, Bowlers, Overseas, Budget) with remaining slots."
        )

    # 5. Pick is valid! Commit updates
    pick_number = len(current_picks) + 1
    
    # Save to PostgreSQL
    db_pick = DraftPick(
        id=uuid.uuid4(),
        draft_session_id=session_id,
        player_id=uuid.UUID(picked_player["player_id"]),
        player_season_id=uuid.UUID(picked_player["player_season_id"]),
        pick_number=pick_number
    )
    db.add(db_pick)
    
    # Update Redis picks
    new_pick_entry = {
        "pick_number": pick_number,
        "player_id": picked_player["player_id"],
        "player_season_id": picked_player["player_season_id"],
        "name": picked_player["name"],
        "role": picked_player["role"],
        "is_overseas": picked_player["is_overseas"],
        "credit_cost": picked_player["credit_cost"]
    }
    session_state["picks"].append(new_pick_entry)
    session_state["budget_remaining"] = round(remaining_budget_after_pick, 1)
    
    # Clear active spin pool
    session_state["current_spin_franchise_id"] = None
    session_state["current_spin_season_id"] = None
    session_state["current_spin_players"] = None
    
    # Check if complete
    if len(session_state["picks"]) == 11:
        session_state["status"] = "COMPLETED"

    # Update PostgreSQL DraftSession status/budget
    db_session_stmt = select(DraftSession).where(DraftSession.id == session_id)
    db_session_res = await db.execute(db_session_stmt)
    db_session = db_session_res.scalar_one()
    db_session.status = session_state["status"]
    db_session.budget_remaining = session_state["budget_remaining"]

    await save_draft_session(str(session_id), session_state)
    
    return build_session_response(session_state)


@router.get("/session/{session_id}", response_model=DraftSessionResponse)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieves the current draft session state. Falls back to DB if Redis cache misses.
    """
    session_state = await get_draft_session(str(session_id))
    
    if not session_state:
        # Fallback to Database
        logger.info(f"Redis cache miss for draft session {session_id}. Loading from PostgreSQL.")
        db_session_stmt = (
            select(DraftSession)
            .where(DraftSession.id == session_id)
        )
        db_session_res = await db.execute(db_session_stmt)
        db_session = db_session_res.scalar_one_or_none()
        
        if not db_session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft session not found")
            
        # Reconstruct picks list
        picks_stmt = (
            select(DraftPick)
            .where(DraftPick.draft_session_id == session_id)
            .order_by(DraftPick.pick_number)
        )
        picks_res = await db.execute(picks_stmt)
        db_picks = picks_res.scalars().all()
        
        picks_list = []
        for pick in db_picks:
            # Query player details
            player_season_stmt = (
                select(PlayerSeason)
                .where(PlayerSeason.id == pick.player_season_id)
                .join(Player)
            )
            ps_res = await db.execute(player_season_stmt)
            ps = ps_res.scalar_one()
            
            picks_list.append({
                "pick_number": pick.pick_number,
                "player_id": str(pick.player_id),
                "player_season_id": str(pick.player_season_id),
                "name": ps.player.name,
                "role": ps.player.role,
                "is_overseas": ps.player.is_overseas,
                "credit_cost": ps.credit_cost
            })
            
        session_state = {
            "id": str(session_id),
            "status": db_session.status,
            "budget_remaining": db_session.budget_remaining,
            "picks": picks_list,
            "current_spin_franchise_id": None,
            "current_spin_season_id": None,
            "current_spin_players": None,
            "spun_franchise_season_ids": [] # Can't fully reconstruct without spin log, but okay for recovery
        }
        # Save back to Redis cache
        await save_draft_session(str(session_id), session_state)
        
    return build_session_response(session_state)
