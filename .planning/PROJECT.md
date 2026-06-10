# 14-0 — IPL Draft & Simulation Platform

## What This Is

A massive-scale IPL Draft and Simulation Platform inspired by the viral "38-0" football draft simulator trend. Users spin for a random historical IPL franchise and era (e.g., "2016 Royal Challengers Bangalore"), draft players from those squads within strict salary caps and role constraints, and simulate a 14-match league stage aiming for an unbeaten "14-0" record. It abstracts live cricket into a mathematically rigorous, freemium "game of skill."

## Core Value

The draft-spin-simulate loop must feel addictive and fair — users spin random historical eras, build a dream XI under constraints, and see their team compete through a probabilistically rigorous ball-by-ball simulation engine.

## Requirements

### Validated

(None yet → ship to validate)

### Active

- [ ] **Spin mechanic** — Randomly serve a specific Team + Year (e.g., CSK 2021) and display that era's roster for drafting
- [ ] **Draft engine** — Let users pick one player per spin from the served historical roster, enforcing role constraints (1 WK, min 3 bowlers, max 4 overseas) and a 100-credit hard salary cap
- [ ] **Historical player dataset ingestion** — Parse CSV/JSON containing Year, Franchise, Player_Name, Role, Base_Rating, and specific attributes (batting avg, strike rate, bowling economy, boundary probability)
- [ ] **Ball-by-ball simulation engine** — Markov chain model outputting discrete events (0,1,2,3,4,6,Wicket,Extras) per delivery, driven by player ratings
- [ ] **Contextual modifiers** — Dynamic probability shifts based on current score, wickets lost, and Required Run Rate
- [ ] **Momentum multiplier** — Clustering logic that suppresses wicket probability for N deliveries after a boundary from a high-variance player
- [ ] **14-match PvE league stage** — User's drafted XI plays 14 AI-generated opponent XIs to chase the 14-0 record
- [ ] **Impact Player rule** — 12th player substitution with batting depth matrix recalculation
- [ ] **DLS method (stochastic weather)** — Random weather interruptions with Duckworth-Lewis-Stern par score calculations
- [ ] **Quick play session flow** — Complete spin→draft→simulate loop in ~5 minutes, single session
- [ ] **PostgreSQL schema** — Tables for Users, Historical_Squads, Draft_Lobbies, Match_Logs
- [ ] **Mobile-first responsive UI** — React/Next.js frontend optimized for mobile viewport
- [ ] **Redis caching** — High-frequency draft spin caching and transient match-state management

### Out of Scope

- Multiplayer draft lobbies → v2 (focus on single-player quick play for MVP)
- Async league scheduling → v2
- Real-money entry fees / prize pools → regulatory complexity, defer
- User authentication / social features → v2
- Deployment to cloud → local dev only for v1
- Monetization implementation → decide revenue model later
- Live match commentary / streaming → v2 cosmetic
- Historical team stat validation against actual IPL records → nice-to-have, not MVP

## Context

- **Inspiration**: The "38-0" football draft simulator trend where users spin random FIFA-rated historical club/era squads and draft players to build an unbeatable team
- **Data model**: System expects a dataset to be ingested post-build containing year-wise IPL teams, players for that year, and FIFA-style simulation ratings (batting avg, strike rate, bowling economy, boundary probability, etc.)
- **Mathematical backbone**: The simulation is built on Markov chains and probability matrices — Python's scientific computing ecosystem (NumPy, SciPy) is critical
- **Target platform**: Mobile-first web app — the primary consumption device is a smartphone
- **Session design**: Quick play — spin, draft, simulate, result — all within ~5 minutes

## Constraints

- **Tech stack**: Python (FastAPI) backend, React (Next.js) frontend, PostgreSQL, Redis → prescribed by architectural requirements
- **Simulation engine**: Must use Markov chain / probability matrix approach → mathematical rigor required
- **Salary cap**: Fixed at 100 credits per roster → derived from player historical ratings
- **Roster rules**: Exactly 1 WK, min 3 specialist bowlers, max 4 overseas, 11 players total → IPL regulations
- **Deployment**: Local development only → no cloud deployment for v1
- **Data dependency**: The historical player dataset will be provided later → system must be built to ingest it

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python/FastAPI for backend | Heavy probabilistic computation (Markov chains, probability matrices) — Python's NumPy/SciPy ecosystem is optimal | → Pending |
| Quick play PvE for MVP | Single-player loop is fastest path to proving the core spin-draft-simulate mechanic | → Pending |
| 100-credit salary cap | Mirrors the FIFA-style "38-0" economy — tight budget forces meaningful draft decisions | → Pending |
| Ball-by-ball simulation (not over-by-over) | Granular simulation enables momentum mechanics and contextual modifiers that make results feel organic | → Pending |
| Historical ratings dataset as separate ingestion | Decouples engine development from data collection — can build and test with seed data | → Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check → still the right priority?
3. Audit Out of Scope → reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-11 after initialization*
