---
phase: 02
slug: core-simulation-probability-engine
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-11
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.x |
| **Config file** | backend/pyproject.toml |
| **Quick run command** | `uv run pytest backend/tests/test_simulation/` |
| **Full suite command** | `uv run pytest backend/tests/` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest backend/tests/test_simulation/`
- **After every plan wave:** Run `uv run pytest backend/tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SIM-01 | unit/integration | `uv run pytest backend/tests/test_simulation/test_simulator.py` | 🔘 pending | 🔘 pending |
| 02-02-01 | 02 | 2 | SIM-02, SIM-03 | unit | `uv run pytest backend/tests/test_simulation/test_modifiers.py` | 🔘 pending | 🔘 pending |
| 02-03-01 | 03 | 3 | SIM-04 | calibration | `uv run pytest backend/tests/test_simulation/test_calibration.py` | 🔘 pending | 🔘 pending |

*Status: 🔘 pending | 🟢 green | 🔴 red | 🟡 flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_simulation/test_simulator.py` — stubs for simulator loop (SIM-01)
- [ ] `backend/tests/test_simulation/test_modifiers.py` — stubs for Strategy modifiers (SIM-02, SIM-03)
- [ ] `backend/tests/test_simulation/test_calibration.py` — stubs for statistical benchmarks calibration test (SIM-04)

---

## Manual-Only Verifications

*None — All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
