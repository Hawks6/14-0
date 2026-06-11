import logging
import random
import pulp
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.squad import FranchiseSeason
from app.models.player import PlayerSeason

logger = logging.getLogger(__name__)

def generate_optimal_squad(candidate_players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Selects exactly 11 players from candidate_players that maximize team strength
    (e.g., sum of percentiles) while satisfying roster constraints.
    Returns the list of 11 selected player dicts, or an empty list if infeasible.
    """
    if len(candidate_players) < 11:
        return []
        
    prob = pulp.LpProblem("AISquadSelection", pulp.LpMaximize)
    
    x = {
        i: pulp.LpVariable(f"x_{i}", cat=pulp.LpBinary)
        for i in range(len(candidate_players))
    }
    
    # Objective: maximize sum of percentiles (batting + bowling) as a proxy for strength
    prob += pulp.lpSum(
        (candidate_players[i].get("percentile_batting", 50) + candidate_players[i].get("percentile_bowling", 50)) * x[i]
        for i in range(len(candidate_players))
    )
    
    # 1. Total slots = 11
    prob += pulp.lpSum(x[i] for i in range(len(candidate_players))) == 11
    
    # 2. Total credit cost relaxed for AI squads (since historical squads are sometimes very strong)
    prob += pulp.lpSum(
        candidate_players[i].get("credit_cost", 0.0) * x[i]
        for i in range(len(candidate_players))
    ) <= 120.0
    
    # 3. Exactly 1 Wicketkeeper (WK)
    prob += pulp.lpSum(
        1 * x[i] for i in range(len(candidate_players))
        if candidate_players[i].get("role") == "WK"
    ) == 1
    
    # 4. At least 3 Bowlers
    prob += pulp.lpSum(
        1 * x[i] for i in range(len(candidate_players))
        if candidate_players[i].get("role") == "BOWL"
    ) >= 3
    
    # 5. At most 4 Overseas players
    prob += pulp.lpSum(
        1 * x[i] for i in range(len(candidate_players))
        if candidate_players[i].get("is_overseas")
    ) <= 4
    
    # 6. Unique physical players (max 1 season selected for any player_id)
    player_groups: dict[str, list[int]] = {}
    for idx, candidate in enumerate(candidate_players):
        p_id = str(candidate["player_id"])
        player_groups.setdefault(p_id, []).append(idx)
        
    for p_id, indices in player_groups.items():
        prob += pulp.lpSum(x[i] for i in indices) <= 1

    try:
        status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
        if status != pulp.LpStatusOptimal:
            return []
            
        selected_players = []
        for i in range(len(candidate_players)):
            if pulp.value(x[i]) == 1.0:
                selected_players.append(candidate_players[i])
                
        return selected_players
    except Exception as e:
        logger.error(f"Error occurred during PuLP solver execution: {e}")
        return []

async def generate_tournament_schedule(db: AsyncSession, num_matches: int = 14) -> List[Dict[str, Any]]:
    """
    Generates a tournament schedule containing AI opponent squads.
    Queries the database for historical franchise seasons and generates optimal valid squads.
    """
    # Fetch all FranchiseSeasons
    query = select(FranchiseSeason).options(
        selectinload(FranchiseSeason.franchise),
        selectinload(FranchiseSeason.season)
    )
    result = await db.execute(query)
    all_franchise_seasons = result.scalars().all()
    
    valid_squads_pool = []
    
    for fs in all_franchise_seasons:
        # Get all players for this franchise season
        players_query = select(PlayerSeason).options(
            selectinload(PlayerSeason.player)
        ).where(
            PlayerSeason.franchise_id == fs.franchise_id,
            PlayerSeason.season_id == fs.season_id
        )
        players_result = await db.execute(players_query)
        player_seasons = players_result.scalars().all()
        
        # Convert to candidate dicts
        candidate_players = []
        for ps in player_seasons:
            candidate_players.append({
                "player_id": str(ps.player_id),
                "player_season_id": str(ps.id),
                "name": ps.player.name,
                "role": ps.player.role,
                "is_overseas": ps.player.is_overseas,
                "credit_cost": ps.credit_cost,
                "percentile_batting": ps.percentile_batting,
                "percentile_bowling": ps.percentile_bowling
            })
            
        squad = generate_optimal_squad(candidate_players)
        if squad and len(squad) == 11:
            valid_squads_pool.append({
                "franchise_season_id": str(fs.id),
                "franchise_name": fs.franchise.name,
                "season_year": fs.season.year,
                "squad": squad
            })
            
    if not valid_squads_pool:
        logger.warning("No valid AI squads could be generated from the database.")
        return []
        
    schedule = []
    # Pick requested number of matches. If not enough unique squads, pick with replacement.
    if len(valid_squads_pool) >= num_matches:
        selected_pool = random.sample(valid_squads_pool, num_matches)
    else:
        selected_pool = random.choices(valid_squads_pool, k=num_matches)
        
    for i, match_data in enumerate(selected_pool):
        schedule.append({
            "match_number": i + 1,
            **match_data
        })
        
    return schedule
