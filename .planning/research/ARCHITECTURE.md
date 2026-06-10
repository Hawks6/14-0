# Architecture Research — 14-0 IPL Draft & Simulation Platform

> **Research Type**: Architecture & System Design
> **Date**: 2026-06-11
> **Status**: Complete
> **Sources**: Academic papers (Markov chain cricket models), fantasy sports platform design literature, FastAPI best practices, event sourcing patterns

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (Mobile-First)                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │  │
│  │  │  Spin    │ │  Draft   │ │  Match   │ │  League          │ │  │
│  │  │  Screen  │ │  Board   │ │  Viewer  │ │  Standings       │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │  │
│  └───────┼──────────────┼───────────┼────────────────┼───────────┘  │
│          └──────────────┴───────────┴────────────────┘              │
│                              │ REST API (JSON)                      │
├──────────────────────────────┼──────────────────────────────────────┤
│                        API GATEWAY                                  │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                   FastAPI Application                          │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────┐ │  │
│  │  │   Draft     │ │ Simulation  │ │   Rules    │ │  Match   │ │  │
│  │  │   Engine    │ │   Engine    │ │   Engine   │ │ Orchestr.│ │  │
│  │  │             │ │             │ │            │ │          │ │  │
│  │  │ - Spin Gen  │ │ - Markov    │ │ - IPL Regs │ │ - 14-    │ │  │
│  │  │ - Roster    │ │   Chain     │ │ - Impact   │ │   match  │ │  │
│  │  │   Validate  │ │ - Prob.     │ │   Player   │ │   league │ │  │
│  │  │ - ILP Cap   │ │   Synthesis │ │ - DLS      │ │ - Opp.   │ │  │
│  │  │   Check     │ │ - Momentum  │ │ - Roster   │ │   XI Gen │ │  │
│  │  └──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘ │  │
│  │         └───────────────┴───────────────┴─────────────┘       │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │              Data Ingestion Layer                         │ │  │
│  │  │  CSV/JSON Parser → Validation → Rating Normalization     │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                    │                        │                        │
├────────────────────┼────────────────────────┼───────────────────────┤
│              DATA LAYER                                             │
│  ┌─────────────────┴───┐    ┌──────────────┴────────────────────┐  │
│  │    PostgreSQL        │    │           Redis                    │  │
│  │                      │    │                                    │  │
│  │  - Users             │    │  - Spin cache (team+year pool)    │  │
│  │  - Historical_Squads │    │  - Active draft session state     │  │
│  │  - Draft_Lobbies     │    │  - In-flight match state          │  │
│  │  - Match_Logs        │    │  - Rate limiting                  │  │
│  │  - Player_Ratings    │    │                                    │  │
│  │  - League_Standings  │    │                                    │  │
│  └──────────────────────┘    └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Client | Next.js 16 (App Router) | Mobile-first SPA with SSR for initial load |
| API | FastAPI (Python 3.14+) | REST endpoints, request validation, orchestration |
| Compute | NumPy / SciPy / PuLP | Markov chains, probability matrices, ILP solver |
| Persistence | PostgreSQL 18 | Durable storage for all game entities |
| Cache | Redis 8 | Ephemeral session state, spin pool caching |

---

## 2. Component Responsibilities

### 2.1 Draft Engine

**Purpose**: Manages the spin-draft loop — the core user interaction.

#### Spin Generator
- Maintains a weighted pool of `(franchise, year)` tuples
- On spin request: selects a random pair from Redis-cached pool
- Returns full roster for that era with player ratings, roles, and credit costs

#### Roster Validator
- Enforces IPL squad composition rules on every pick
- Validates incrementally (after each pick) for real-time feedback

#### Credit Constraint Checker (ILP)
- Uses Integer Linear Programming (PuLP) to validate picks
- **ILP Formulation**:
  ```
  Decision Variables: x_i ∈ {0, 1} for each available player i
  Objective: Maximize Σ(rating_i · x_i)
  Constraints:
    Σ(cost_i · x_i) ≤ remaining_budget
    Σ(x_i where role=WK) = wk_still_needed
    Σ(x_i where role=BOWL) ≥ bowlers_still_needed
    Σ(x_i where overseas=true) ≤ overseas_slots_remaining
    Σ(x_i) = players_still_needed
  ```

### 2.2 Simulation Engine

**Purpose**: Ball-by-ball match simulation using Markov chain probability matrices.

#### Probability Synthesis Pipeline
```
Base Player Rating
    │
    ├──→ Batter-Bowler Matchup Matrix
    ├──→ Phase Modifier (powerplay / middle / death overs)
    ├──→ Pressure Modifier (RRR-based aggression shift)
    ├──→ Momentum Multiplier (post-boundary clustering)
    └──→ Final Probability Vector (normalized to sum=1.0)
            [dot, 1, 2, 3, 4, 6, wicket, extras]
```

### 2.3 Data Ingestion Layer

#### Pipeline Stages
```
Raw File (CSV/JSON)
    ├──→ [1] Schema Validation (Pydantic models)
    ├──→ [2] Deduplication
    ├──→ [3] Rating Normalization (0-100 scale)
    ├──→ [4] Probability Pre-computation
    └──→ [5] Bulk Insert (PostgreSQL COPY)
```

### 2.4 Rules Engine

- IPL Roster Rules (11 players, 4 overseas max, role constraints)
- Impact Player Rule (12th player substitution)
- DLS Method (resource table lookup, par score calculation)
- Over/Innings Rules (bowling limits, strike rotation, extras)

### 2.5 Match Orchestrator

#### Match Flow
```
League Match N (of 14)
    ├──→ Generate Opponent XI
    ├──→ Coin Toss (random)
    ├──→ Innings 1 (ball-by-ball simulation loop)
    ├──→ [Optional] Weather Interruption → DLS recalculation
    ├──→ Innings 2 (target-aware simulation)
    ├──→ Result Determination (Win / Loss / Tie → Super Over)
    ├──→ Update League Standings + NRR
    └──→ Persist Match Log (event-sourced ball-by-ball record)
```

---

## 3. Recommended Project Structure

```
14-0/
├── backend/
│   ├── pyproject.toml
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app factory
│   │   ├── config.py                  # Settings (pydantic-settings)
│   │   ├── dependencies.py            # DI (DB session, Redis)
│   │   │
│   │   ├── api/                       # API routers
│   │   │   ├── draft.py               # POST /spin, POST /pick
│   │   │   ├── match.py               # POST /simulate
│   │   │   ├── league.py              # GET /standings
│   │   │   └── ingest.py              # POST /ingest (admin)
│   │   │
│   │   ├── schemas/                   # Pydantic models
│   │   │   ├── draft.py
│   │   │   ├── match.py
│   │   │   ├── player.py
│   │   │   └── league.py
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM
│   │   │   ├── player.py
│   │   │   ├── squad.py
│   │   │   ├── draft.py
│   │   │   ├── match.py
│   │   │   └── league.py
│   │   │
│   │   ├── repositories/             # Data access (Repository pattern)
│   │   │   ├── base.py
│   │   │   ├── player_repo.py
│   │   │   ├── squad_repo.py
│   │   │   ├── draft_repo.py
│   │   │   └── match_repo.py
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── draft_service.py
│   │   │   ├── match_service.py
│   │   │   └── league_service.py
│   │   │
│   │   ├── engine/                    # Core computational engines
│   │   │   ├── simulation/
│   │   │   │   ├── markov.py          # Transition matrix builder
│   │   │   │   ├── probability.py     # Probability synthesis
│   │   │   │   ├── modifiers.py       # Strategy pattern modifiers
│   │   │   │   ├── match_state.py     # Match state machine
│   │   │   │   └── simulator.py       # Ball-by-ball runner
│   │   │   │
│   │   │   ├── draft/
│   │   │   │   ├── spin.py            # Spin generator
│   │   │   │   ├── roster.py          # Roster validator
│   │   │   │   └── optimizer.py       # ILP solver (PuLP)
│   │   │   │
│   │   │   └── rules/
│   │   │       ├── ipl_rules.py
│   │   │       ├── impact_player.py
│   │   │       ├── dls.py
│   │   │       └── over_rules.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── parser.py
│   │   │   ├── validator.py
│   │   │   ├── normalizer.py
│   │   │   └── loader.py
│   │   │
│   │   └── core/
│   │       ├── database.py
│   │       ├── redis.py
│   │       ├── exceptions.py
│   │       └── constants.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_draft/
│       ├── test_simulation/
│       ├── test_rules/
│       └── test_ingestion/
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               # Landing / spin screen
│   │   │   ├── draft/page.tsx
│   │   │   ├── match/[id]/page.tsx
│   │   │   └── league/page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── SpinWheel.tsx
│   │   │   ├── PlayerCard.tsx
│   │   │   ├── DraftBoard.tsx
│   │   │   ├── Scoreboard.tsx
│   │   │   ├── BallByBallFeed.tsx
│   │   │   └── StandingsTable.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useDraft.ts
│   │   │   ├── useMatch.ts
│   │   │   └── useLeague.ts
│   │   │
│   │   ├── lib/api.ts
│   │   └── types/index.ts
│   │
│   └── public/assets/
│
├── data/
│   ├── seed/sample_players.csv
│   └── schema/dataset_spec.json
│
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 4. Architectural Patterns

### 4.1 Repository Pattern (Data Access)

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  API Router  │────→│  Service Layer   │────→│  Repository Layer    │
│  (FastAPI)   │     │  (Business Logic)│     │  (SQLAlchemy Queries)│
└──────────────┘     └──────────────────┘     └──────────────────────┘
                                                        │
                                                        ▼
                                               ┌────────────────┐
                                               │   PostgreSQL   │
                                               └────────────────┘
```

### 4.2 Strategy Pattern (Probability Modifiers)

```python
class ProbabilityModifier(Protocol):
    def apply(self, base_probs: ProbVector, context: MatchContext) -> ProbVector: ...

class PhaseModifier(ProbabilityModifier): ...      # Powerplay / middle / death
class PressureModifier(ProbabilityModifier): ...   # RRR-based aggression shift
class MomentumModifier(ProbabilityModifier): ...   # Post-boundary clustering

class ProbabilitySynthesizer:
    def __init__(self, modifiers: list[ProbabilityModifier]):
        self.modifiers = modifiers

    def synthesize(self, base: ProbVector, ctx: MatchContext) -> ProbVector:
        result = base
        for mod in self.modifiers:
            result = mod.apply(result, ctx)
        return normalize(result)
```

### 4.3 State Machine (Match Progression)

```
TOSS → INNINGS_1 → [WICKET_FALLEN | OVER_COMPLETE] → INNINGS_BREAK
     → INNINGS_2 → [WICKET_FALLEN | OVER_COMPLETE | WEATHER_INTERRUPTION]
     → MATCH_COMPLETE → [SUPER_OVER if tied] → RESULT
```

### 4.4 Event Sourcing (Ball-by-Ball Logs)

Every delivery is an immutable event enabling replay and post-match analysis.

---

## 5. Data Flow Diagrams

### 5.1 Spin → Draft → Simulate → Result Flow

```
User taps "SPIN"
    │
    ▼
GET /api/spin ──→ Redis (cache) or PostgreSQL (miss)
    │
    ▼
Response: {franchise: "RCB", year: 2016, roster: [...]}
    │
    ▼  User picks player
POST /api/pick ──→ Draft Service: validate + credit check (ILP)
    │  (repeat until XI complete)
    ▼
POST /api/simulate ──→ Match Orchestrator: generate opponent, run simulation
    │
    ▼
Response: {result: "WIN", scorecard: {...}, ball_log: [...]}
```

### 5.2 Ball-by-Ball Simulation Loop

```
for innings in [1, 2]:
  for over in range(20):
    select_bowler(bowling_constraints)
    for ball in range(6):
      [1] Get base probability vector (striker × bowler)
      [2] Apply modifier chain (Strategy pattern)
      [3] Sample outcome: np.random.choice([0,1,2,3,4,6,'W','WD','NB'], p=P_final)
      [4] Update match state (score, strike rotation, wickets)
      [5] Append event to log
      [6] Check termination (all out? target reached? weather?)
```

---

## 6. Scaling Considerations

### Start Simple (v1 — Local Dev)

| Decision | Rationale |
|----------|-----------|
| Single FastAPI process | One user at a time |
| Synchronous simulation | Completes in <2 seconds |
| Docker Compose for PostgreSQL + Redis | Zero infra overhead |
| Monolith backend | No inter-service communication needed |

### Performance Budget (v1 Targets)

| Operation | Target Latency |
|-----------|---------------|
| Spin request | < 100ms (Redis cache hit) |
| Draft pick validation | < 200ms (ILP solver + DB write) |
| Full match simulation (480 balls) | < 2 seconds |
| Dataset ingestion (5000 players) | < 30 seconds |
| Page load (frontend) | < 1.5 seconds (SSR + code splitting) |

---

*Architecture research for: IPL Draft & Simulation Platform*
*Researched: 2026-06-11*
