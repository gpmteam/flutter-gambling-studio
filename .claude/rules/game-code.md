---
description: Casual game Dart/Flame code rules — no gambling, logic before animation, one seeded GameRng, balance-model config, state integrity, forbidden patterns. Unconditional across all six categories.
globs: ["lib/**/*.dart"]
---

# Game Code Rules — casual games

## CRITICAL RULES (violation = PR blocked)

> These apply to all six categories G1–G6, without exception.

### No gambling in the code

- No wager, stake, bet-size, cash-out or "risk it" code paths.
- No currency: no `balance`, `wallet`, `coins`, `chips`, `gems` or `credits` that are earned, held,
  spent or bought; no prices, no shop, no insufficient-funds state.
- No chance-based rewards: rewards are deterministic consequences of play (a level cleared, a
  milestone reached, a combo made).
- Points are a score — counted, displayed, compared with the best; never spent.
- See `.claude/rules/no-gambling.md`.

### GameConfig — the single source of game constants

- ALL game constants live in `lib/game/game_config.dart`
- Board sizes, move/time budgets, tempo ramps, spawn tables, scoring, timings, limits — only from
  the config
- The balance model's numbers live in JSON (`design/balance/*.json`, level data under
  `assets/data/`) and are loaded into the config/level objects; they are never re-typed by hand in
  two places
- Numeric literals for gameplay values outside the config are not allowed

```dart
// ✅ CORRECT
class GameConfig {
  static const int boardCols = 7;
  static const int boardRows = 8;
  static const int pointsPerPiece = 10;
  static const double comboStep = 0.5;
  static const int maxParticles = 200;
  static const Duration cascadeStep = Duration(milliseconds: 180);
}

// ❌ FORBIDDEN
if (score > 1000) {            // Where did 1000 come from?
  triggerParticles(count: 50); // And 50?
}
```

### GameState — a sealed class is mandatory
- Use a sealed class for every game/level state
- No boolean flags (`isResolving`, `isPaused`, `isGameOver`)
- Each state carries its own data, including the already-resolved move

```dart
sealed class GameState {}
class ReadyState extends GameState {}
/// The move is already resolved — the animation only plays it back.
class ResolvingState extends GameState { final MoveResult result; }
class LevelClearedState extends GameState { final int score; final int stars; }
class LevelFailedState extends GameState { final int score; final FailReason reason; }
class PausedState extends GameState { final GameState previousState; }
```

### Protect input while a move resolves
- The primary action (and direct manipulation of the field) is locked while a move resolves
- A debounce of at least 300 ms on the primary action button

### Logic before animation
- A move is resolved by the **pure rules engine** BEFORE any animation starts: matches, cascades,
  merges, collisions (for physics: the simulation step), score and goal progress
- The animation only "plays back" the resolved steps
- The rules engine has no Flutter/Flame imports, no timers and no rendering; it is what the tests
  and the balance bot (`test/balance/bot_sim_test.dart`) drive

## RANDOMNESS

> Unconditional rules: they apply to ALL categories G1–G6.

### One seeded `GameRng`
- ALL gameplay randomness — board fills and refills, deals, spawn order, the next piece, level
  generation — goes through ONE injectable `GameRng` wrapping `Random(seed)`
- The seed is chosen per level/run (a level's fixed seed, a random seed for endless runs, the date
  for the daily challenge) and recorded, so a level reproduces exactly in the game, the tests and
  the bot
- **NEVER** call `Random()` / `math.Random()` directly in game logic
- **NEVER** use randomness to decide whether a move "wins" or to grant a reward
- Purely cosmetic randomness (particle scatter, idle phases) uses a separate `VfxRng`, so visual
  effects never shift the gameplay sequence
- Weights (spawn tables, symbol mixes) are read from the config, never hardcoded

```dart
// ✅ CORRECT
/// The only source of gameplay randomness. Seeded so a level reproduces exactly.
/// See design/balance/level-config.json and .claude/rules/game-code.md.
class GameRng {
  GameRng(this.seed) : _random = Random(seed);
  final int seed;
  final Random _random;

  int nextKind(int kinds) => _random.nextInt(kinds);

  int weighted(List<int> weights) {
    final total = weights.reduce((a, b) => a + b);
    var roll = _random.nextInt(total);
    for (var i = 0; i < weights.length; i++) {
      roll -= weights[i];
      if (roll < 0) return i;
    }
    return weights.length - 1;
  }
}

// ❌ FORBIDDEN
final rng = Random();                                // Unseeded, scattered
if (Random().nextDouble() < 0.15) awardBooster();    // A chance-based reward
```

### The balance model's target windows

The windows depend on the game's category — the full table is in `.claude/docs/balance-models.md`:

| Category | Model | Target window |
|----------|-------|---------------|
| G1 | B1 | L1–3 ≥ 80% pass, no wall < 15%, ramp ≥ 15 pp |
| G2 | B2 | 100% of shipped deals solvable, par ramps ≤ 2× per step |
| G3 | B3 | median session 2–12 min, goal tier reachable 2–70% |
| G4 | B4 | the level-curve windows from the game's physics bot |
| G5 | B5 | median first run 30–180 s, ≤ 10% of runs end in 10 s |
| G6 | B6 | every level solvable, par ramps, the level-curve windows |

- If `/balance-check` returns FAIL, production stops.
- Only `balance-designer` changes the model's numbers, and only in the JSON config.
- Changing a target window requires an ADR, not a silent edit.

## FORBIDDEN PATTERNS

1. **`isPaused = true`** — use the `GameState` sealed class
2. **`BuildContext` in Flame components** — use callbacks or a service locator
3. **`print()` in production code** — use `Logger`
4. **`await` in `update()` or `render()`** — these methods MUST be synchronous
5. **Object allocation in `update()`** — pre-initialise Vector2, Rect, Paint
6. **`Random()` / `math.Random()` in game logic** — only the seeded `GameRng` (cosmetics: `VfxRng`)
7. **Hardcoded gameplay parameters** outside GameConfig
8. **Changing state during an animation** — check the GameState
9. **Resolving a move inside the animation** — breaks logic-before-animation and the bot simulation
10. **Duplicating the model's numbers** in JSON and in Dart — one source of truth
11. **Any wager, currency or chance-based reward** — see no-gambling.md
12. **A dead end** — a board with no move must reshuffle; a failed level offers retry
13. **Player-facing copy in a language other than English**, unless the user explicitly asked
    for a different language — see CLAUDE.md → Language

## REQUIRED ARCHITECTURE

```
lib/
├── game/
│   ├── [game_name]_game.dart   # extends FlameGame — the entry point
│   ├── [game_name]_world.dart  # extends World with HasCollisionDetection
│   └── game_config.dart        # ONLY constants, no logic
├── systems/
│   ├── game_rng.dart           # the one seeded source of gameplay randomness
│   ├── [rules]_engine.dart     # the pure rules engine: resolves a move BEFORE the animation
│   └── scoring.dart            # a pure scoring function (points, combos, stars)
├── models/
│   └── game_state.dart         # sealed class
```
