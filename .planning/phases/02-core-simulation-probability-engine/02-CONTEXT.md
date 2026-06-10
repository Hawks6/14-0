# Phase 2: Core Simulation & Probability Engine - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a decoupled, high-performance ball-by-ball T20 cricket simulation engine using a Monte Carlo Markov chain model. This phase focuses entirely on probability synthesis, transition resolution, momentum, and calibration. The draft engine, UI displays, and league tournaments are out of scope.

</domain>

<decisions>
## Implementation Decisions

### Markov Chain & Modifier Pipeline
- **Orchestration Pattern:** Use a "Base Matchup + Modifier Strategy Chain". Start with a base batter-bowler matchup probability vector, then sequentially apply contextual modifiers (powerplay, Required Run Rate pressure, momentum) using the Strategy Pattern.
- **Matchup Synthesis:** Combine the batter's percentile profile and the bowler's percentile profile using weighted multiplicative formulas (geometric mean/weighted averages) to generate base delivery probabilities, then normalize to 1.0.

### Momentum & Bowling Pressure
- **Momentum Trigger:** Trigger positive batting momentum when a batsman hits a 6, or hits consecutive boundaries (4s or 6s) within 3 deliveries.
- **Momentum Decay:** Batting momentum decays exponentially by 35% per ball (multiplied by `0.65^(balls_since_boundary)`). Wicket probability is suppressed during high momentum.
- **Bowling Pressure:** Consecutive dot balls build bowling pressure, increasing the base wicket probability by 5% per dot ball, up to a defined cap. Any run scored resets this pressure.

### Calibration & Testing
- Establish a standalone CLI test script to simulate 10,000 matches in isolation to calibrate scoring distributions against actual IPL benchmarks (mean 157-160 runs, SD ~30).

### the agent's Discretion
- Choice of exact mathematical weights when blending batter/bowler ratings.
- Cap limits for batting momentum and dot-ball pressure adjustments.
- Log formatting of delivery events in the test CLI output.

</decisions>

<canonical_refs>
## Canonical References

### Simulation Requirements & Design
- `.planning/PROJECT.md` — Simulation engine background.
- `.planning/REQUIREMENTS.md` — Specifications for requirements `SIM-01`, `SIM-02`, `SIM-03`, and `SIM-04`.
- `.planning/research/STACK.md` — Pinned scientific dependencies (NumPy 2.4, SciPy 1.17).
- `.planning/phases/01-data-model-ingestion-engine/01-CONTEXT.md` — Percentile ratings schema defined in Phase 1.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/core/database.py` — Database async engine.
- `backend/app/models/player.py` — ORM models for Player and PlayerSeason containing normalized percentiles.

### Established Patterns
- Greenfield Python backend module layout with type annotations (`Mapped`).

### Integration Points
- The simulation engine will read player ratings from `player_seasons` generated in Phase 1.

</code_context>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-core-simulation-probability-engine*
*Context gathered: 2026-06-11*
