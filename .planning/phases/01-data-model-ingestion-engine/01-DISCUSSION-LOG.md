# Phase 1: Data Model & Ingestion Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-11
**Phase:** 1-Data Model & Ingestion Engine
**Areas discussed:** Era Normalization & Sample Size Calibration

---

## Era Normalization & Sample Size Calibration

| Option | Description | Selected |
|--------|-------------|----------|
| Season-relative Percentiles | Rank players on 0-99 scale within each specific IPL season. Robust against outliers. | Yes (Recommended) |
| Season-relative Z-Scores | Standard deviations from that season's mean. Preserves precise statistical distances. | No |
| Raw Absolute Stats | No relative normalization. | No |

**User's choice:** Season-relative Percentiles
**Notes:** Maps ratings to a 0-99 percentile rank within that season to ensure robust cross-era comparison.

---

## Minimum Sample Size Threshold

| Option | Description | Selected |
|--------|-------------|----------|
| 30 balls faced / 30 balls bowled | Filters out extreme outliers with 1-2 lucky deliveries while keeping useful backups. | Yes (Recommended) |
| 10 balls faced / 10 balls bowled | More inclusive, but risks highly skewed z-scores/percentiles. | No |
| No minimum threshold | Include everyone. | No |

**User's choice:** 30 balls faced / 30 balls bowled
**Notes:** Keeps useful backup players while removing extreme anomalies.

---

## Handling of Low-Sample Players (Below Threshold)

| Option | Description | Selected |
|--------|-------------|----------|
| Assign baseline average ratings | Assign flat season average rating of 50/100 so they remain playable but average. | Yes (Recommended) |
| Exclude them entirely | Roster will only contain players who met the threshold. | No |
| Apply a regressed rating | Regress tiny sample sizes toward league average using prior distribution. | No |

**User's choice:** Assign baseline average ratings
**Notes:** Assigns a flat rating of 50 to ensure low-sample squad players can still fill roster positions.

---

## the agent's Discretion
- Choice of exact database table naming conventions.
- Details of CSV/JSON raw ingestion file structures.
- CLI script logging output style and error handling.
