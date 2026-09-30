# Coding standards — Flutter Game Studio

All production standards are specialised for mini-games on Flame 1.18.x.

---

## 1. Dart style guide

### Import order

```dart
// 1. dart: SDK (alphabetical)
import 'dart:async';
import 'dart:math';

// 2. package: (alphabetical)
import 'package:flame/components.dart';
import 'package:flutter/material.dart';
import 'package:my_game/game/game_config.dart';

// 3. Relative (inside the package only)
import '../components/board_component.dart';
```

### Class file — member order

1. Static constants and fields
2. Instance fields (`final` before mutable, public before private)
3. Constructors
4. Static methods
5. Lifecycle methods (onLoad → onMount → update → render → onRemove)
6. Public methods (alphabetical)
7. Private methods (alphabetical)

### `final` vs `var` vs `const`

| Keyword | When to use it |
|---------|----------------|
| `const` | Compile-time constants — always preferred |
| `final` | Assigned once at runtime — the default for fields and locals |
| `var` | Only when the variable is reassigned — requires a comment explaining why |

### Null safety

- No bare `!` without an inline comment explaining why the value is guaranteed non-null
- Prefer `??` for default values
- Use pattern matching for complex null checks
- `late final` only when initialisation cannot happen in the constructor

---

## 2. Flame component standards

### The required lifecycle method order

```dart
class BoardComponent extends PositionComponent with HasGameRef<BoardGame> {
  // Fields
  final _tempPos = Vector2.zero(); // Pre-initialised!

  // Constructor

  @override
  Future<void> onLoad() async { ... }

  @override
  void onMount() { ... }

  @override
  void onGameResize(Vector2 size) {
    if (!isMounted) return; // The check is mandatory!
    super.onGameResize(size);
  }

  @override
  void update(double dt) { ... } // SYNCHRONOUS only!

  @override
  void render(Canvas canvas) { ... } // SYNCHRONOUS only!

  @override
  void onRemove() { ... }
}
```

### No allocation in the hot path

```dart
// ❌ Creates objects every frame — FORBIDDEN
void update(double dt) {
  position = Vector2(x, y + dropOffset); // allocation!
  final paint = Paint()..color = Colors.red; // allocation!
}

// ✅ Pre-initialised
final _tempPos = Vector2.zero();
late final Paint _tilePaint;

@override
Future<void> onLoad() async {
  _tilePaint = Paint()..color = Colors.amber;
}

@override
void update(double dt) {
  _tempPos.setValues(x, y + dropOffset);
  position.setFrom(_tempPos);
}
```

### Component limits

- Maximum lines in a component: 300 — otherwise decompose it
- Maximum direct children in onLoad: 10
- Maximum constructor parameters: 8 (otherwise use a config data class)
- Maximum inheritance depth: 3 below Component

---

## 3. Game-specific standards

### GameRng — the single seeded source of gameplay randomness

```dart
/// The only source of gameplay randomness (fills, deals, spawns, level generation).
/// Seeded so a level reproduces exactly in the game, the tests and the balance bot.
/// See .claude/rules/game-code.md.
class GameRng {
  GameRng(this.seed) : _random = Random(seed);

  final int seed;
  final Random _random;

  /// Picks a symbol kind using the level's spawn weights from GameConfig/level data.
  int pickKind(List<int> weights) {
    assert(weights.isNotEmpty);
    final total = weights.reduce((a, b) => a + b);
    var roll = _random.nextInt(total);
    for (var i = 0; i < weights.length; i++) {
      roll -= weights[i];
      if (roll < 0) return i;
    }
    return weights.length - 1;
  }
}
```

### MatchFinder — a pure function

```dart
/// Finds every run of 3+ identical kinds on a board.
/// Pure function — no side effects, no state, no randomness.
/// See design/gdd/board-rules.md, AC-1 through AC-5.
class MatchFinder {
  /// [cells] is row-major, [cols] wide; returns the indexes to clear.
  static Set<int> find(List<int> cells, int cols) {
    // Pure logic, no RNG, no state
  }
}
```

### GameState — a sealed class is mandatory

```dart
/// Represents all possible states of a level.
/// Transitions: Ready → Resolving → Ready | Cleared | Failed
///              Ready → Paused → Ready
sealed class GameState {
  const GameState();
}

final class ReadyState extends GameState { const ReadyState(); }
final class ResolvingState extends GameState {
  const ResolvingState({required this.result});
  final MoveResult result; // The move is resolved BEFORE the animation!
}
final class ClearedState extends GameState {
  const ClearedState({required this.score, required this.stars});
  final int score;
  final int stars;
}
final class FailedState extends GameState {
  const FailedState({required this.score});
  final int score;
}
final class PausedState extends GameState {
  const PausedState({required this.previous});
  final GameState previous;
}
```

---

## 4. Flutter UI standards (HUD / screens)

### Separating state

```dart
// ✅ Correct — the HUD only reads
class HudWidget extends StatelessWidget {
  final ValueNotifier<int> score;        // From BoardGame
  final ValueNotifier<int> movesLeft;    // From BoardGame
  final ValueNotifier<bool> isResolving; // From BoardGame

  const HudWidget({
    required this.score,
    required this.movesLeft,
    required this.isResolving,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<int>(
      valueListenable: score,
      builder: (context, points, _) => Text('$points', style: ...),
    );
  }
}
```

### Primary action — double-tap protection

```dart
class PlayButtonWidget extends StatefulWidget {
  final VoidCallback onPlay;
  final ValueNotifier<bool> isResolving;

  @override
  State<PlayButtonWidget> createState() => _PlayButtonWidgetState();
}

class _PlayButtonWidgetState extends State<PlayButtonWidget> {
  final _sinceTap = Stopwatch();

  void _handleTap() {
    if (_sinceTap.isRunning &&
        _sinceTap.elapsed < const Duration(milliseconds: 300)) {
      return; // Debounce
    }
    _sinceTap
      ..reset()
      ..start();
    if (!widget.isResolving.value) {
      widget.onPlay();
    }
  }
}
```

---

## 5. Audio standards

### AudioService — at most 3 concurrent

```dart
/// Manages game audio — max 3 concurrent sounds: BGM + Action + Effect.
/// See .claude/docs/technical-preferences.md for audio spec.
class AudioService {
  static const int maxConcurrent = 3;

  AudioPlayer? _bgmPlayer;

  /// Opt-in: games ship SFX-only by default, so this is a no-op unless a BGM
  /// asset was generated. Keep the method and the Settings toggle regardless —
  /// see .claude/agents/sound-designer.md → "Music is opt-in".
  Future<void> startBgm() async {
    await _bgmPlayer?.stop();
    _bgmPlayer = await FlameAudio.loopLongAudio('audio/bgm/bgm_main.wav', volume: 0.7);
  }

  Future<void> playMatch(int cascadeStep) =>
      FlameAudio.play('audio/sfx/sfx_score.wav', volume: (0.7 + cascadeStep * 0.1).clamp(0, 1));

  Future<void> playClear() => FlameAudio.play('audio/sfx/sfx_win_big.wav');
}
```

---

## 6. Error handling

```dart
// ✅ Always name the exception type
try {
  await loadLevelData();
} on FileSystemException catch (e, stack) {
  logger.severe('Level data load failed', e, stack);
  // Fall back to the bundled level set
}

// ❌ Forbidden — swallowing errors
try {
  await loadLevelData();
} catch (e) {
  // silence
}
```

---

## 7. Documentation

### Doc comments — mandatory for public APIs

```dart
/// Resolves a swap on the board.
///
/// Returns [MoveResult] with every cascade step, the cleared cells and the points earned.
/// The move is resolved BEFORE the animation starts (logic before animation).
/// See design/gdd/board-rules.md.
///
/// Throws [IllegalMoveException] if the swap makes no match.
MoveResult resolveSwap({required int from, required int to}) { ... }
```

### TODO format

```dart
// TODO(agent-name): Description [TASK-NNN]
// Example:
// TODO(mechanics-programmer): Add the colour-bomb special [BOARD-42]
```

---

## 8. Testing standards

### The AAA structure — mandatory

```dart
test('MatchFinder finds a horizontal run of three', () {
  // Arrange
  final cells = [0, 0, 0, 1, 2, 3, 4, 5, 6]; // Row 0: three bells

  // Act
  final matched = MatchFinder.find(cells, 3);

  // Assert
  expect(matched, equals({0, 1, 2}));
});
```

### Minimum coverage

| File | Minimum |
|------|---------|
| board_engine.dart / rules engine | 95% |
| scoring.dart | 95% |
| game_rng.dart + level generation | 90% |
| game_state.dart | 85% |
| Screens / widgets | 70% |

---

## 9. Git standards

### Commit format

```
<type>(<scope>): <description>

Examples:
feat(board): add the crown special tile [BOARD-42]
fix(rng): route refills through the seeded GameRng [BUG-7]
test(board): add cascade resolution tests [QA-12]
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`
Scopes: `board`, `rng`, `ui`, `audio`, `vfx`, `balance`, `qa`

### PR checklist

- [ ] dart analyze — 0 errors
- [ ] flutter test — all green
- [ ] No `Random()` outside `game_rng.dart` / `vfx_rng.dart`
- [ ] No wager, currency or chance-based reward (no-gambling.md)
- [ ] Every game constant in GameConfig
- [ ] A GDD reference in the doc comment (for a new mechanic)
- [ ] No allocation in update()/render()

---

## 10. Forbidden patterns

1. **`math.Random()` or `Random()` in game logic** — only the seeded `GameRng` (cosmetics: `VfxRng`)
2. **Hardcoded spawn weights or budgets** outside GameConfig / level data
3. **`isPaused = true`** — use `GameState` + `pauseEngine()`
4. **`await` in `update()` / `render()`** — they must be synchronous
5. **`BuildContext` in Flame components** — use callbacks
6. **`print()`** — use `Logger`
7. **Allocation in `update()` / `render()`** — pre-initialise
8. **`dynamic`** outside JSON boundaries
9. **Inheritance more than 3 levels** below Component
10. **Changing balance numbers** outside the balance config + balance-designer's approval
11. **Any wager, currency or chance-based reward** — `.claude/rules/no-gambling.md`
