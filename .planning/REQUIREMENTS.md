# Requirements: 14-0 — IPL Draft & Simulation Platform

**Defined:** 2026-06-11
**Core Value:** The draft-spin-simulate loop must feel addictive and fair — users spin random historical eras, build a dream XI under constraints, and see their team compete through a probabilistically rigorous ball-by-ball simulation engine.

## v1 Requirements

### Data Ingestion

- [ ] **DATA-01**: Ingest player ratings and attributes from structured JSON/CSV historical datasets.
- [ ] **DATA-02**: Normalize historical statistics using era-relative z-scores/percentiles to make different IPL seasons (e.g. 2008 vs 2024) comparable.
- [ ] **DATA-03**: Precompute default player-bowler matchup transition matrices during ingestion.

### Simulation Engine

- [ ] **SIM-01**: Ball-by-ball simulation using a Monte Carlo Markov chain model mapping to discrete outcomes (0, 1, 2, 3, 4, 6, Wicket, Wide, No Ball).
- [ ] **SIM-02**: Dynamic probability adjustments (Contextual Modifiers) based on current score, wickets lost, and Required Run Rate (RRR).
- [ ] **SIM-03**: Decay-based boundary momentum multiplier to model hot streaks and dot-ball pressure modifiers.
- [ ] **SIM-04**: Decoupled, CLI-testable engine capable of running batch matches (e.g., 10,000 runs) in isolation for calibration.

### Draft Engine

- [ ] **DRFT-01**: Serve random historical franchise + year (e.g. 2016 RCB) pools on spin trigger.
- [ ] **DRFT-02**: Select one player from the served roster per spin, storing active draft state in Redis.
- [ ] **DRFT-03**: Enforce draft constraints (Exactly 11 players, 100 credits budget, 1 WK, min 3 specialist bowlers, max 4 overseas) using Integer Linear Programming (ILP) with PuLP.
- [ ] **DRFT-04**: Real-time validation of remaining salary and active roster constraints.

### Game & Tournament Loop

- [ ] **GAME-01**: Generate a 14-match PvE tournament schedule containing AI opponent squads.
- [ ] **GAME-02**: Manage the tournament progression state machine, calculating standings (points, Net Run Rate).
- [ ] **GAME-03**: Execute the complete session loop (spin → draft 11 → simulate 14 matches) in ~5 minutes.
- [ ] **GAME-04**: Persist match events as event-sourced logs for playback and verification.

### Cricket Rules

- [ ] **RULE-01**: Support player strike rotation, extras (wides, no-balls), and bowler over allocations (max 4 overs per bowler).
- [ ] **RULE-02**: Implement the Impact Player rule allowing substitution of one player during matches.
- [ ] **RULE-03**: Integrate stochastic weather interruptions and par score recalculations using Standard ICC DLS tables.

### User Interface

- [ ] **UI-01**: Mobile-first responsive UI built with Next.js 16 and Tailwind CSS 4.
- [ ] **UI-02**: High-contrast scorecard overlay and ball-by-ball visual ticker.
- [ ] **UI-03**: Animated spin wheel mechanic (Motion) and interactive player draft board.
- [ ] **UI-04**: Session result dashboard showing final season standings and a shareable summary card.

## v2 Requirements

### Multiplayer

- **MULT-01**: Multiplayer live draft lobbies with real-time player selections.
- **MULT-02**: Async league scheduling to play tournaments against other user-drafted XIs.

### Social & Account

- **SOC-01**: User authentication and account creation (email or Google OAuth).
- **SOC-02**: Universal leaderboards highlighting users who achieve the perfect 14-0 record.
- **SOC-03**: Dynamic generation of match commentary using natural language templates.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-Money Entry Fees & Prizes | Avoids regulatory gaming compliance and complexity in India (F2P game of skill only). |
| Cloud Deployment / Hosting | Development is restricted to local docker environments for v1. |
| Actual IPL Match Validation | Cross-referencing simulated outcomes against actual historic match scorecards is deferred. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| SIM-01 | Phase 2 | Pending |
| SIM-02 | Phase 2 | Pending |
| SIM-03 | Phase 2 | Pending |
| SIM-04 | Phase 2 | Pending |
| DRFT-01 | Phase 3 | Pending |
| DRFT-02 | Phase 3 | Pending |
| DRFT-03 | Phase 3 | Pending |
| DRFT-04 | Phase 3 | Pending |
| GAME-01 | Phase 4 | Pending |
| GAME-02 | Phase 4 | Pending |
| GAME-03 | Phase 4 | Pending |
| GAME-04 | Phase 4 | Pending |
| RULE-01 | Phase 5 | Pending |
| RULE-02 | Phase 5 | Pending |
| RULE-03 | Phase 5 | Pending |
| UI-01 | Phase 6 | Pending |
| UI-02 | Phase 6 | Pending |
| UI-03 | Phase 6 | Pending |
| UI-04 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0

---
*Requirements defined: 2026-06-11*
*Last updated: 2026-06-11 after domain research synthesis*
