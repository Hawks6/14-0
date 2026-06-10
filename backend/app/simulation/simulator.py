import numpy as np
import random
from typing import List, Dict, Any, Optional
from app.simulation.models import MatchOutcome, MatchState, InningsResult, synthesize_base_matchup
from app.simulation.modifiers import SimulationModifier

def get_player_id(player) -> Any:
    val = getattr(player, "id", None)
    if val is not None:
        return val
    if isinstance(player, dict):
        return player.get("id")
    return id(player)

def get_player_role(player) -> str:
    val = getattr(player, "role", None)
    if val is not None:
        return val
    if isinstance(player, dict):
        return player.get("role", "BAT")
    return "BAT"

def get_player_name(player) -> str:
    val = getattr(player, "name", None)
    if val is not None:
        return val
    if isinstance(player, dict):
        return player.get("name", "Player")
    return "Player"

def get_batting_percentile(player) -> int:
    for attr in ("percentile_batting", "batting_percentile"):
        val = getattr(player, attr, None)
        if val is not None:
            return val
    if isinstance(player, dict):
        return player.get("percentile_batting") or player.get("batting_percentile") or 50
    return 50

def get_bowling_percentile(player) -> int:
    for attr in ("percentile_bowling", "bowling_percentile"):
        val = getattr(player, attr, None)
        if val is not None:
            return val
    if isinstance(player, dict):
        return player.get("percentile_bowling") or player.get("bowling_percentile") or 50
    return 50

class InningsSimulator:
    OUTCOMES = list(range(10))

    def __init__(self, seed: Optional[int] = None, modifiers: Optional[List[SimulationModifier]] = None):
        self.rng = np.random.default_rng(seed)
        self.random_inst = random.Random(seed)
        self.modifiers = modifiers if modifiers is not None else []

    def _select_bowler(
        self,
        bowlers: List[Any],
        overs_bowled_tracker: Dict[Any, int],
        last_bowler_id: Optional[Any]
    ) -> Any:
        """
        Selects a valid bowler based on quotas and consecutive over limits.
        Prioritizes players with the 'BOWL' role.
        """
        valid_bowlers = [
            b for b in bowlers
            if get_player_id(b) != last_bowler_id and overs_bowled_tracker.get(get_player_id(b), 0) < 24
        ]
        if not valid_bowlers:
            # Fallback if no valid bowler fits the consecutive limit
            valid_bowlers = [
                b for b in bowlers
                if overs_bowled_tracker.get(get_player_id(b), 0) < 24
            ]
        
        if not valid_bowlers:
            raise ValueError("No valid bowlers available with overs remaining!")

        specialists = [b for b in valid_bowlers if get_player_role(b) == "BOWL"]
        choices = specialists if specialists else valid_bowlers
        
        return self.random_inst.choice(choices)

    def _sample_outcome(self, probs: List[float]) -> int:
        return self.random_inst.choices(self.OUTCOMES, weights=probs)[0]

    def simulate_innings(
        self,
        batting_lineup: List[Any],
        bowling_lineup: List[Any],
        target: Optional[int] = None
    ) -> InningsResult:
        state = MatchState(target=target)
        
        if len(batting_lineup) < 2:
            raise ValueError("Batting lineup must contain at least 2 players")

        # Track batting positions
        striker_idx = 0
        non_striker_idx = 1
        next_batsman_idx = 2
        
        striker = batting_lineup[striker_idx]
        non_striker = batting_lineup[non_striker_idx]
        
        # Bowler tracking
        bowlers = [p for p in bowling_lineup if get_player_role(p) in {"BOWL", "ALLROUNDER"}]
        if not bowlers:
            bowlers = list(bowling_lineup)
            
        overs_bowled_tracker = {get_player_id(b): 0 for b in bowlers}
        last_bowler_id = None
        current_bowler = self._select_bowler(bowlers, overs_bowled_tracker, last_bowler_id)
        
        delivery_log = []
        
        while state.overs_completed < 20 and state.wickets < 10:
            # Check target before delivery
            if target is not None and state.runs >= target:
                break
                
            # Synthesize base matchup
            base_probs = synthesize_base_matchup(
                get_batting_percentile(striker),
                get_bowling_percentile(current_bowler),
                get_player_role(striker)
            )
            
            # Apply modifiers sequentially
            probs = base_probs.tolist()
            for modifier in self.modifiers:
                probs = modifier.apply(state, probs)
                if isinstance(probs, np.ndarray):
                    probs = probs.tolist()
            
            # Normalize and clip final probabilities
            probs = [max(1e-7, p) if idx != 5 else 0.0 for idx, p in enumerate(probs)]
            s = sum(probs)
            probs = [p / s for p in probs]
            
            # Resolve delivery outcome
            outcome_val = self._sample_outcome(probs)
            outcome = MatchOutcome(outcome_val)
            
            is_legal_ball = True
            runs_on_ball = 0
            extra_runs = 0
            wicket_fell = False
            
            if outcome == MatchOutcome.WICKET:
                wicket_fell = True
                state.wickets += 1
                state.last_event_was_wicket = True
                state.consecutive_dots = 0
                state.balls_since_boundary = 10
            elif outcome == MatchOutcome.DOT:
                state.consecutive_dots += 1
                state.balls_since_boundary += 1
                state.last_event_was_wicket = False
            elif outcome == MatchOutcome.WIDE:
                is_legal_ball = False
                extra_runs = 1
                state.consecutive_dots = 0
                state.last_event_was_wicket = False
            elif outcome == MatchOutcome.NO_BALL:
                is_legal_ball = False
                extra_runs = 1
                state.consecutive_dots = 0
                state.last_event_was_wicket = False
            else: # ONE, TWO, THREE, FOUR, SIX
                runs_on_ball = int(outcome)
                state.consecutive_dots = 0
                state.last_event_was_wicket = False
                if outcome in {MatchOutcome.FOUR, MatchOutcome.SIX}:
                    state.balls_since_boundary = 0
                else:
                    state.balls_since_boundary += 1
            
            # Update scores
            state.runs += runs_on_ball + extra_runs
            
            # Record bowler quota
            if is_legal_ball:
                overs_bowled_tracker[get_player_id(current_bowler)] += 1
            
            # Log event
            delivery_log.append({
                "over": state.overs_completed,
                "ball": state.balls_completed + 1 if is_legal_ball else state.balls_completed,
                "striker": get_player_name(striker),
                "bowler": get_player_name(current_bowler),
                "outcome": outcome.name,
                "runs": runs_on_ball + extra_runs,
                "cumulative_score": f"{state.runs}/{state.wickets}"
            })
            
            # Check target immediately after score update
            if target is not None and state.runs >= target:
                if is_legal_ball:
                    state.balls_completed += 1
                    if state.balls_completed == 6:
                        state.overs_completed += 1
                        state.balls_completed = 0
                break

            # Update ball progression and strike rotation
            if is_legal_ball:
                state.balls_completed += 1
                
                if wicket_fell:
                    state.balls_since_boundary = 10
                    if state.wickets < 10:
                        striker = batting_lineup[next_batsman_idx]
                        next_batsman_idx += 1
                    else:
                        break
                else:
                    if runs_on_ball in {1, 3}:
                        striker, non_striker = non_striker, striker
                
                # Check Over Completion
                if state.balls_completed == 6:
                    state.overs_completed += 1
                    state.balls_completed = 0
                    
                    # Swap ends at the end of the over
                    striker, non_striker = non_striker, striker
                    
                    # Change Bowler
                    last_bowler_id = get_player_id(current_bowler)
                    if state.overs_completed < 20 and state.wickets < 10:
                        current_bowler = self._select_bowler(bowlers, overs_bowled_tracker, last_bowler_id)
                        state.balls_since_boundary = 10
            else:
                # Non-legal ball, check if wicket fell (e.g. run out)
                if wicket_fell:
                    state.balls_since_boundary = 10
                    if state.wickets < 10:
                        striker = batting_lineup[next_batsman_idx]
                        next_batsman_idx += 1
                    else:
                        break
                        
        total_overs = state.overs_completed + (state.balls_completed / 6.0)
        extras_count = sum(1 for log in delivery_log if log["outcome"] in {"WIDE", "NO_BALL"})
        
        return InningsResult(
            total_runs=state.runs,
            wickets=state.wickets,
            overs_bowled=total_overs,
            extras=extras_count,
            delivery_log=delivery_log
        )
