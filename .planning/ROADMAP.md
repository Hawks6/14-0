# Roadmap: 14-0 — IPL Draft & Simulation Platform

## Overview

This roadmap defines the implementation path for the 14-0 IPL Draft & Simulation Platform. It progresses from establishing the normalized historical player dataset, implementing the core Monte Carlo simulation engine, building the constraint-based draft engine, orchestrating the 14-match PvE tournament flow, layering on advanced IPL rules (Impact Player, DLS), and finally wrapping it all in a premium, responsive Next.js mobile-first UI.

## Phases

- [ ] **Phase 1: Data Model & Ingestion Engine** - Create the PostgreSQL database schema and ingestion parser for normalized player ratings.
- [ ] **Phase 2: Core Simulation & Probability Engine** - Implement the Markov chain delivery outcome simulator and calibrate outcomes.
- [ ] **Phase 3: Draft Engine & Constraint Solver** - Build the spin selection pools and draft optimizer using PuLP.
- [ ] **Phase 4: Match Orchestrator & Season State** - Set up the 14-match schedule progression and event-sourced logging.
- [ ] **Phase 5: Advanced Cricket Rules** - Layer on IPL rules including the Impact Player rule and DLS stochastic weather calculations.
- [ ] **Phase 6: Mobile-First Frontend & Polish** - Create the responsive React interface, spin wheel animations, and scorecard displays.

## Phase Details

### Phase 1: Data Model & Ingestion Engine
**Goal**: Establish the relational model and ingest era-normalized player metrics to serve as the foundation for simulation and draft.
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria**:
  1. The database schema for players, seasons, drafts, and matches is successfully migrated in PostgreSQL.
  2. Historical datasets can be imported via an ingestion script, mapping raw stats to era-normalized percentiles.
  3. Precomputed batsman/bowler base matchup matrix entries are verified.
**Plans**: TBD

Plans:
- [x] 01-01: Database schema definition and Alembic configuration
- [x] 01-02: Dataset parser and era-normalization pipelines
- [ ] 01-03: Base matchup probability pre-computation tests

### Phase 2: Core Simulation & Probability Engine
**Goal**: Build a decoupled, high-performance ball-by-ball simulation engine using Markov chain transitions.
**Depends on**: Phase 1
**Requirements**: SIM-01, SIM-02, SIM-03, SIM-04
**Success Criteria**:
  1. Individual deliveries generate realistic outcomes based on dynamic matchup probabilities.
  2. Batting momentum multipliers and bowling pressure modifiers organically shift probabilities.
  3. In a 10,000 match validation simulation, scoring averages align to real IPL benchmarks (157-160 runs/innings, ~30 run SD).
**Plans**: TBD

Plans:
- [ ] 02-01: Markov chain state machine and delivery resolver
- [ ] 02-02: Contextual modifiers and momentum Strategy pattern implementation
- [ ] 02-03: Statistical verification test suite and calibration

### Phase 3: Draft Engine & Constraint Solver
**Goal**: Implement the randomized spin generation and the ILP-based roster builder.
**Depends on**: Phase 2
**Requirements**: DRFT-01, DRFT-02, DRFT-03, DRFT-04
**Success Criteria**:
  1. Spins correctly yield valid random team-era rosters cached in Redis.
  2. Active draft constraint checker verifies budget (100 credits) and role requirements in real time.
  3. The PuLP optimizer successfully validates if a user's remaining slots are mathematically solvable to avoid dead-ends.
**Plans**: TBD

Plans:
- [ ] 03-01: Redis draft session storage and spin mechanics
- [ ] 03-02: PuLP solver integration for constraint check and smart warnings

### Phase 4: Match Orchestrator & Season State
**Goal**: Combine matches into a cohesive 14-match single-player PvE season.
**Depends on**: Phase 3
**Requirements**: GAME-01, GAME-02, GAME-03, GAME-04
**Success Criteria**:
  1. Generating a session produces a 14-match calendar with progressive AI opponent squads.
  2. Simulated seasons track points, wins, losses, and Net Run Rate (NRR) correctly.
  3. All match details are saved as event-sourced logs to allow retrospective scorecard views.
**Plans**: TBD

Plans:
- [ ] 04-01: AI opponent squad generators
- [ ] 04-02: League orchestrator and standings processor
- [ ] 04-03: Event-sourced match logging and FastAPI session endpoints

### Phase 5: Advanced Cricket Rules
**Goal**: Layer IPL-specific rules onto the simulation engine to maximize gameplay fidelity.
**Depends on**: Phase 4
**Requirements**: RULE-01, RULE-02, RULE-03
**Success Criteria**:
  1. Wickets trigger strike rotation, and extras (wides/no-balls) handle score/over increments.
  2. The Impact Player rule allows active substitution during matches, recalculating batting depth.
  3. Weather interruptions correctly reduce overs and compute par targets using standard DLS lookup tables.
**Plans**: TBD

Plans:
- [ ] 05-01: Strike rotation and over rules extension
- [ ] 05-02: Impact Player substitution implementation
- [ ] 05-03: Stochastic weather generator and DLS resource model

### Phase 6: Mobile-First Frontend & Polish
**Goal**: Design and build the interactive user interface optimized for smartphones.
**Depends on**: Phase 5
**Requirements**: UI-01, UI-02, UI-03, UI-04
**Success Criteria**:
  1. Layout adjusts beautifully to mobile viewports with broadcast-style scoreboard layouts.
  2. Spin mechanics feature satisfying visual chimes and slot-reel effects.
  3. Users can complete a draft, view simulated games in a ticker feed, and share final season cards.
**Plans**: TBD

Plans:
- [ ] 06-01: Next.js setup with Tailwind CSS 4 and Zustand global state
- [ ] 06-02: Interactive Draftboard and animated Spin Wheel
- [ ] 06-03: Scorecard displays, ball-by-ball ticker, and share card generator

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Model & Ingestion Engine | 2/3 | Executing | - |
| 2. Core Simulation & Probability Engine | 0/3 | Not started | - |
| 3. Draft Engine & Constraint Solver | 0/2 | Not started | - |
| 4. Match Orchestrator & Season State | 0/3 | Not started | - |
| 5. Advanced Cricket Rules | 0/3 | Not started | - |
| 6. Mobile-First Frontend & Polish | 0/3 | Not started | - |

---
*Roadmap defined: 2026-06-11*
*Last updated: 2026-06-11 after requirements synthesis*
