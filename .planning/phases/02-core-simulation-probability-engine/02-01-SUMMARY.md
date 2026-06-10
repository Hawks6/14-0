# Phase 2 Plan 02-01 Summary: Core Simulation & Probability Engine

## Overview
This document summarizes the changes, files created, and verification results for plan `02-01` of Phase 2 (Core Simulation & Probability Engine).

## Created Files
The following files were successfully created:
1. **`backend/app/simulation/models.py`**:
   - `MatchOutcome` IntEnum containing delivery outcomes (`DOT`, `ONE`, `TWO`, `THREE`, `FOUR`, `SIX`, `WICKET`, `WIDE`, `NO_BALL`).
   - `LEAGUE_BASE_PROBS` mapping historical baseline probabilities for each outcome.
   - `MatchState` dataclass tracking the live state of a simulated match (runs, wickets, overs, balls, required target, momentum trackers).
   - `InningsResult` dataclass summarizing innings totals, wickets, overs, extras, and full delivery logs.
   - `synthesize_base_matchup()` combining batter and bowler percentiles with non-linear scaling and tailender boundary suppression.
2. **`backend/app/simulation/simulator.py`**:
   - `InningsSimulator` class managing bowler quotas (max 4 overs, no consecutive overs) and strike rotation.
   - Core Monte Carlo simulation loop (`simulate_innings`) executing ball-by-ball matches with chase target termination.
3. **`backend/tests/test_simulation/test_simulator.py`**:
   - Comprehensive unit test suite covering percentile blending, tailender penalties, bowler selection limits, strike rotation rules, and innings termination conditions.
4. **`backend/tests/test_simulation/test_modifiers.py`**:
   - Basic stub for upcoming modifier tests (to be implemented in plan `02-02`).
5. **`backend/tests/test_simulation/test_calibration.py`**:
   - Basic stub for upcoming calibration test suite.

## Verification Results
All unit tests in `backend/tests/test_simulation/` executed and passed successfully.
```bash
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\for use\projects-antigravity\14-0\backend
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 10 items

tests\test_simulation\test_calibration.py .                              [ 10%]
tests\test_simulation\test_modifiers.py .                                [ 20%]
tests\test_simulation\test_simulator.py ........                         [100%]

============================= 10 passed in 1.40s ==============================
```

### Key Behaviors Verified
- **Percentile Blending**: High batting percentiles properly increase run and boundary chances, while high bowling percentiles increase dot-ball and wicket rates.
- **Tailender Suppression**: Tailenders (bowlers with batting percentiles < 25) have boundary rates heavily suppressed (e.g. sixes multiplier reduced to 0.1x).
- **Bowler Selection**: No bowler bowls more than 4 overs (24 legal balls), and bowlers alternate overs properly.
- **Strike Rotation**: Striker swaps correctly on odd runs (1 or 3 runs), at the end of overs, and after wicket falls (modern ICC striker replacement rule).
- **Innings Termination**: Innings end cleanly on over limits (20 overs), wicket limits (10 wickets), or when the target is successfully chased.

## Git Commit Log
All updates were staged and committed atomically via GSD tools:
- `9e6d92f` — Initialize Wave 0 test stubs
- `95f07d5` — Implement simulation data models and percentile blending
- `6b86c8c` — Implement InningsSimulator core Monte Carlo loop
- `388ac30` — Implement unit tests for InningsSimulator core behaviors
- `3ccf4fc` — Refactor simulator.py to extract _sample_outcome for testability
