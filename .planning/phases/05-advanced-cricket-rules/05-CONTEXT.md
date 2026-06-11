# Phase 5: Advanced Cricket Rules — Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Layer IPL-specific rules onto the existing InningsSimulator to maximize gameplay fidelity.
Phase 5 sits on top of the Phase 2 simulation engine and is decoupled from the Phase 4 match orchestration/scheduling layer.

Three areas of work:
1. **Strike rotation + over rules** — extras increment over counts correctly, bowler quota enforcement (max 4 overs = 24 legal balls per bowler per innings, already partially coded with the `overs_bowled_tracker` using `< 24` balls), wide/no-ball re-deliveries.
2. **Impact Player substitution** — IPL rule: team can swap one player (batting or bowling) mid-match. Recalculate batting depth/bowling pool dynamically.
3. **DLS weather interruptions** — Stochastic weather event during innings 2 reduces remaining overs; compute par score via standard ICC D/L resource percentage table.

Out of scope: live UI updates, Phase 4 season state, frontend.
</domain>

<decisions>
## Implementation Decisions

### 05-01: Strike Rotation & Over Rules
- **Bowler quota**: Already uses `overs_bowled_tracker` in balls (max 24). No change to data model needed — enforce that a bowler is excluded once they reach 24 legal balls.
- **Wide handling**: Currently wides add 1 run and do NOT advance ball count (`is_legal_ball = False`). **This is correct per IPL rules** — no change needed.
- **No-ball handling**: No-balls add 1 run, delivery is not counted (`is_legal_ball = False`), AND the batter gets a free hit on the next ball. Add `state.free_hit_next: bool` flag to `MatchState`. On a free hit, the WICKET outcome is remapped to DOT (batter cannot be dismissed off a free hit except run-out).
- **Strike rotation on extras**: Current code correctly doesn't rotate strike on wide/no-ball.
- **End of over strike swap**: Already correctly implemented.
- **Bowler quota per match (not per innings)**: In T20 each bowler bowls in one innings only, so per-innings quota is fine.
- **Test**: Unit tests verifying no-ball → free hit → wicket suppression; bowler quota exhaustion fallback.

### 05-02: Impact Player Rule
- **Trigger**: Impact Player swap can be triggered once per match, at any fall of wicket OR at the start of any over.
- **Implementation**: Add `impact_player_used: bool` to match state (passed in from orchestrator). `InningsSimulator.simulate_innings` accepts an optional `impact_player: Optional[Any]` argument. If provided and not yet used, at the first fall of wicket after ball 6 (end of PP), swap the designated player into the batting or bowling lineup.
- **Batting impact**: Replace the last unplayed batsman slot with the impact player.
- **Bowling impact**: Add the impact player to the available bowlers pool if they have a bowling role.
- **Agent Discretion**: Exact trigger timing (wicket vs. over boundary) — agent picks wicket trigger for simplicity.

### 05-03: Stochastic Weather + DLS
- **Weather trigger**: At the start of innings 2 (or mid-innings-1 for Duckworth Lewis on batting team), a random weather event may reduce the total overs. Probability of interruption: 15% per match.
- **Overs reduction**: If triggered, pick a uniform random reduction of 1–5 overs (minimum 5 overs must remain for a valid match).
- **DLS par score**: Use the standard ICC D/L resource percentage lookup table (simplified 10-wicket table). Implement a `DLS_RESOURCES` lookup dict mapping `(overs_remaining, wickets_lost)` → `resource_percentage`. Par = Team1_score × (resources_at_interruption / resources_at_start).
- **Standalone module**: Implement in `backend/app/simulation/weather.py` so it is independently testable and importable by the Phase 4 orchestrator.
- **Test**: Unit tests for resource lookup, weather event generation, and par score calculation.
</decisions>

<canonical_refs>
## Canonical References

- `backend/app/simulation/simulator.py` — InningsSimulator (existing, to be extended).
- `backend/app/simulation/models.py` — MatchState, InningsResult, MatchOutcome (existing, to be extended).
- `backend/app/simulation/modifiers.py` — modifier pattern (reuse Protocol).
- `.planning/REQUIREMENTS.md` — RULE-01, RULE-02, RULE-03.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `InningsSimulator.simulate_innings` — main loop to extend in-place.
- `MatchState` dataclass — extend with `free_hit_next: bool = False`.
- `SimulationModifier` Protocol — can add a `FreeHitModifier` following the same pattern.
- `overs_bowled_tracker` — already tracks per-bowler ball count; bowler quota max is already `< 24`.

### Integration Points
- Phase 4 (Match Orchestrator) will call `InningsSimulator` and pass in `impact_player` + receive `InningsResult`.
- Phase 4 will call `weather.py` before starting innings 2 to determine if overs are reduced.
</code_context>

<deferred>
## Deferred Ideas

- Full Duckworth-Lewis-Stern (DLS) v2 table (261 rows × 10 wickets) — using simplified 10-over-bucket table for v1.
- Rain during innings 1 (Team 1's innings interrupted) — deferred to v2.
- Umpire's Call for LBW — deferred.
</deferred>

---
*Phase: 05-advanced-cricket-rules*
*Context gathered: 2026-06-11*
