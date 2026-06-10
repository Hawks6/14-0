# Technology Stack — 14-0 IPL Draft & Simulation Platform

> Research Date: 2026-06-11
> Status: **Prescriptive** — versions pinned to current stable releases

---

## 1. Core Technologies

| Technology | Version | Purpose | Rationale |
|---|---|---|---|
| **Python** | 3.14.x | Runtime for backend services | Latest stable (3.14.6 released 2026-06-10). Rich scientific computing ecosystem (NumPy, SciPy) critical for Markov chain simulation engine |
| **FastAPI** | 0.136.x | REST API framework | Async-native, automatic OpenAPI docs, Pydantic-first validation. ~38% Python developer adoption in 2026. Production-proven at Netflix, Microsoft, Uber |
| **Uvicorn** | 0.49.x | ASGI server | High-performance async server for FastAPI. Native `asyncio` event loop with `uvloop` support |
| **Pydantic** | 2.13.x | Data validation & serialization | Core dependency of FastAPI. Type-safe request/response models, settings management. Rust-powered core for validation speed |
| **Next.js** | 16.x | React meta-framework | Server Components, SSR/SSG, Turbopack (Rust bundler, now default), mobile-first routing. Industry-standard React framework for production apps |
| **React** | 19.x | UI library | Component model, hooks, React Compiler (auto-memoization). Ships with Next.js 16 |
| **PostgreSQL** | 18.x | Relational database | Latest stable (18.4 released 2026-05-14). JSONB for flexible player attribute storage, CTEs for complex draft queries, excellent indexing for historical data lookups |
| **Redis** | 8.x | In-memory cache & state store | Latest stable (8.8.0 released 2026-06). Built-in rate limiter, new Array data type, sub-key notifications. Used for draft spin caching, transient match-state management |

### Python Version Note
Pin to **Python 3.14.x** (not 3.15 beta). NumPy 2.4.x and SciPy 1.17.x are fully validated against 3.14.

### PostgreSQL Version Note
PostgreSQL 18 is preferred over 17 (which is also supported). PG 18 offers improved query planning and partitioning — useful for partitioning `Match_Logs` by season.

---

## 2. Backend — Supporting Libraries

### 2.1 Simulation Engine (Probabilistic Computing)

| Library | Version | Purpose | Rationale |
|---|---|---|---|
| **NumPy** | 2.4.x | Probability matrices, array ops | Core of the Markov chain transition matrices. Vectorized operations for ball-by-ball outcome computation. 2.4.6 is latest stable |
| **SciPy** | 1.17.x | Statistical distributions | `scipy.stats` for probability distributions (batting/bowling performance curves). `scipy.sparse` for sparse transition matrices. HiGHS solver integrated for optimization |
| **pandas** | 3.0.x | Dataset ingestion & transformation | Ingest CSV/JSON historical player datasets, transform to normalized DB schema. pandas 3.0 has copy-on-write by default (performance boost) and dedicated string dtype |
| **PuLP** | 3.30.x | Integer Linear Programming | Draft constraint solver — enforce salary cap (100 credits), role constraints (1 WK, 3+ bowlers, 4 max overseas). PuLP preferred over `scipy.optimize.linprog` for complex modeling with named constraints and multiple solver backends (CBC, HiGHS) |

### 2.2 Database Access

| Library | Version | Purpose | Rationale |
|---|---|---|---|
| **SQLAlchemy** | 2.0.x | ORM & query builder | `Mapped` types, `mapped_column` for modern type-safe models. First-class async support via `create_async_engine`. 2.0.50 is latest stable |
| **asyncpg** | 0.31.x | Async PostgreSQL driver | Native binary protocol implementation — significantly faster than psycopg3 for async workloads. Used as SQLAlchemy's async dialect backend |
| **Alembic** | 1.18.x | Database migrations | `alembic init -t async` for async-native migration environment. Auto-generates migrations from SQLAlchemy model changes. 1.18.4 is latest stable |

### 2.3 Networking & Integration

| Library | Version | Purpose | Rationale |
|---|---|---|---|
| **httpx** | 0.28.x (pinned) | Async HTTP client | For internal service calls and potential external API integrations. ⚠️ Original project maintenance stalled in 2025 — pin to 0.28.1, monitor `httpx2` (Pydantic initiative) as successor. Sufficient for v1 local-dev scope |
| **redis-py** | 8.0.x | Redis client (sync + async) | Unified client with `redis.asyncio` namespace. Install with `redis[hiredis]` for compiled response parser. Matches Redis server 8.x API |

---

## 3. Frontend Libraries

### 3.1 Core UI & Styling

| Library | Version | Purpose | Rationale |
|---|---|---|---|
| **Tailwind CSS** | 4.3.x | Utility-first CSS | Mobile-first by design (unprefixed = mobile, `sm:`/`md:` = larger). Oxide engine (Rust) for 5x faster builds. CSS-first config via `@theme` — no `tailwind.config.js` needed |
| **shadcn/ui** | latest | Component system | Copy-paste component pattern — full code ownership. Built on Radix UI primitives for WCAG-compliant accessibility. Industry standard for Next.js projects in 2026 |
| **Radix UI** | latest | Headless primitives | Keyboard navigation, ARIA attributes, focus management — baked into shadcn/ui components. Handles the "hard parts" of accessible UI |

### 3.2 State Management

| Library | Version | Purpose | Rationale |
|---|---|---|---|
| **Zustand** | 5.0.x | Client UI state | Draft selections, spin state, UI mode toggles. ~1.1 KB bundle, no Provider required, minimal boilerplate. Default choice for MVP/medium-scale apps in 2026 |
| **TanStack Query** | 5.101.x | Server state & data fetching | API response caching, background refetching, optimistic updates. Separates "server state" from "client UI state" — 2026 best practice |

> **Decision: Zustand over Redux** — For this project's scope (single-player quick-play, medium complexity), Zustand's simplicity wins. Redux Toolkit adds ~12 KB + boilerplate overhead that's unjustified without large-team enterprise requirements. If v2 multiplayer introduces complex shared state, revisit.

### 3.3 Animation

| Library | Version | Purpose | Rationale |
|---|---|---|---|
| **Motion** (fka Framer Motion) | 12.x | Spin mechanic animations | Draft spin wheel, card reveals, match event animations. Rebranded from `framer-motion` → `motion` package. Import from `motion/react`. Declarative animation API perfect for game-feel interactions |

> **Note**: Install as `motion` (not `framer-motion`). The old package is deprecated.
> ```bash
> npm install motion
> ```
> ```tsx
> import { motion } from "motion/react";
> ```

### 3.4 State Architecture Summary

```
┌─────────────────────────────────────────┐
│              Component State            │
│         (useState, useReducer)          │
│   Form inputs, toggles, local UI       │
├─────────────────────────────────────────┤
│              Zustand Store              │
│   Draft state, spin results, game      │
│   mode, player selections              │
├─────────────────────────────────────────┤
│           TanStack Query Cache          │
│   Player data, historical rosters,     │
│   match results, leaderboards          │
├─────────────────────────────────────────┤
│         Context API (minimal)           │
│   Theme, locale (if needed)            │
└─────────────────────────────────────────┘
```

---

## 4. Development Tools

### 4.1 Python Tooling

| Tool | Version | Purpose |
|---|---|---|
| **pytest** | 9.0.x | Test framework — parametrize for simulation edge cases |
| **ruff** | 0.15.x | Linter + formatter (replaces flake8, isort, black). Rust-powered, ~100x faster |
| **mypy** | 2.1.x | Static type checking — critical for Pydantic model correctness |
| **uv** | latest | Package manager — Rust-based pip replacement. Fast installs, lock files |

### 4.2 JavaScript/TypeScript Tooling

| Tool | Version | Purpose |
|---|---|---|
| **ESLint** | 10.x | Linter — flat config only (legacy eslintrc removed in v10) |
| **TypeScript** | 5.x | Type safety for frontend — strict mode |
| **Prettier** | latest | Code formatter — integrates with ESLint |

### 4.3 Infrastructure

| Tool | Version | Purpose |
|---|---|---|
| **Docker Compose** | v5.x | Local dev orchestration — PostgreSQL, Redis, backend, frontend in containers |
| **Docker Desktop** | latest | Container runtime (includes Compose plugin). Use `docker compose` (no hyphen) |

### 4.4 Docker Compose Services (Local Dev)

```yaml
services:
  db:
    image: postgres:18
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

  redis:
    image: redis:8
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_started }
    volumes: ["./backend:/app"]  # Hot reload

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
    volumes: ["./frontend:/app"]  # Hot reload
    environment:
      - CHOKIDAR_USEPOLLING=true  # Windows file watching
```

---

## 5. Alternatives Considered

| Category | Chosen | Alternative | Why Not |
|---|---|---|---|
| **Backend Framework** | FastAPI | Django REST Framework | Django's ORM is synchronous-first; FastAPI's native async is critical for concurrent simulation requests |
| **Backend Framework** | FastAPI | Flask | Flask lacks native async, type validation, and auto-generated API docs |
| **Frontend Framework** | Next.js | Vite + React SPA | Next.js provides SSR for initial load performance on mobile networks |
| **Database** | PostgreSQL | MongoDB | Relational data model is natural for player-team-season relationships |
| **Database Driver** | SQLAlchemy + asyncpg | Raw asyncpg | SQLAlchemy provides migration support (Alembic), model definitions, and query building |
| **State Management** | Zustand | Redux Toolkit | ~12 KB vs ~1.1 KB, Provider wrapper overhead, action/reducer boilerplate |
| **Data Fetching** | TanStack Query | SWR | TanStack Query has richer cache invalidation, pagination, and devtools |
| **Animation** | Motion | CSS animations | Spin mechanic requires spring physics and gesture-based interactions |
| **Optimization** | PuLP | scipy.optimize.linprog | PuLP supports named variables/constraints, multiple solver backends |
| **CSS** | Tailwind CSS | CSS Modules | Tailwind's utility-first approach is faster for mobile-first responsive design |

---

## 6. What NOT to Use

| Technology | Reason |
|---|---|
| **Django** | Synchronous ORM is a bottleneck for concurrent simulation |
| **Flask** | No built-in type validation, async support, or API documentation |
| **Express.js / Node.js backend** | Python's NumPy/SciPy ecosystem has no equivalent in Node |
| **MongoDB** | Player-team-season-match data is inherently relational |
| **Firebase / Supabase** | Adds cloud dependency (project is local-dev only for v1) |
| **Redux** | Unnecessary boilerplate and bundle size for single-player MVP |
| **Chakra UI / Material UI** | Heavy runtime CSS-in-JS overhead |
| **framer-motion** (old package) | Deprecated — rebranded to `motion` |
| **GraphQL** | REST is simpler for this well-defined API surface |
| **Socket.io / WebSockets** | No real-time multiplayer in v1 |
| **Celery** | No background job queue needed for v1 |
| **SQLite** | Insufficient for concurrent access patterns |

---

## 7. Version Pinning Summary

### Backend (`pyproject.toml`)

```
python = ">=3.14,<3.15"
fastapi = ">=0.136,<0.137"
uvicorn = {version = ">=0.49,<0.50", extras = ["standard"]}
pydantic = ">=2.13,<3.0"
sqlalchemy = ">=2.0.50,<2.1"
asyncpg = ">=0.31,<0.32"
alembic = ">=1.18,<1.19"
numpy = ">=2.4,<2.5"
scipy = ">=1.17,<1.18"
pandas = ">=3.0,<3.1"
pulp = ">=3.30,<4.0"
redis = {version = ">=8.0,<9.0", extras = ["hiredis"]}
httpx = ">=0.28,<0.29"
pytest = ">=9.0,<10.0"
ruff = ">=0.15,<1.0"
mypy = ">=2.1,<3.0"
```

### Frontend (`package.json`)

```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.100.0",
    "motion": "^12.0.0",
    "tailwindcss": "^4.3.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "eslint": "^10.0.0",
    "@types/react": "^19.0.0",
    "@types/node": "^22.0.0"
  }
}
```

### Infrastructure

```
PostgreSQL: 18.x (Docker image: postgres:18)
Redis: 8.x (Docker image: redis:8)
Docker Compose: v5.x (via Docker Desktop)
Node.js: >=20.x (for Next.js 16)
```

---

## 8. Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    Frontend (Next.js 16)              │
│  ┌─────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ Zustand  │  │ TanStack │  │ Motion (anims)   │    │
│  │ (state)  │  │ Query    │  │ Spin wheel, cards│    │
│  └─────────┘  └──────────┘  └──────────────────┘    │
│  Tailwind CSS 4 + shadcn/ui + Radix primitives       │
└────────────────────┬─────────────────────────────────┘
                     │ REST API (JSON)
┌────────────────────▼─────────────────────────────────┐
│                  Backend (FastAPI 0.136)               │
│  ┌─────────────────────────────────────────────┐     │
│  │        Simulation Engine                     │     │
│  │  NumPy (matrices) + SciPy (distributions)   │     │
│  │  PuLP (draft constraint solver)              │     │
│  └─────────────────────────────────────────────┘     │
│  Pydantic models │ SQLAlchemy ORM │ Alembic migrations│
└───────┬──────────────────────────────┬───────────────┘
        │                              │
┌───────▼───────┐              ┌───────▼───────┐
│ PostgreSQL 18 │              │   Redis 8     │
│ Players, Teams│              │ Spin cache,   │
│ Drafts, Logs  │              │ match state   │
└───────────────┘              └───────────────┘
```

---

*This document is prescriptive. All version numbers reflect stable releases as of 2026-06-11.*
