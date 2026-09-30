---
description: QA test standards for casual mini-games — seeded determinism, the pure rules engine, scoring, no dead ends, edge cases, layout geometry
globs: ["test/**/*.dart", "integration_test/**/*.dart"]
---

# Test Standards — Casual Game QA

## Mandatory tests for every game

### 1. Seeded determinism (CRITICALLY IMPORTANT)
The same seed must reproduce the same level exactly — this is what makes levels, bot simulations
and bug reports reproducible:

```dart
group('GameRng', () {
  test('the same seed reproduces the same starting board', () {
    // Arrange
    final a = BoardEngine.newLevel(LevelData.byId(5), GameRng(1234));
    final b = BoardEngine.newLevel(LevelData.byId(5), GameRng(1234));

    // Assert
    expect(a.cells, equals(b.cells));
  });

  test('the same seed and moves reproduce the same score', () {
    final moves = [const Swap(12, 13), const Swap(30, 37)];
    int play(int seed) {
      final engine = BoardEngine.newLevel(LevelData.byId(5), GameRng(seed));
      for (final m in moves) {
        engine.resolve(m);
      }
      return engine.score;
    }
    expect(play(99), equals(play(99)));
  });

  test('gameplay code never constructs its own Random', () {
    for (final file in Directory('lib').listSync(recursive: true).whereType<File>()) {
      if (!file.path.endsWith('.dart') || file.path.endsWith('game_rng.dart') ||
          file.path.endsWith('vfx_rng.dart')) {
        continue;
      }
      expect(file.readAsStringSync(), isNot(contains('Random(')), reason: file.path);
    }
  });
});
```

### 2. The rules engine (pure logic)
```dart
group('BoardEngine', () {
  test('a swap that lines up three clears them', () { ... });
  test('a swap that makes no match is rejected and the board is unchanged', () { ... });
  test('cascades resolve until the board is stable', () { ... });
  test('a 5-in-a-row creates the special tile', () { ... });
  test('a board with no legal move is reshuffled into one with a move', () { ... });
});
```

### 3. Scoring and goals
```dart
group('Scoring', () {
  test('points follow the combo formula from the config', () { ... });
  test('the level clears the moment the goal is met', () { ... });
  test('stars follow the configured thresholds', () { ... });
});
```

### 4. Edge cases
```dart
group('Edge cases', () {
  test('a fast double tap does not submit two moves', () async {
    final game = BoardGame();
    game.tryMove(const Swap(1, 2));
    final second = game.tryMove(const Swap(3, 4)); // Must be ignored while resolving
    expect(second, isFalse);
    expect(game.gameState, isA<ResolvingState>());
  });

  test('state recovers after a pause mid-resolve', () async {
    final game = BoardGame();
    game.tryMove(const Swap(1, 2));
    game.pause();
    game.resume();
    await game.settle();
    expect(game.gameState, isA<ReadyState>());
  });

  test('running out of moves ends the level with a retry path', () { ... });
});
```

### 5. No gambling (mandatory)
```dart
test('the game has no currency, wager or chance-based reward code', () {
  final forbidden = RegExp(r'\b(bet|wager|stake|jackpot|payout|paytable|coinBalance|chips|gacha|lootBox)\b',
      caseSensitive: false);
  for (final file in Directory('lib').listSync(recursive: true).whereType<File>()) {
    if (!file.path.endsWith('.dart')) continue;
    expect(forbidden.hasMatch(file.readAsStringSync()), isFalse, reason: file.path);
  }
});
```

### 6. State leakage tests
```dart
group('State leakage — nothing leaks between levels', () {
  test('starting a new level resets score, moves and goals', () { ... });
  test('GameState returns to Ready after every resolved move', () async {
    final game = BoardGame();
    for (var i = 0; i < 10; i++) {
      await game.playAnyLegalMove();
      expect(game.gameState, isA<ReadyState>(),
             reason: 'After move #$i the GameState should be Ready');
    }
  });
});
```

### 7. The balance bot (mandatory when the mechanic has no built-in simulator)
`test/balance/bot_sim_test.dart` drives the pure rules engine (or the headless Forge2D world at a
fixed 1/60 s step) with a player bot and a skilled bot over every level, and writes
`design/balance/bot-report.json` in the format in `.claude/docs/balance-models.md`. It must not
depend on rendering or wall-clock time.

### 8. Gameplay-screen geometry (mandatory widget test)

Every `GameScreen` must expose `Key('gameplaySurface')` and `Key('primaryAction')` as required by
`.claude/docs/mobile-first-contract.md` and `.claude/docs/gameplay-screen-contract.md`. Pump the
real screen at the four portrait phones — 360×640, 360×800, 390×844 and 430×932 — and verify:

- `tester.takeException()` stays null and no overflow is logged;
- both keys are present, on-screen, and not under a vertical `Scrollable`;
- the gameplay surface meets the contract's field-dominance thresholds, unless the documented
  narrow-mechanic exception is asserted explicitly in the test;
- the primary action has a tap target at least 48 logical pixels wide and 56 high, and is visible in
  the first viewport;
- 1.3× text scale does not clip the primary action, score or goal labels.
- phone sizes preserve the thumb-reachable, touch-first hierarchy.
- the same composition renders at every phone (no width breakpoint switches layouts);
- pumped once at 1440×900 inside the app's `MaterialApp.builder`, the screen renders at phone-column
  width over the background surround, not stretched and not recomposed.

Name the file `test/screens/game_screen_layout_test.dart`. Geometry tests complement rather than
replace the mandatory idle/active screenshot vision pass.

## Minimum coverage by area

| Area | Minimum |
|------|---------|
| Rules engine (board/deal/merge/physics step) | 95% |
| Scoring and goals | 95% |
| GameRng / level generation | 90% |
| The GameState machine | 85% |
| HUD widgets | 70% |
| GameScreen geometry at the four portrait phones (+ the wide-host column check) | 100% of required sizes |
| Animations (components) | 60% |

## Test format (AAA)

```dart
test('a description in the third person, present tense', () {
  // Arrange — set up
  final game = ...;

  // Act — do the thing
  final result = game.method();

  // Assert — check it
  expect(result, ...);
});
```

Test names and `reason:` strings are written in English, like the rest of the codebase.

## Forbidden in tests

1. An unseeded `Random()` inside tests — use a fixed `GameRng(seed)` or a fake
2. `sleep()` or `Future.delayed()` — use `FakeAsync` or `pump()`
3. Tests without a single `expect` — empty tests are forbidden
4. Dependence on test order — every test must be independent
