# Feature Landscape — 14-0 IPL Draft & Simulation Platform

> Research document covering feature analysis, competitor benchmarking, and MVP scoping for the 14-0 platform.

**Research Date**: 2026-06-11
**Sources**: 38-0/82-0/20-0 draft simulators, Dream11, MPL, fantasy cricket platforms, cricket simulation engine research, IPL rules documentation
**Status**: Complete

---

## 1. Table Stakes (Users Expect These)

Features that any draft-simulate game in this genre **must** have to feel complete. Absence of any of these would feel like a bug.

### 1.1 Spin / Draft Mechanic with Visual Flair

| Aspect | Requirement | Notes |
|--------|-------------|-------|
| Slot-machine spin animation | Randomized visual "reel" showing team logos + years cycling | The 38-0 hook — this is the first thing users see |
| Team + Era reveal | Display franchise name, year, and team crest on landing | e.g., "2016 Royal Challengers Bangalore" |
| Player roster presentation | Show the era's full roster with roles and ratings | Users pick ONE player per spin |
| Re-spin / skip mechanic | Limited re-rolls (0–3 per session) to skip undesirable eras | Too many re-rolls kills difficulty; too few feels punishing |
| Sound design | Satisfying spin SFX + landing chime | Critical for dopamine loop — 38-0's virality depends on this |

### 1.2 Roster Builder with Constraint Validation

| Constraint | Rule | IPL Basis |
|------------|------|-----------|
| Squad size | Exactly 11 players | Standard XI |
| Salary cap | 100 credits total | Mirrors 38-0/Dream11 budget economy |
| Wicketkeeper | Exactly 1 WK required | IPL regulations |
| Bowlers | Minimum 3 specialist bowlers | Match balance requirement |
| Overseas players | Maximum 4 in playing XI | IPL overseas cap |
| Role balance | Min 1 all-rounder recommended (soft constraint) | Gameplay balance |

**UX Requirements**:
- Real-time constraint validation with visual indicators (green/red)
- Running salary counter showing remaining credits
- Position slots visualization (filled vs. empty)
- "Team sheet" preview showing batting order and bowling options

### 1.3 Match Simulation with Ball-by-Ball Results

| Component | Description |
|-----------|-------------|
| Ball-by-ball output | Discrete events per delivery: 0, 1, 2, 3, 4, 6, Wicket, Wide, No Ball |
| Innings structure | 20 overs per innings, 6 legal deliveries per over |
| Batting order progression | Next batter enters on wicket fall; follows user's batting order |
| Bowling rotation | Bowlers limited to 4 overs each; auto-rotation logic needed |
| Over-by-over summary | Condensed view showing runs per over, key events |
| Full scorecard | Post-match detailed scorecard (batters, bowlers, extras, FOW) |

### 1.4 Score Display with Cricket-Specific Formatting

| Element | Format | Priority |
|---------|--------|----------|
| Team score | `150/3` (runs/wickets) | Primary — largest visual element |
| Overs bowled | `12.4 ov` (decimal notation, NOT 12:4) | Primary |
| Current Run Rate (CRR) | `7.50` (runs per over) | Secondary |
| Required Run Rate (RRR) | `9.25` (2nd innings chase only) | Secondary |
| Current batters | Name + runs(balls) with strike indicator | Secondary |
| Current bowler | Name + figures (overs-maidens-runs-wickets) | Secondary |
| Target | `Target: 180` (2nd innings only) | Tertiary |
| Extras | `Extras: 12 (wd 5, nb 3, b 2, lb 2)` | Tertiary |

**Design Principles** (from broadcast UI research):
- "Scorebug" philosophy: compact, <10% screen real estate
- High-contrast: dark background (navy/charcoal) + bright text (white/yellow)
- Visual hierarchy: Score → Overs → Batters → Run Rate → Target
- Mobile-first: vertical stacking on small viewports

### 1.5 Player Cards with Ratings and Stats

| Attribute | Type | Description |
|-----------|------|-------------|
| Player name + photo placeholder | Identity | Name, nationality flag, franchise badge |
| Overall rating | 0–99 scale | Composite rating (FIFA-style) |
| Role badge | Enum | BAT / BOWL / AR / WK |
| Batting stats | Numeric | Batting average, strike rate, boundary % |
| Bowling stats | Numeric | Bowling economy, bowling strike rate, dot ball % |
| Credit cost | Numeric | Cost against 100-credit salary cap |
| Era tag | Label | Year + franchise of historical appearance |
| Rarity tier | Visual | Based on overall rating (Bronze/Silver/Gold/Diamond) |

### 1.6 Session Result Screen

| Scenario | Display |
|----------|---------|
| 14-0 achieved | Full celebration screen — confetti, "PERFECT SEASON" banner, final XI showcase |
| First loss | "Your run ended at X-1" — show the match that broke the streak |
| Season summary | W/L record, total runs scored/conceded, best player performance |
| Share card | Shareable image/screenshot with team + record (critical for virality) |
| Replay prompt | "Try again?" button with new spin immediately available |

---

## 2. Differentiators (Competitive Advantage)

Features that set 14-0 apart from both the 38-0 family AND fantasy cricket platforms.

### 2.1 Historical Era Spin Mechanic (The Viral Hook)

**What makes this different from 38-0**:
- Cricket has **deeper roster complexity** than football (11 positions with distinct role constraints vs. 4 position groups)
- IPL spans 2008–present with **dramatic franchise transformations** (e.g., CSK 2011 vs. CSK 2023 are fundamentally different squads)
- Era-specific meta: 2008 IPL was bowling-dominated; 2023+ is boundary-heavy
- **No cricket equivalent exists** — 38-0 has spawned basketball (82-0), NFL (20-0), World Cup (7-0), but NO cricket/IPL version

### 2.2 Momentum Multiplier System

**Concept**: After a boundary from a high-variance batter, suppress wicket probability for N subsequent deliveries.

**Technical Implementation**:
- Track consecutive boundary events per batter
- Apply multiplier to transition matrix: reduce P(wicket) by factor M for next K deliveries
- M and K calibrated from historical IPL data
- Inverse: after a dot ball sequence, increase P(wicket) slightly (pressure building)
- Higher-order Markov chain: outcome depends on last N balls, not just current state

### 2.3 Impact Player Rule Integration

**IPL Rule (since 2023)**:
- Teams name 5 substitutes pre-match
- One substitute can replace one starting XI player during the match
- Substitution allowed at: start of innings, fall of wicket, or end of over
- Replaced player cannot participate further

### 2.4 DLS Weather Interruption Randomness

**DLS Implementation**:
- Resource table: percentage value for every (overs remaining × wickets lost) combination
- Par score = Team 1's Score × (Team 2's Resources / Team 1's Resources)
- Random interruption probability: ~10-15% chance per match
- Minimum overs rule: Don't trigger before over 6

### 2.5 Ball-by-Ball Markov Chain Simulation (Not Simplified)

| Approach | How it works | Problem |
|----------|-------------|---------|
| Over-by-over | Generate runs per over from a distribution | Loses granularity |
| Simple RNG | Random outcome per ball with flat probabilities | Feels arbitrary |
| **Markov Chain** | **State-dependent transition matrix per ball** | **Produces organic, believable results** |

---

## 3. Anti-Features (Commonly Requested but Problematic)

### 3.1 Real-Money Gambling / Entry Fees

| Concern | Detail |
|---------|--------|
| Regulatory landscape | India's Online Gaming Act (2025) has made real-money gaming extremely complex |
| Classification risk | Markov chain simulation with random elements could be classified as gambling |
| **Decision**: Defer indefinitely | Free-to-play only |

### 3.2 Live Commentary / Text Generation

| Concern | Detail |
|---------|--------|
| Scope creep | Generating natural-language commentary is essentially a separate NLG system |
| Alternative | Simple event labels ("FOUR!", "WICKET!") are sufficient |
| **Decision**: Out of scope for v1 | Use templated event labels |

### 3.3 Full IPL Auction Mechanics

| Concern | Detail |
|---------|--------|
| Session length | Even simplified, auctions take 20-30 minutes |
| Core value conflict | 14-0's value proposition is "complete loop in ~5 minutes" |
| **Decision**: Spin-draft only for MVP | The spin mechanic IS the hook |

### 3.4 Multiplayer Draft Lobbies

| Concern | Detail |
|---------|--------|
| Infrastructure | WebSocket management, matchmaking, lobby persistence |
| MVP risk | Multiplayer requires critical mass of concurrent users |
| **Decision**: v2 feature | Prove single-player loop first |

---

## 4. Feature Dependencies (Build Order)

```
Phase 1: Data Foundation
├── Historical player dataset schema (CSV/JSON)
├── Player rating calculation system
└── Seed data for testing (10-20 team-years)

Phase 2: Core Engine
├── Markov chain probability engine
│   ├── Base transition matrix construction
│   ├── Batter × Bowler matchup matrices
│   └── Contextual modifier system
├── Ball-by-ball simulation loop
└── Match result calculation

Phase 3: Draft System
├── Spin mechanic (random team+era selection)
├── Player selection from roster
├── Constraint validation engine
└── Draft state persistence

Phase 4: Game Loop
├── 14-match league generation
├── Session flow (spin→draft→simulate→result)
└── Result screen + share card

Phase 5: Advanced Mechanics
├── Momentum multiplier system
├── Impact Player substitution logic
├── DLS weather interruption
└── Difficulty modes (Classic vs. Blind)

Phase 6: Polish & UI
├── Spin animation (slot machine visual)
├── Scorecard display (cricket formatting)
├── Player card design
├── Mobile-responsive layout
└── Sound design
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 (MVP)

---

## 5. MVP Definition

### v1.0 — Minimum Viable Product ("Prove the Loop")

| Feature | Included | Notes |
|---------|----------|-------|
| Spin mechanic | ✅ | Random team+era, basic animation |
| Player roster display | ✅ | Cards with ratings, role, cost |
| Draft with constraints | ✅ | 11-player XI, salary cap, role rules |
| Ball-by-ball simulation | ✅ | Markov chain engine, basic modifiers |
| 14-match PvE league | ✅ | AI opponents, season result |
| Result screen | ✅ | Win/loss record, 14-0 achievement |
| Share card | ✅ | Static image for social sharing |
| Mobile-first UI | ✅ | Responsive, cricket-formatted scores |
| Impact Player | ❌ | Defer to v1.x |
| DLS interruptions | ❌ | Defer to v1.x |
| Momentum multiplier | ❌ | Defer to v1.x |

### v1.x — Feature Complete ("Depth & Replay Value")

- v1.1: Momentum multiplier
- v1.2: Impact Player (12th man draft) + DLS weather
- v1.3: Blind/Knowledge mode + Sound design
- v1.4: Difficulty tiers + Season statistics

### v2.0+ — Scale ("Social & Competitive")

- User authentication + profiles
- Multiplayer draft lobbies
- Leaderboards
- Cosmetic monetization

---

## 6. Competitor Analysis

### 6.1 Market Gap Analysis

```
                    REAL OUTCOMES          SIMULATED OUTCOMES
                    ─────────────          ──────────────────
SLOW PLAY           Dream11, My11Circle    Full cricket
(hours/days)        MPL, SportsBaazi       management sims
                    
QUICK PLAY          [2nd Innings Fantasy]  ← 14-0 GOES HERE
(~5 minutes)                               (no competitor)
```

**The gap**: No product combines quick-play session design with simulated cricket outcomes. 14-0 occupies the **quick-play simulation** quadrant that the 38-0 family proved is viral for other sports but nobody has built for cricket.

---

*Feature research for: IPL Draft & Simulation Platform*
*Researched: 2026-06-11*
