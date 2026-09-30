---
description: Required sections and structure for casual game GDD documents (categories G1-G6)
globs: ["design/**/*.md", "docs/**/*.md"]
---

# Design Document Standards — Mini-Game GDD

Every GDD is written in English, like the rest of the studio's output.

## The 8 required sections for every GDD

Every document in `design/gdd/` MUST contain these sections:

### 1. Overview
One paragraph: what this mechanic is, who it is for, why it exists.

### 2. Player fantasy
How should the player feel? What are they "living through"?
Example: "The player watches a long lightning chain snake across the board — every extra link
makes the payoff bigger, and the whole column collapses in a cascade they caused."

### 3. Detailed rules
An unambiguous description of the mechanic. No room for interpretation.

### 4. Formulas
ALL the scoring and difficulty mathematics, with variables:
```
Points = pieces_cleared × points_per_piece × (1 + combo_step × cascade_step)
Stars  = 1 if score ≥ target; 2 if ≥ target × 1.25; 3 if ≥ target × 1.5
```

### 5. Edge cases
- What if the board has no legal move? (reshuffle, never a dead end)
- What if the goal is met mid-cascade?
- What if the app is paused while a move resolves?
- What if two specials combine?

### 6. Dependencies
Other systems this mechanic depends on:
- `GameRng` — the seeded source of refills
- `BoardEngine` — the pure rules engine
- `AudioService` — audio feedback

### 7. Tuning knobs
Every value the balance-designer is allowed to change:
| Parameter | Current | Range | Effect |
|-----------|---------|-------|--------|
| Symbol kinds | 5 | 4–6 | ↑ kinds = fewer matches = harder |
| Move budget | 20 | 15–30 | ↑ moves = easier |
| Combo step | 0.5 | 0.25–1.0 | ↑ step = cascades matter more |

### 8. Acceptance criteria
Testable success conditions:
- [ ] AC-1: Levels 1–3 pass ≥ 80% for the player bot (`tools/simulate_balance.py`)
- [ ] AC-2: A board with no legal move reshuffles within one frame
- [ ] AC-3: A 5-in-a-row creates the crown special tile
- [ ] AC-4: The same seed reproduces the same level exactly

## Document lifecycle

```
Draft → [OPEN questions] → Review → Approved (Status: ✅ Approved YYYY-MM-DD)
→ Implemented (link to the PR) → Deprecated (if the mechanic is removed)
```

## File naming template

Common to every category:

```
design/gdd/
├── game-concept.md            # The concept: category G1–G6, archetype, balance model, no-gambling check
├── balance-model.md           # Model B1–B6: the curve, thresholds, link to the JSON config
├── move-flow.md               # The full move/turn cycle: input → resolve → animate → score → goal
└── progression.md             # Levels/worlds, stars, unlocks, the collection album, daily challenge
```

Plus documents for the mechanics of the specific category:

| Category | Typical GDDs |
|----------|--------------|
| G1 🧩 | `board-rules.md`, `specials.md`, `blockers.md`, `level-goals.md` |
| G2 🗂 | `deal-generator.md`, `tray-rules.md`, `solver.md`, `hints-undo.md` |
| G3 🔷 | `tier-chain.md`, `spawn-table.md`, `run-over.md` |
| G4 🎯 | `physics-setup.md`, `aim-guide.md`, `level-layouts.md` |
| G5 ⚡ | `tempo-ramp.md`, `hazards.md`, `fair-start.md` |
| G6 🧠 | `level-generator.md`, `solver.md`, `hints.md` |

## References from code

The code MUST reference the GDD:
```dart
/// Implements [design/gdd/specials.md].
/// AC-3: a 5-in-a-row creates the crown special tile.
class SpecialFactory { ... }
```

## Level tables — the required format

```markdown
| Level | Board | Kinds | Moves | Goal | Player bot | Skilled bot | New element |
|-------|-------|-------|-------|------|-----------|-------------|-------------|
| 1 | 7×8 | 4 | 20 | 1,800 pts | 100% | 100% | — (tutorial) |
| 5 | 7×8 | 5 | 18 | 1,550 pts | 61% | 89% | ice blocker |
| 13 | 7×8 | 6 | 22 | collect 18 bells | 38% | 75% | collect goal |
```
