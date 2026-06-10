# Phase 1: Data Model & Ingestion Engine - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Create the PostgreSQL database schema and ingestion parser for player ratings and historical squads. This phase focuses entirely on data definition, ingestion scripts, and normalizations. The drafting mechanic, match simulation engine, and user interfaces are out of scope for this phase.

</domain>

<decisions>
## Implementation Decisions

### Data Normalization & Era Calibration
- **Normalization Method:** Use season-relative percentiles (ranking players on a 0-99 scale within each specific IPL season) to ensure ratings are comparable across different eras (e.g. 2008 vs 2024).
- **Minimum Sample Size:** Enforce a minimum threshold of 30 balls faced (for batting) or 30 balls bowled (for bowling) in a given season for a player's season stats to be eligible for relative percentile calculations.
- **Low-Sample Handling:** For players who fall below the 30-ball threshold in a season, assign a flat baseline average rating (50/100) for those attributes, ensuring they are still draftable and playable without distorting statistical ranges.

### Ingestion execution
- Ingestion will be triggered via a Python CLI script (e.g. `python -m app.ingestion.loader` or a similar UV script command).
- The script will read source CSV/JSON files, run the normalization pipeline, and bulk-load data into PostgreSQL.

### Matchup Strategy
- Base matchups (batter vs bowler) will be computed dynamically with standard default fallback coefficients, rather than pre-calculating every single pair in the database.

### the agent's Discretion
- Choice of exact database table naming conventions (snake_case vs CamelCase).
- The CSV/JSON file structure details for raw ingestion.
- Logging output style and error handling within the ingestion script.

</decisions>

<canonical_refs>
## Canonical References

### Project Requirements & Stack
- `.planning/PROJECT.md` — Roster rules and credit constraints background.
- `.planning/REQUIREMENTS.md` — Specifications for requirements `DATA-01`, `DATA-02`, and `DATA-03`.
- `.planning/research/STACK.md` — Backend dependency version pinning (PostgreSQL 18, SQLAlchemy 2.0, asyncpg).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None (Greenfield project).

### Established Patterns
- None (First phase).

### Integration Points
- This phase establishes the core DB models that all subsequent phases (Draft, Simulation, Match Orchestrator) will build upon.

</code_context>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-data-model-ingestion-engine*
*Context gathered: 2026-06-11*
