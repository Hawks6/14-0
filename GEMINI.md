<!-- GSD:project-start source:PROJECT.md -->
## Project

**14-0 — IPL Draft & Simulation Platform**

A massive-scale IPL Draft and Simulation Platform inspired by the viral "38-0" football draft simulator trend. Users spin for a random historical IPL franchise and era (e.g., "2016 Royal Challengers Bangalore"), draft players from those squads within strict salary caps and role constraints, and simulate a 14-match league stage aiming for an unbeaten "14-0" record. It abstracts live cricket into a mathematically rigorous, freemium "game of skill."

**Core Value:** The draft-spin-simulate loop must feel addictive and fair — users spin random historical eras, build a dream XI under constraints, and see their team compete through a probabilistically rigorous ball-by-ball simulation engine.

### Constraints

- **Tech stack**: Python (FastAPI) backend, React (Next.js) frontend, PostgreSQL, Redis → prescribed by architectural requirements
- **Simulation engine**: Must use Markov chain / probability matrix approach → mathematical rigor required
- **Salary cap**: Fixed at 100 credits per roster → derived from player historical ratings
- **Roster rules**: Exactly 1 WK, min 3 specialist bowlers, max 4 overseas, 11 players total → IPL regulations
- **Deployment**: Local development only → no cloud deployment for v1
- **Data dependency**: The historical player dataset will be provided later → system must be built to ingest it
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

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
### PostgreSQL Version Note
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
### 3.3 Animation
| Library | Version | Purpose | Rationale |
|---|---|---|---|
| **Motion** (fka Framer Motion) | 12.x | Spin mechanic animations | Draft spin wheel, card reveals, match event animations. Rebranded from `framer-motion` → `motion` package. Import from `motion/react`. Declarative animation API perfect for game-feel interactions |
### 3.4 State Architecture Summary
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
## 7. Version Pinning Summary
### Backend (`pyproject.toml`)
### Frontend (`package.json`)
### Infrastructure
## 8. Architecture Overview
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
