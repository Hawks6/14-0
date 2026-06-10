# PITFALLS.md — 14-0 IPL Draft & Simulation Platform

> Pre-build research into what commonly goes wrong when building cricket simulation engines, probabilistic game systems, and draft mechanics. Every item here is a trap that has caught real projects.

---

## 1. Critical Pitfalls

### 1.1 Probability Distributions That Don't Feel Realistic

**The Problem:** Simulations tend to be either too random (every match a coin flip) or too predictable (best-rated team always wins).

**Why It Happens:**
- Using uniform distributions instead of weighted distributions from real IPL data
- Ignoring that T20 scoring follows a bell curve: mean ~157–160 runs, std dev ~30 runs
- Treating every delivery as independent when cricket has deep contextual dependencies
- Not differentiating between Powerplay (1–6), Middle (7–15), and Death (16–20) overs

**Real-World Benchmarks:**
| Metric | IPL Benchmark |
|--------|--------------|
| Average innings total | 157–160 runs |
| Score standard deviation | ~30 runs |
| 65% of runs | Come from boundaries (fours + sixes) |
| Sixes contribution | ~30–31% of total runs |
| Fours contribution | ~34% of total runs |
| Dot ball percentage | ~34% of deliveries |
| Scores 130–190 range | ~60–65% of all innings |

**Mitigation:**
- Calibrate probability matrices against these real distributions
- Run 10,000 simulated innings and plot the distribution
- Build a "sanity checker" that flags innings outside 80–280 range
- Phase-specific probability tables are non-negotiable

---

### 1.2 Markov Chain State Space Explosion

**The Problem:** Naively encoding every state combination creates ~21.8 million states. Impossible to pre-compute.

**Mitigation:**
- **Never materialize the full matrix.** Generate transitions on-the-fly per delivery
- **Factored state representation:** Separate probability tables that multiply together
- **Lump aggressively:** Bucket scores, tier batsmen (elite/good/average/tailender)
- **Monte Carlo over matrix solving:** Sample forward step-by-step, never solve analytically
- **Benchmark:** Single innings simulation (120 deliveries) in <50ms

---

### 1.3 Credit/Salary Cap Balancing

**The Problem:** Linear rating-to-cost mapping lets users exploit "stars and scrubs" strategy.

**Mitigation:**
- **Exponential cost curve:** Cost = base × (rating / baseline)^1.5-2.0
- **Role-based cost floors:** Bowlers and WKs have meaningful minimums
- **Playtesting:** Across 1000 drafts, win-rate distribution should be normal centered at 50%

---

### 1.4 Player Ratings That Don't Differentiate Between Eras

**The Problem:** "Batting average 35" means different things in 2009 vs 2024. Raw stats aren't comparable.

**Mitigation:**
- **Era-normalize:** Convert to z-scores within each season
- **Or percentile ranks:** "Top 10% of batsmen in their season" is cross-era comparable
- **Hybrid:** Era-relative percentiles for simulation, raw stats for display

---

### 1.5 Simulation Results That Don't Match Cricket Intuition

**Common Violations:**
- Tailenders scoring at top-order rates
- No "collapses" (wicket clusters)
- Every close match on the last ball
- Bowling changes having no effect

**Mitigation:**
- **Batting order decay:** Lower-order scoring probability decreases significantly
- **Wicket clustering:** After a wicket, increase P(wicket) for next 6–12 balls
- **Bowler-batsman matchup:** Even simplified pace/spin preference per batsman
- **Win distribution validation:** Match IPL reality (55–60% comfortable wins, 20–25% close)

---

### 1.6 Momentum Mechanics That Create Runaway Snowball Effects

**The Problem:** Boundary → lower wicket chance → more boundaries → unrealistic 50-run overs.

**Mitigation:**
- **Exponential decay:** `momentum = base_bonus × 0.65^(balls_since_trigger)`
- **Hard cap:** Never exceed ±15–20% adjustment
- **Bidirectional:** Dot balls build bowling "pressure" (natural dampener)
- **Test:** No over exceeds 36 runs more than 0.1% of the time

---

### 1.7 DLS Calculations That Produce Absurd Par Scores

**Mitigation:**
- Use Standard Edition tables (publicly available) as starting point
- Implement resource table lookup, not raw formula
- Cap adjustments if they differ from target by >40%
- Minimum overs rule: no DLS before over 6
- Test every over × wicket combination

---

## 2. Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded probability values | Fast prototyping | 15+ files to grep-replace for tuning | Never — use config from day 1 |
| Engine-API tight coupling | Fewer files initially | Can't unit test or batch-run simulations | Never — define interface contract first |
| Missing ball-by-ball logging | Simpler code | Can't debug outcomes or build replay feature | Never — log from first simulation |

---

## 3. Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Synchronous 14-match simulation | 3–5s frozen UI | Async offloading via ProcessPoolExecutor; NumPy vectorization | Any concurrent users |
| N+1 squad data queries | 200–500ms per spin | Eager loading with JOINs; materialized views; Redis cache | >10 concurrent users |
| Redis memory bloat | OOM crash | Mandatory TTL (30min sliding); `maxmemory-policy: volatile-lru`; compact serialization | 10,000+ abandoned sessions |

---

## 4. Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing raw ratings to frontend | Users reverse-engineer optimal drafts; game becomes solved | Send display tiers only ("Elite"/"Good"/"Average"); server-side simulation only |
| No spin rate limiting | Bots enumerate full database; pre-compute optimal strategies | 10 spins/IP/hour; spin commitment with 5min cooldown; server-side spin assignment |

---

## 5. UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Simulation too fast (no tension) | No emotional engagement; users don't care about results | Tiered display: overview (10–15s/match), speed (2–3s), deep dive (optional) |
| Confusing draft constraints | Users create dead-end rosters; frustration → churn | Live constraint viz; smart warnings; gray out impossible picks; draft undo |
| No visual feedback during 14-match sim | Users think app crashed; close it | Progressive streaming; animated match cards; running W/L record |

---

## 6. "Looks Done But Isn't" Checklist

| # | Feature | What's Actually Missing |
|---|---------|------------------------|
| 1 | Ball-by-ball simulation | Distribution validation against IPL benchmarks; no debug logging |
| 2 | Salary cap draft | Constraint solver doesn't prevent dead-end states; no undo |
| 3 | DLS method | Edge cases at extreme over/wicket combos produce absurd par scores |
| 4 | Momentum multiplier | No decay function → snowball; no counter-momentum for bowling |
| 5 | 14-match league | No opponent variety or progressive difficulty |
| 6 | Historical data ingestion | No era-normalization → 2010 players systematically underperform |
| 7 | Impact Player rule | Batting depth matrix not recalculated |
| 8 | Redis caching | No TTL → memory bloat over time |
| 9 | Mobile-first UI | Breaks on older Android, small screens, landscape |
| 10 | Spin mechanic | No rate limiting; no spin cooldown |

---

## 7. Pitfall-to-Phase Mapping

| Pitfall | Likely Phase | When to Address |
|---------|-------------|-----------------|
| Probability distributions unrealistic | Simulation Engine | During initial calibration |
| Markov state space explosion | Simulation Engine architecture | At design time — wrong choice requires rewrite |
| Credit/salary cap imbalance | Draft Engine + Dataset | After ratings finalized; iterative playtesting |
| Era-blind player ratings | Dataset Ingestion | During data preprocessing |
| Simulation intuition violations | Simulation Engine tuning | Continuous validation |
| Momentum snowball | Contextual Modifiers | During implementation; test in isolation |
| DLS absurd par scores | DLS implementation | Edge-case testing suite required |
| Synchronous 14-match simulation | API integration | Async from the start |
| N+1 squad queries | Database Schema | Materialized views + eager loading |
| Redis memory bloat | Redis Integration | TTL policies on every key from day 1 |

---

## Key Takeaways

> **The #1 risk is the simulation engine.** If probabilities don't produce "real cricket" results, users reject the product instantly.

> **The #2 risk is salary cap economy.** If every user converges on the same optimal draft, replayability dies.

> **The #3 risk is performance.** 14 synchronous simulations blocking the main thread on mobile will feel broken.

**Build order implication:** Get the simulation engine right in isolation (CLI-testable, batch-runnable, distribution-validated) before building any API or frontend.

---

*Research compiled: 2026-06-11*
*Sources: Academic research on Markov chain cricket models, fantasy sports platform post-mortems, game design feedback loop theory, Redis/FastAPI performance guides, ICC DLS documentation, IPL statistical databases*
