import numpy as np
from app.simulation.simulator import InningsSimulator
from app.simulation.modifiers import PowerplayModifier, MomentumModifier, BowlingPressureModifier

class DummyPlayer:
    def __init__(self, id_val, name, role, percentile_batting, percentile_bowling):
        self.id = id_val
        self.name = name
        self.role = role
        self.percentile_batting = percentile_batting
        self.percentile_bowling = percentile_bowling

class SafeInningsSimulator(InningsSimulator):
    def _sample_outcome(self, probs: np.ndarray) -> int:
        probs = probs.copy()
        if len(probs) > 5:
            probs[5] = 0.0
            probs = probs / np.sum(probs)
        return super()._sample_outcome(probs)

def run_sim(bat_pcts, bowl_pcts, runs=400):
    roles = ["BAT", "BAT", "BAT", "WK", "BAT", "ALLROUNDER", "ALLROUNDER", "BOWL", "BOWL", "BOWL", "BOWL"]
    
    batting_team = []
    for i in range(11):
        batting_team.append(DummyPlayer(i+1, f"B_{i+1}", roles[i], bat_pcts[i], bowl_pcts[i]))
        
    bowling_team = []
    for i in range(11):
        bowling_team.append(DummyPlayer(i+1, f"Bowler_{i+1}", roles[i], bat_pcts[i], bowl_pcts[i]))
        
    modifiers = [
        PowerplayModifier(),
        MomentumModifier(),
        BowlingPressureModifier()
    ]
    sim = SafeInningsSimulator(seed=123, modifiers=modifiers)
    
    scores = []
    wickets = []
    for _ in range(runs):
        res = sim.simulate_innings(batting_team, bowling_team)
        scores.append(res.total_runs)
        wickets.append(res.wickets)
        
    scores = np.array(scores)
    wickets = np.array(wickets)
    return scores.mean(), scores.std(), wickets.mean()

print("Sweeping fragile batting lineups:")
bat_pcts = [78, 74, 68, 50, 35, 20, 10, 5, 5, 5, 5]
for q_bowl in range(50, 71):
    bowl_pcts = [10, 10, 10, 10, 10, q_bowl - 10, q_bowl - 10, q_bowl, q_bowl, q_bowl, q_bowl]
    m_score, std_score, m_wickets = run_sim(bat_pcts, bowl_pcts, runs=500)
    
    is_ok = (154.0 <= m_score <= 163.0) and (25.0 <= std_score <= 35.0) and (5.5 <= m_wickets <= 7.5)
    if is_ok:
        print(f"MATCH! q_bowl={q_bowl} -> Mean={m_score:.2f}, SD={std_score:.2f}, Wickets={m_wickets:.2f}")
    else:
        print(f"       q_bowl={q_bowl} -> Mean={m_score:.2f}, SD={std_score:.2f}, Wickets={m_wickets:.2f}")
