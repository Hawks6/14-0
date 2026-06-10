# Phase 2: Core Simulation & Probability Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-11
**Phase:** 2-Core Simulation & Probability Engine
**Areas discussed:** Markov Chain & Modifier Pipeline, Momentum Multiplier Trigger & Decay

---

## Markov Chain & Modifier Pipeline

| Option | Description | Selected |
|--------|-------------|----------|
| Base Matchup + Modifier Strategy Chain | Start with a batter-bowler base vector, then sequentially apply modifiers for powerplay, pressure, and momentum using the Strategy Pattern. | Yes (Recommended) |
| Static State-Space Matrix | Map every possible game state to a static lookup matrix. | No |

**User's choice:** Base Matchup + Modifier Strategy Chain
**Notes:** Strategy Pattern provides maximum modularity and flexibility when scaling probability rules.

---

## Base Matchup Vector Synthesis

| Option | Description | Selected |
|--------|-------------|----------|
| Weighted Multiplicative Synthesis | Combine the batter's percentile profile and the bowler's profile using weighted formulas, then normalize. | Yes (Recommended) |
| Additive Delta Offsets | Start with a league average baseline and add/subtract offsets. | No |

**User's choice:** Weighted Multiplicative Synthesis
**Notes:** Ensures player stats organically blend together into a unified vector.

---

## Momentum Trigger Conditions

| Option | Description | Selected |
|--------|-------------|----------|
| High-value Boundary | Triggered by hitting a 6, or hitting consecutive boundaries (4s or 6s) within 3 deliveries. | Yes (Recommended) |
| Any Boundary | Any 4 or 6 triggers momentum immediately. | No |
| Batter Rating-dependent | Only star batsmen with overall rating > 85 can trigger momentum. | No |

**User's choice:** High-value Boundary
**Notes:** Makes hot streaks feel earned and realistic, matching actual T20 clustering mechanics.

---

## Momentum Decay and Bowling Counter-Pressure

| Option | Description | Selected |
|--------|-------------|----------|
| Exponential Decay & Pressure Stacking | Batting momentum decays by 35% per ball. Consecutive dot-balls build bowling pressure (increasing wicket probability by 5% per dot ball up to a cap). | Yes (Recommended) |
| Linear Decay Only | Batting momentum decays by a flat rate per ball over a fixed 5 deliveries, with no dot-ball pressure. | No |
| No Decay (Fixed Duration) | Momentum lasts for a fixed number of deliveries. | No |

**User's choice:** Exponential Decay & Pressure Stacking
**Notes:** Captures the true tension of dot-ball pressure and realistic momentum curves in cricket.

---

## the agent's Discretion
- Choice of exact mathematical weights when blending batter/bowler ratings.
- Cap limits for batting momentum and dot-ball pressure adjustments.
- Log formatting of delivery events in the test CLI output.
