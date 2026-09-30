---
name: code-review
description: "A comprehensive code review of the mini-game: architecture, game integrity, the Flame API, tests and risks."
argument-hint: "[path or area]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /code-review

Invocation: the user runs `/code-review [path or area]`

## Goal

A comprehensive code review of the mini-game. It checks:
- The casual-game critical requirements (RNG, state integrity)
- The Flame 1.18.x architecture (correct API usage)
- Code quality (patterns, readability, tests)
- The no-gambling gate, seeded gameplay randomness and config-driven difficulty
- Performance (no allocations in update/render)

## Agents

- `lead-programmer` — architecture, patterns, Dart quality
- `mechanics-programmer` — casual rules, deterministic RNG, the Flame API
- `qa-tester` — test coverage, edge cases

## Order of work

### Step 1: determine the review scope

If a path is given (for example `lib/systems/game_rng.dart`), review that file.
If not, review the whole `lib/` directory.

### Step 2: lead-programmer — the architectural review

The `lead-programmer` agent checks:

**Project structure:**
- [ ] `lib/game/game_config.dart` exists and contains the canonical JSON-backed tuning values
- [ ] `lib/systems/game_rng.dart` uses `Random(seed)`
- [ ] `lib/models/game_state.dart` contains a sealed class
- [ ] No business logic in `screens/` (UI only)
- [ ] No `BuildContext` in Flame components

**Portrait phone target:**
- [ ] The four portrait phones pass; no screen branches on width to another layout (no desktop,
      tablet, landscape, side-rail or split-pane code)
- [ ] Portrait lock in `main()`, the Android manifest and the iOS plist
- [ ] Touch is the only required input: nothing needs hover, a tooltip or a keyboard
- [ ] `MaterialApp.builder` wraps the app in the phone column; a wide host shows the phone screen
      over the background surround, not stretched and not framed

**Dart patterns:**
- [ ] No `dynamic` outside JSON boundaries
- [ ] No `print()` in production code
- [ ] No `await` in `update()` / `render()`
- [ ] `final` is used wherever possible
- [ ] No magic numbers outside GameConfig

**The Flame 1.18.x API:**
- [ ] `HasCollisionDetection` on the `World`, not on `FlameGame`
- [ ] `CameraComponent(world: world)` — the new API
- [ ] No `isPaused = true` — `GameState` is used
- [ ] Pre-initialised Vector2/Rect/Paint in `update()`

### Step 3: mechanics-programmer — game integrity

The `mechanics-programmer` agent checks:

**Critical requirements:**
- [ ] `.claude/rules/no-gambling.md` holds: no wagers (even with points), currencies, shops,
      chance-based rewards, casino games or controls; scores are never spent.
- [ ] Gameplay uses one seeded `GameRng`; cosmetic randomness is separate.
- [ ] A move resolves in the pure rules engine BEFORE animation; scoring is committed once.
- [ ] Inputs cannot start overlapping actions; budgets, timers and stars stay valid.
- [ ] New game, retry, pause and resume do not leak state; save recovery preserves progress.
- [ ] Dead boards reshuffle, deals/logic levels are solvable, physics bodies are bounded.

**Balance and configuration:**
- [ ] G1–G6 category and B1–B6 model agree with the mechanic.
- [ ] Budgets, goals, spawn tables and tempo ramps load from `design/balance/*.json`.
- [ ] Scoring/combos/stars are pure and exact; no duplicate JSON/Dart tuning values.
- [ ] The complete curve passed `tools/simulate_balance.py`; unsupported mechanics have a
      headless bot report from the actual game engine.

### Step 4: qa-tester — test coverage

- [ ] Same seed and moves produce the same board/deal/spawns and score.
- [ ] Rules, scoring, terminal states, invalid moves, double input, pause and retry are tested.
- [ ] The category's dead-end/solver/body-cap checks are covered.
- [ ] Save/progression and deterministic achievement claims survive restart.
- [ ] `game_screen_layout_test.dart` covers 360×640, 360×800, 390×844, 430×932 and the
      1440×900 phone-column check.
- [ ] Tests exercise behavior with meaningful assertions and do not mirror implementation.

### Step 5: producing the report

Create `docs/review-YYYY-MM-DD.md` with this structure:

```markdown
# Code Review — [date]
## Scope: [path or "the whole project"]

## 🚨 CRITICAL PROBLEMS (they block the release)
- The list of critical findings

## ⚠️ IMPORTANT OBSERVATIONS (they need fixing)
- The list of important problems

## 💡 RECOMMENDATIONS (improvements)
- The list of recommendations

## ✅ WELL DONE
- The list of what was done right

## Summary
- Status: APPROVED / NEEDS WORK / BLOCKED
- Next steps: [the list of actions]
```

## Arguments

- No arguments: a full review of `lib/`
- `lib/systems/` — review systems only
- `lib/game/` — review the game layer
- `--quick` — only the critical integrity checks (RNG, move resolution, config), no architecture
- `--rng` — gameplay RNG determinism only

## Tools

```
Read, Glob, Grep, Bash(grep*), Bash(dart analyze*)
```

## Example output

```
Review: NEEDS WORK
- Critical: a retry keeps the previous attempt's move counter.
- Important: the last world has no headless bot report.
- Verified: seeded board replay and points-only scoring.
Report saved: docs/review-2026-03-24.md
```
