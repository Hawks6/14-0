# Project Research Summary

**Project:** 14-0 — IPL Draft & Simulation Platform
**Domain:** Sports Draft & T20 Cricket Simulation (F2P Game of Skill)
**Researched:** 2026-06-11
**Confidence:** HIGH

## Executive Summary

14-0 is a mobile-first, single-player draft and simulation game inspired by the viral "38-0" football draft simulator trend. Users spin for random historical IPL team-eras (e.g. 2016 RCB, 2011 CSK), draft a starting XI under strict role and credit constraints, and simulate a 14-match PvE season aiming for an undefeated "14-0" record. 

The core technical challenge lies in building a mathematically rigorous T20 cricket simulation engine that runs efficiently and produces highly realistic statistical outcomes (averaging 157-160 runs/innings with standard deviation of ~30 runs). By utilizing a Markov chain model with factored state representations and composable modifiers (using the Strategy Pattern), the system can capture cricket-specific momentum, wicket clustering, phase adjustments, and stochastic weather interruptions via standard DLS resource tables. 

To ensure high-frequency responsiveness on mobile-first frontends, draft state and transient spin pools are cached in Redis 8, while PostgreSQL 18 holds relational historical rosters and persistent game logs. All computations are handled asynchronously on a Python 3.14/FastAPI backend, with Next.js 16/Zustand driving smooth animations and a premium, responsive user experience.

- **Recommended Approach:** A monorepo separating Next.js (frontend) and FastAPI (backend). The core simulation logic will be a data-driven Markov model built using NumPy/SciPy, decoupled from the API layer, and validated using extensive automated distribution testing (e.g., 10,000 runs) before building the frontend.
- **Key Risks:** 
  - **Simulation Realism:** Inaccuracies in scoring, runaway momentum effects, or unrealistic player/bowler matchup distributions. Mitigation: Continuous statistical validation against real IPL benchmarks.
  - **Salary Cap Exploitability:** Users finding degenerate "stars and scrubs" strategies. Mitigation: An exponential player cost curve (PuLP constraint solver) forcing tough choices.
  - **Performance Bottleneck:** Blocking requests during 14-match synchronous simulations. Mitigation: Async offloading and NumPy vectorization from day one.

## Key Findings

### Recommended Stack
*Detailed documentation: [STACK.md](file:///c:/for%20use/projects-antigravity/14-0/.planning/research/STACK.md)*

We have selected a modern, type-safe stack optimized for high-performance scientific/probabilistic calculations and fast mobile UI rendering.

**Core technologies:**
- **Python 3.14 + FastAPI 0.136:** Powering backend services, offering async-native operations, type safety via Pydantic 2.13, and optimal integration with scientific computing libraries.
- **Next.js 16 (React 19) + Zustand 5:** Responsive mobile-first frontend with minimal bundle size (~1.1KB Zustand vs ~12KB Redux) and React Server Components for fast initial page loads.
- **PostgreSQL 18 + asyncpg:** Robust storage for historical squads, user profiles, and event-sourced ball-by-ball match logs.
- **Redis 8:** Transient caching of draft spins and active simulation state to guarantee sub-100ms API response latency.

### Expected Features
*Detailed documentation: [FEATURES.md](file:///c:/for%20use/projects-antigravity/14-0/.planning/research/FEATURES.md)*

**Must have (table stakes):**
- **Spin/Draft Mechanic:** Randomized visual reel selection of team-era, roster presentation, and limited re-spins (0-3).
- **Roster Builder with Constraints:** 11-player squad, 100-credit budget, 1 WK, min 3 bowlers, max 4 overseas players, with real-time UI validation.
- **Ball-by-Ball Simulator:** Full 20-over innings with batsman strike rotation, bowler allocations (max 4 overs), and complete scorecards.
- **Mobile-First Broadcast UI:** Compact, high-contrast scoreboards, progressive feed rendering, and detailed post-match statistics.

**Should have (competitive):**
- **Momentum Modifiers:** Post-boundary wicket suppression and dot-ball bowling pressure modifiers.
- **Impact Player Rule:** 12th player substitution dynamically altering the batting depth matrix.
- **Stochastic DLS Weather:** Stochastic weather interruptions triggering standard DLS par score target adjustments.

**Defer (v2+):**
- Multiplayer draft lobbies, real-money transactions, live commentary text generation, and user authentication.

### Architecture Approach
*Detailed documentation: [ARCHITECTURE.md](file:///c:/for%20use/projects-antigravity/14-0/.planning/research/ARCHITECTURE.md)*

The platform follows a layered, decoupled service architecture:
1. **Draft Engine:** Manages spin pools and solves squad selection feasibility using Integer Linear Programming (ILP) with PuLP.
2. **Simulation Engine:** Factored Markov chain engine executing step-by-step Monte Carlo delivery sampling.
3. **Data Ingestion Layer:** Ingests and era-normalizes player historical stats (z-scores relative to season averages) to compute base matchup probability matrices.
4. **Match Orchestrator:** Manages the 14-match tournament state machine and records deliveries as an immutable event-sourced log.

### Critical Pitfalls
*Detailed documentation: [PITFALLS.md](file:///c:/for%20use/projects-antigravity/14-0/.planning/research/PITFALLS.md)*

1. **Unrealistic Scores:** Prevented by calibrating transition matrices against T20 benchmarks (mean 157-160, SD ~30, 34% dot ball rate) and conducting bulk validation runs.
2. **State Space Explosion:** Prevented by factoring transition matrices and computing probabilities dynamically on-the-fly per ball instead of materializing a huge matrix.
3. **Stars & Scrubs Exploits:** Prevented by applying an exponential player rating-to-cost scaling curve rather than a linear mapping.
4. **Synchronous Blocking:** Avoided by writing the simulation engine to run fully async with NumPy vectorization (target match duration < 50ms).

## Implications for Roadmap

Based on feature dependencies, database design, and risk mitigation, we propose the following phased approach:

### Phase 1: Data Model & Ingestion Engine
- **Rationale:** The simulation and draft engines depend entirely on validated, era-normalized player statistics. Establishing this schema prevents downstream restructuring.
- **Delivers:** PostgreSQL schema, seed datasets, and parser scripts.
- **Addresses:** Historical player dataset ingestion.
- **Avoids:** Era-blind ratings pitfall.

### Phase 2: Core Simulation & Probability Engine
- **Rationale:** The simulation is the highest technical risk. It must be built, optimized, and statistically validated in isolation before APIs or UI are added.
- **Delivers:** Markov chain transition engine, probability modifiers (Strategy pattern), and automated CLI test runner simulating 10,000 matches.
- **Addresses:** Ball-by-ball simulation engine, Contextual modifiers.
- **Avoids:** Unrealistic scores and state space explosion.

### Phase 3: Draft Engine & Constraint Solver
- **Rationale:** Once players are simulated, we build the constraints under which they are drafted.
- **Delivers:** Spin generation algorithms, active session validation, and PuLP-based ILP cost constraints.
- **Addresses:** Spin mechanic, Draft engine.
- **Avoids:** Salary cap loopholes and dead-end draft states.

### Phase 4: Match Orchestrator & Season State
- **Rationale:** Combines individual matches and drafts into a full 14-match single-player PvE season.
- **Delivers:** Opponent XI generation, match history logging, and tournament standing manager.
- **Addresses:** 14-match PvE league stage, Quick play session flow.
- **Avoids:** Synchronous thread-blocking UI.

### Phase 5: Advanced Cricket Rules
- **Rationale:** Adds the unique rules that make the simulator feel like actual IPL cricket, layered onto a stable engine.
- **Delivers:** Impact Player substitution logic, DLS weather tables, and momentum modifier tuning.
- **Addresses:** Impact Player rule, DLS method, Momentum multiplier.
- **Avoids:** DLS edge-case errors.

### Phase 6: Mobile-First Frontend & Polish
- **Rationale:** Design aesthetics and user feedback are developed last, building on top of the finalized backend API contracts.
- **Delivers:** Next.js UI, slot-machine spin wheel animation (Motion), and live scoreboard display.
- **Addresses:** Mobile-first responsive UI, Redis caching integration.
- **Avoids:** Confusing user constraints and poor visual feedback.

### Suggested Phase Research Flags
- **Phase 2 (Simulation):** Needs deep research into Markov chain transitions and NumPy optimization to meet the <50ms/match performance budget.
- **Phase 3 (Draft Solver):** Requires benchmarking PuLP ILP execution speed under concurrent request loads.
- **Phase 5 (DLS/Impact Player):** Needs careful mapping of ICC DLS resource tables to python matrices.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Python and Next.js are industry standards; chosen libraries are well-supported. |
| Features | HIGH | Directly maps 38-0 viral elements to Cricket/IPL context. |
| Architecture | HIGH | Service-repository split allows testing simulation logic in absolute isolation. |
| Pitfalls | HIGH | Identifies all major pitfalls of sports simulations (DLS, salary caps, scaling). |

**Overall confidence:** HIGH

### Gaps to Address
- **Data Completeness:** The exact shape of the historical player dataset must be finalized. A mock schema will be generated in Phase 1 to proceed with confidence.
- **DLS Coefficients:** Access to precise DLS resource tables is required; a standard 20-over reference matrix will be hardcoded in Phase 5.

## Sources

### Primary (HIGH confidence)
- Official ICC Duckworth-Lewis-Stern (DLS) Reference Materials
- PuLP Linear Programming Documentation
- Python scientific stack docs (NumPy 2.4 / SciPy 1.17)

---
*Research completed: 2026-06-11*
*Ready for roadmap: yes*
