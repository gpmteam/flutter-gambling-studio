---
name: map-systems
description: "Decomposes a casual game concept into technical systems. Builds a dependency graph and an implementation plan for the programmer, working from the category G1-G6 and the balance model B1-B6."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
---

# `map-systems` — the game build plan

Breaks the game from `design/gdd/game-concept.md` down into structural components for Flame.

## Behaviour

Do not ask the user anything. Read the concept (the **Classification** block), determine the
category and the balance model, and generate `design/gdd/systems-map.md`.

## Output template

```markdown
# Systems map: [Game name]

**Category**: [G1-G6] — [name]
**Archetype**: [A-AB]
**Balance model**: [B1-B6] → `design/balance/[file].json`

## 1. Core logic
- `GameConfig` (every tuning knob; the model's numbers are loaded from JSON, never duplicated)
- `GameState` (sealed class: Ready / Resolving / Paused / LevelCleared / LevelFailed)
- `GameRng` (`Random(seed)` — the ONLY source of gameplay randomness; `VfxRng` for cosmetics)
- `[Rules]Engine` (the pure rules engine: resolves a move BEFORE the animation)
- `Scoring` (a pure function: points, combos, stars)

## 2. Flame components (presentation)
- `[MainComponent]` (board / tile pile / merge grid / peg field / lanes / logic grid)
- `[ElementComponent]` (tiles, pieces, balls, hazards)
- `ComboFeedbackComponent` (VFX scaled to what the player earned)
- `AmbientParticles` (optional, only if the Design Signature calls for it)

## 3. Flutter UI
- `GameScreen` (full-screen portrait composition from
  `.claude/docs/mobile-first-contract.md` and `.claude/docs/gameplay-screen-contract.md`;
  touch only, one composition for every phone, no nested window or core-loop scrolling)
- `HudWidget` (score, goal, moves/time through a ValueNotifier)
- `ActionButton` (a 300 ms debounce + disabled/pressed states + ≥48 wide/56 high primary target)
- Stable layout keys: `gameplaySurface`, `primaryAction`, and `controlDeck` for geometry tests
- `MainMenuScreen`, `LevelMapScreen`, `LevelComplete`/`LevelFailed`, every MVP screen

## 4. Meta & audio
- `SaveService`, `ProgressionService`, `AchievementService`, `CollectionService`,
  `DailyChallengeService` (no currency, no shop, no random rewards)
- `AudioService` (at most 3 concurrent sounds)

## Development order (the plan)
1. The balance model → `/design-system [system]` → `/balance-check`
2. Core logic (GameRng + rules engine + scoring) → `/design-system`
3. Flame components → `/prototype [mechanic]`
4. Flutter UI (every screen)
5. Meta systems and content
6. Integration → `/balance-check` → `/ui-audit` → testing
```

## Key systems by category

| Category | The mechanic's core |
|----------|---------------------|
| **G1** 🧩 | `BoardEngine` (match, gravity, refill, cascades, specials, reshuffle) + `BoardComponent` + `TileComponent` |
| **G2** 🗂 | `DealGenerator` + `DealSolver` + `TrayRules` + `UndoStack` + `TilePileComponent` |
| **G3** 🔷 | `MergeEngine` + `SpawnTable` + `RunOverDetector` + `MergeBoardComponent` |
| **G4** 🎯 | `PhysicsWorld` (fixed timestep) + `AimGuide` + `TargetTracker` + `BodyLimiter` |
| **G5** ⚡ | `TempoRamp` + `HazardSpawner` + `CollisionJudge` + `PlayerComponent` |
| **G6** 🧠 | `LevelGenerator` + `LevelSolver` + `HintService` + `LogicBoardComponent` |

The document must include the `Development order` section and the list of classes.
