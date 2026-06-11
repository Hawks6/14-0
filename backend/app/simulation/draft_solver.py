import logging
import pulp
from typing import Any

logger = logging.getLogger(__name__)

def check_draft_solvability(
    current_picks: list[dict[str, Any]],
    remaining_budget: float,
    remaining_slots: int,
    candidate_players: list[dict[str, Any]]
) -> bool:
    """
    Checks if there exists a valid selection of players from candidate_players
    to complete the draft session satisfying all roster constraints:
    1. Exactly 11 players total (remaining_slots elements to choose).
    2. Total credit cost <= 100 (remaining budget limit).
    3. Exactly 1 Wicketkeeper (WK) overall.
    4. Minimum 3 specialist Bowlers (BOWL) overall.
    5. Maximum 4 overseas players overall.
    6. No duplicate physical players (each player_id must be unique in the final team).
    
    Returns True if a feasible solution exists, False otherwise.
    """
    # If no slots remain, the current roster must be valid.
    if remaining_slots <= 0:
        # Check if current roster satisfies all rules:
        wk_count = sum(1 for p in current_picks if p.get("role") == "WK")
        bowl_count = sum(1 for p in current_picks if p.get("role") == "BOWL")
        overseas_count = sum(1 for p in current_picks if p.get("is_overseas"))
        cost_sum = sum(p.get("credit_cost", 0.0) for p in current_picks)
        
        valid = (
            len(current_picks) == 11
            and wk_count == 1
            and bowl_count >= 3
            and overseas_count <= 4
            and cost_sum <= 100.0
        )
        return valid

    # Calculate current counts from already selected picks
    current_wk_count = sum(1 for p in current_picks if p.get("role") == "WK")
    current_bowl_count = sum(1 for p in current_picks if p.get("role") == "BOWL")
    current_overseas_count = sum(1 for p in current_picks if p.get("is_overseas"))
    
    # Pre-filter candidate_players:
    # 1. Exclude player_ids already drafted
    drafted_player_ids = {p["player_id"] for p in current_picks}
    eligible_candidates = [
        p for p in candidate_players if p["player_id"] not in drafted_player_ids
    ]
    
    # 2. Exclude candidates whose cost exceeds the remaining budget
    eligible_candidates = [
        p for p in eligible_candidates if p.get("credit_cost", 0.0) <= remaining_budget
    ]

    # If the number of remaining eligible candidates is less than remaining slots,
    # we can't possibly fill the roster.
    if len(eligible_candidates) < remaining_slots:
        return False

    # Define the PuLP problem
    prob = pulp.LpProblem("DraftSolvability", pulp.LpMaximize)
    
    # Dummy objective (we only care about feasibility)
    prob += 0
    
    # Define binary selection variables for eligible candidates
    x = {
        i: pulp.LpVariable(f"x_{i}", cat=pulp.LpBinary)
        for i in range(len(eligible_candidates))
    }
    
    # 1. Total remaining slots constraint
    prob += pulp.lpSum(x[i] for i in range(len(eligible_candidates))) == remaining_slots
    
    # 2. Total remaining budget constraint
    prob += pulp.lpSum(
        eligible_candidates[i].get("credit_cost", 0.0) * x[i]
        for i in range(len(eligible_candidates))
    ) <= remaining_budget
    
    # 3. Wicketkeeper constraint: exactly 1 WK overall
    prob += pulp.lpSum(
        1 * x[i] for i in range(len(eligible_candidates))
        if eligible_candidates[i].get("role") == "WK"
    ) + current_wk_count == 1
    
    # 4. Bowler constraint: at least 3 Bowlers overall
    prob += pulp.lpSum(
        1 * x[i] for i in range(len(eligible_candidates))
        if eligible_candidates[i].get("role") == "BOWL"
    ) + current_bowl_count >= 3
    
    # 5. Overseas constraint: at most 4 overseas players overall
    prob += pulp.lpSum(
        1 * x[i] for i in range(len(eligible_candidates))
        if eligible_candidates[i].get("is_overseas")
    ) + current_overseas_count <= 4
    
    # 6. Unique physical players: max 1 season selected for any player_id
    # Group candidates by player_id
    player_groups: dict[str, list[int]] = {}
    for idx, candidate in enumerate(eligible_candidates):
        p_id = str(candidate["player_id"])
        player_groups.setdefault(p_id, []).append(idx)
        
    for p_id, indices in player_groups.items():
        prob += pulp.lpSum(x[i] for i in indices) <= 1

    # Solve the ILP problem silently
    try:
        status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
        return status == pulp.LpStatusOptimal
    except Exception as e:
        logger.error(f"Error occurred during PuLP solver execution: {e}")
        return False
