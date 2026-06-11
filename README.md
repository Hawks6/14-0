# 14-0 — IPL Draft & Simulation Platform

14-0 is a historical IPL draft-and-sim game inspired by the viral “38-0” sports simulator format: spin a random franchise era, draft a legal XI under strict constraints, then simulate a 14-match season and chase a perfect 14-0 run.

## Game Intro

The core loop is:

1. **Spin** a random historical team-season pool.
2. **Draft** one player per spin while respecting roster rules and salary cap.
3. **Simulate** a 14-match PvE season with ball-by-ball probabilistic outcomes.
4. **Review** scorecards, event logs, and season summary.

This project is built to feel skill-based, repeatable, and mathematically grounded.

## Core Rules

- **Roster size:** 11 players
- **Salary cap:** 100 credits
- **Wicketkeepers:** exactly 1
- **Specialist bowlers:** minimum 3
- **Overseas players:** maximum 4
- **Season target:** go unbeaten across 14 simulated league matches

## Technical Overview

### Stack

- **Backend:** FastAPI + SQLAlchemy (async) + PostgreSQL + Redis
- **Frontend:** Next.js (App Router) + React + Zustand + TanStack Query + Motion
- **Simulation & optimization:** Python probabilistic engine + PuLP feasibility checks
- **Infrastructure:** Docker Compose for PostgreSQL and Redis local services

### Architecture (Current)

- **Frontend (`/frontend`)**
  - Landing page and game UI flows for draft and league simulation.
  - Client state handled with Zustand stores.
  - API integration in `src/lib/api.ts`.

- **Backend (`/backend`)**
  - FastAPI app entrypoint in `app/main.py`.
  - Draft endpoints in `app/api/draft.py`.
  - League simulation endpoints in `app/api/league.py`.
  - Models in `app/models/*` with Alembic migrations in `backend/alembic`.
  - Redis used for draft session cache state.

- **Data flow**
  - Historical dataset ingestion via `backend/ingest_dataset.py`.
  - Seed helper available via `backend/seed_db.py`.

## API Surface (Implemented)

### System
- `GET /health`

### Draft
- `POST /api/draft/session` — create draft session
- `POST /api/draft/session/{session_id}/spin` — spin franchise-season player pool
- `POST /api/draft/session/{session_id}/pick` — draft selected player with constraint + solvability validation
- `GET /api/draft/session/{session_id}` — get session state

### League
- `POST /api/league/start/{draft_session_id}` — simulate full 14-match season
- `GET /api/league/{draft_session_id}` — fetch season matches
- `GET /api/league/match/{match_id}` — fetch match details + ball events

## Local Development

### 1) Start databases

Run from the repository root:

```bash
docker compose up -d db redis
```

### 2) Backend (FastAPI)

```bash
cd backend
# install dependencies using your preferred Python workflow
alembic upgrade head
python seed_db.py
uvicorn app.main:app --reload --port 8000
```

### 3) Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend defaults to `http://localhost:3000` and backend to `http://localhost:8000`.

## Notes

- This repository currently targets **local development** only.
- A production historical dataset is expected to be ingested when available.
- The simulation engine and rules are evolving in phased development.
