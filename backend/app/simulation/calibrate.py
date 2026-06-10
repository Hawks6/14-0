import argparse
import time
import numpy as np
from typing import List, Any
from app.simulation.simulator import InningsSimulator
from app.simulation.modifiers import PowerplayModifier, MomentumModifier, BowlingPressureModifier

class DummyPlayer:
    def __init__(self, id_val: int, name: str, role: str, percentile_batting: int, percentile_bowling: int):
        self.id = id_val
        self.name = name
        self.role = role
        self.percentile_batting = percentile_batting
        self.percentile_bowling = percentile_bowling



def get_calibrated_lineup() -> List[DummyPlayer]:
    """
    Returns a standard dummy lineup calibrated to yield realistic IPL scores:
    - Mean score: 157-160
    - Standard deviation: ~30
    - Average wickets: 5.5 - 7.5
    """
    roles = ["BAT", "BAT", "BAT", "WK", "BAT", "ALLROUNDER", "ALLROUNDER", "BOWL", "BOWL", "BOWL", "BOWL"]
    bat_pcts = [50, 50, 50, 50, 50, 30, 20, 5, 5, 5, 5]
    bowl_pcts = [10, 10, 10, 10, 10, 55, 55, 39, 39, 39, 39]
    
    players = []
    for i in range(11):
        players.append(DummyPlayer(
            id_val=i + 1,
            name=f"Player_{i + 1}",
            role=roles[i],
            percentile_batting=bat_pcts[i],
            percentile_bowling=bowl_pcts[i]
        ))
    return players

def run_calibration(runs: int):
    print(f"Running calibration simulation with {runs:,} runs...")
    
    batting_team = get_calibrated_lineup()
    bowling_team = get_calibrated_lineup()
    
    modifiers = [
        PowerplayModifier(),
        MomentumModifier(),
        BowlingPressureModifier()
    ]
    sim = InningsSimulator(seed=123, modifiers=modifiers)
    
    scores = []
    wickets = []
    extras = []
    fours = 0
    sixes = 0
    total_balls = 0
    
    start_time = time.time()
    for _ in range(runs):
        res = sim.simulate_innings(batting_team, bowling_team)
        scores.append(res.total_runs)
        wickets.append(res.wickets)
        extras.append(res.extras)
        
        for log in res.delivery_log:
            outcome = log["outcome"]
            if outcome == "FOUR":
                fours += 1
            elif outcome == "SIX":
                sixes += 1
            if outcome not in ("WIDE", "NO_BALL"):
                total_balls += 1
                
    elapsed = time.time() - start_time
    
    scores = np.array(scores)
    wickets = np.array(wickets)
    extras = np.array(extras)
    
    mean_score = scores.mean()
    std_score = scores.std()
    mean_wickets = wickets.mean()
    mean_extras = extras.mean()
    four_rate = fours / total_balls if total_balls > 0 else 0
    six_rate = sixes / total_balls if total_balls > 0 else 0
    
    print("\n--- Calibration Results ---")
    print(f"Mean Score: {mean_score:.2f}")
    print(f"Std Dev: {std_score:.2f}")
    print(f"Mean Wickets: {mean_wickets:.2f}")
    print(f"Mean Extras: {mean_extras:.2f}")
    print(f"Four Rate: {four_rate * 100:.2f}% ({fours} fours)")
    print(f"Six Rate: {six_rate * 100:.2f}% ({sixes} sixes)")
    print(f"Execution Time: {elapsed:.3f}s ({(elapsed / runs) * 1000:.3f}ms per innings)")
    
    return {
        "mean_score": mean_score,
        "std_score": std_score,
        "mean_wickets": mean_wickets,
        "mean_extras": mean_extras,
        "elapsed": elapsed
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run match simulation calibration")
    parser.ArgumentOption = parser.add_argument(
        "--runs",
        type=int,
        default=10000,
        help="Number of simulations to run (default: 10000)"
    )
    args = parser.parse_args()
    run_calibration(args.runs)
