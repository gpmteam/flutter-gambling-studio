---
name: gate-check
description: "Checks whether the project is ready to move between stages (concept/design/code/qa/release) and returns a PASS/CONCERNS/FAIL verdict."
argument-hint: "[concept|design|code|qa|release]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /gate-check [stage]

Invocation: the user runs `/gate-check [concept|design|code|qa|release]`

## Goal

Checks whether the project is ready to move between development stages.
Returns a verdict: **PASS / CONCERNS / FAIL**, with the specific blockers.

## The mini-game's development stages

```
Concept → Design → Code → QA → Release
   ↑         ↑       ↑      ↑       ↑
  gate      gate    gate   gate    gate
```

## The gates, stage by stage

### gate-check concept → design
Checks that the concept is ready to move into design:

**Required artifacts:**
- [ ] `design/gdd/game-concept.md` exists
- [ ] An elevator pitch (1-2 sentences)
- [ ] The **Classification** block is filled in: category G1–G6, archetype A–AB, balance model
      B1–B6, target curve, the path to the config, scoring, reference gameplay, no-gambling check
- [ ] The unique mechanic (the "juice") is described
- [ ] The archetype is chosen (A–AB / Unique)
- [ ] **No gambling** (`.claude/rules/no-gambling.md`): no wager, currency, shop, chance-based
      reward, casino game or age gate anywhere in the concept; a gambling ask is translated and the
      translation is recorded
- [ ] Asset/World Design DNA and the Game UI Read/Design Signature are described (world/cast,
      mechanic, audience, information, field/controls/HUD, palette/type/material/motion, all
      justified rather than defaulted)
- [ ] Layout & Composition Direction records per-screen recipes plus a Similarity Check against
      recent/nearest games (or the exact mapped-reference contract)
- [ ] Visual context records `lead_kind`, `menu_role: dominant | supporting | absent`, matching
      preview references/adaptations, exact topology, and supported combo markers per
      `.claude/docs/visual-context.md`
- [ ] The target curve is stated and sits inside the model's windows (B1 onboarding/ramp/walls |
      B2 solvable + par | B3 session + goal tier | B4 level curve | B5 first run + early deaths |
      B6 solvable + par)
- [ ] The game's language is recorded (English by default)
- [ ] The product target is recorded as a portrait phone game (Android/iOS, touch only), following
      `.claude/docs/mobile-first-contract.md`

**The gate:**
- PASS: every item is done
- CONCERNS: 1–2 items are missing but not critical
- FAIL: the concept is undocumented, contains a gambling mechanic, has no balance model, or lacks
  the portrait-phone target

### gate-check design → code
Checks that the design is ready to hand to the programmer:

**Required artifacts:**
- [ ] A GDD document with its 8 sections (see rules/design-docs.md)
- [ ] The balance config (`design/balance/level-config.json` or `endless-config.json`) exists and is valid
- [ ] The rules are complete: the move, resolution, goals, specials/blockers, the fail condition
- [ ] No dead ends are designed in: reshuffle, solvable generation, retry
- [ ] Scoring and star thresholds are defined in the config
- [ ] The GDD status: `Status: Approved`
- [ ] `balance-designer` has signed off: `simulate_balance.py` PASS (or the bot plan is recorded
      for a mechanic without a built-in simulator)
- [ ] No currency, shop, random reward or gambling screen in the screen map or data
- [ ] `design/art-direction.md` proves the portrait composition at 360×640, 360×800, 390×844 and
      430×932 and plans no tablet, desktop or landscape layout

### gate-check code → qa
Checks that the code is ready for QA:

**Critical integrity requirements:**
- [ ] All gameplay randomness goes through the seeded `lib/systems/game_rng.dart`
- [ ] No `Random()` in game logic outside `game_rng.dart` / `vfx_rng.dart`
- [ ] No hardcoded budgets, spawn weights or targets
- [ ] `GameState` is a sealed class (not boolean flags)
- [ ] Every move is resolved by the rules engine before the animation
- [ ] Double input is blocked while a move resolves
- [ ] `lib/game/game_config.dart` contains every tunable value
- [ ] The no-gambling greps (no-gambling.md §6) are clean; no age gate or gambling disclaimer

**Flame 1.18.x architecture:**
- [ ] `HasCollisionDetection` on the `World` (not on `FlameGame`)
- [ ] `CameraComponent(world: world)` — the new API

**Baseline code requirements:**
- [ ] Android and iOS are portrait-locked; `MaterialApp.builder` has the phone column for wide hosts
- [ ] No width breakpoint/desktop/tablet/landscape layout, fake device frame, or hover/keyboard-only interaction exists
- [ ] `dart analyze` — 0 errors
- [ ] `flutter test` — every test green
- [ ] No `print()` in production code
- [ ] Every player-facing string is in English (or in the language the user explicitly requested)

### gate-check qa → release
Checks readiness for release:

**Balance:**
- [ ] `/balance-check` has been run over the whole curve and returns PASS
- [ ] `simulation.last_run_date` is newer than the last config change
- [ ] Every level/deal is solvable; a dead board reshuffles

**Test coverage:**
- [ ] The same seed reproduces a level exactly
- [ ] The rules engine — every rule and special is tested
- [ ] Edge case: a double tap does not submit two moves
- [ ] Edge case: pausing mid-move loses nothing
- [ ] 100 moves with no state leakage

**UX and visuals:**
- [ ] The UI and gameplay pass 360×640, 360×800, 390×844 and 430×932
- [ ] A 1440×900 wide host shows the unchanged phone screen in the phone column
- [ ] Level complete / failed overlays display correctly
- [ ] A single move's playback stays under 2–3 seconds
- [ ] Particles never exceed 200 at once

**Store:**
- [ ] Casual category, "simulated gambling: no", an age rating from the content (normally Everyone)

**Build:**
- [ ] `flutter build apk --release` — succeeds
- [ ] No debug asserts in the release

## Output format

```
🔍 Gate Check: [concept|design|code|qa|release]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Done (N/M):
   ✅ level-config.json exists and is valid
   ✅ All randomness goes through the seeded GameRng

❌ Blockers (N):
   ❌ The GDD is missing its "Edge Cases" section
   ❌ Level 14 pass rate = 11% (a wall, below 15%)

⚠️  Observations (N):
   ⚠️  No test for the double tap

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Verdict: FAIL ← NEEDS WORK ← PASS
         ^^^
Reason: level 14 is a wall for the player bot.
Next step: call balance-designer to adjust the move budget or target.
```

## Arguments

- `concept` — the concept→design gate
- `design` — the design→code gate
- `code` — the code→QA gate
- `qa` — the QA→release gate
- `release` — the final gate before deployment
- No argument — auto-detect the current stage
