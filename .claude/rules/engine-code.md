---
description: Flame 1.18.x specific patterns — component lifecycle, world setup, camera, forbidden APIs
globs: ["lib/game/**/*.dart", "lib/components/**/*.dart", "lib/systems/**/*.dart"]
---

# Engine Code Rules — Flame 1.18.x

## CRITICAL Flame 1.18.x APIs

### HasCollisionDetection — on World, not on FlameGame
```dart
// ✅ CORRECT (Flame 1.18+)
class BoardWorld extends World with HasCollisionDetection {
  // collision detection goes here
}

// ❌ FORBIDDEN (deprecated in 1.17, removed in 1.18)
class BoardGame extends FlameGame with HasCollisionDetection { }
```

### CameraComponent — the new API only
```dart
// ✅ CORRECT
late final CameraComponent camera;
late final BoardWorld world;

@override
Future<void> onLoad() async {
  world = BoardWorld();
  camera = CameraComponent(world: world);
  await addAll([world, camera]);
}

// ❌ FORBIDDEN (the old Camera API)
camera = Camera(); // Does not exist in Flame 1.18!
```

### FlameGame.world and FlameGame.camera — first-class fields
```dart
// Flame 1.18: game.world and game.camera are built-in fields.
// Do not create your own fields named world/camera — those names are reserved.

class BoardGame extends FlameGame {
  // this.world — already exists (World)
  // this.camera — already exists (CameraComponent)
  // Create typed getters instead:
  BoardWorld get boardWorld => world as BoardWorld;
}
```

### SpawnComponent (Flame 1.15+)
```dart
// ✅ Use it for periodic spawning of hazards/effects
add(SpawnComponent(
  factory: (i) => SparkParticle(),
  period: 0.1,
  area: Rectangle.fromLTWH(0, 0, size.x, size.y),
));
```

### HasTimeScale (Flame 1.16+) — slow down / speed up
```dart
// For a slow-motion effect on a big combo
class BoardComponent extends PositionComponent with HasTimeScale {
  void slowMotion() => timeScale = 0.3;
  void normalSpeed() => timeScale = 1.0;
}
```

## Forbidden Flame patterns

1. **`game.isPaused = true`** — use a `GameState` enum + `pauseEngine()`/`resumeEngine()`
2. **`Flame.images.load()` inside `update()`** — only in `onLoad()`
3. **Direct `ComponentSet` operations** — use `game.children.toList()` (Flame 1.18)
4. **`onGameResize` without an `isMounted` check** — a component can receive a resize before it loads
5. **Inheritance deeper than 3 levels** — use composition instead (add child components)
6. **Hot reload for game files** — use Hot Restart (Shift+R)

## Required patterns

### The board component
```dart
class BoardComponent extends PositionComponent with HasGameRef<BoardGame> {
  // Pre-initialised for update() — no allocation in the hot path
  final _tempVector = Vector2.zero();

  late final List<TileComponent> _tiles;

  @override
  Future<void> onLoad() async {
    // Load assets ONLY in onLoad
    _tiles = await _createTiles();
    await addAll(_tiles);
  }

  @override
  void update(double dt) {
    // SYNCHRONOUS! No await!
    if (!_isAnimatingDrop) return;
    _tempVector.setFrom(position);
    _advanceDrop(dt); // No allocation — plays back an already-resolved cascade
  }
}
```

### ParticleSystemComponent — limits
```dart
// For combos of x5 and above
void _spawnComboParticles(int combo) {
  final count = (combo * 10).clamp(20, GameConfig.maxParticles);
  add(ParticleSystemComponent(
    particle: Particle.generate(
      count: count,
      lifespan: 1.5,
      generator: (i) => AcceleratedParticle(
        acceleration: Vector2(0, 98),
        speed: Vector2(
          (vfxRng.nextDouble() - 0.5) * 200, // cosmetic only — never the gameplay GameRng
          -vfxRng.nextDouble() * 300,
        ),
        child: CircleParticle(radius: 3, paint: Paint()..color = Colors.amber),
      ),
    ),
  ));
}
```

### Audio — at most 3 concurrent sounds
```dart
class AudioService {
  // Only 3 channels: BGM + Action + Effect
  static const int maxConcurrentSounds = 3;

  Future<void> playClear(int tier) async {
    await FlameAudio.play('audio/sfx/sfx_win_${_tierName(tier)}.wav');
  }

  // Score ticking with rising pitch along a cascade
  Future<void> playScoreTick(int cascadeStep) async {
    final rate = 1.0 + (cascadeStep / 10).clamp(0.0, 0.5);
    await FlameAudio.play('audio/sfx/sfx_score.wav', volume: 1.0);
    // playbackRate is controlled through the AudioPlayer instance
  }
}
```

## Delta-plan presentation

- A resolved fall list may contain only displaced pieces; it is not the complete field.
- During falling, draw stationary survivors as well as moving pieces and refills. Prepare
  membership masks outside `update()`/`render()`; never recompute gameplay to fill visual gaps.
- Inspect a mid-fall frame after a small clear and one that displaces other pieces. Verify
  unchanged survivors remain visible and the committed board and score stay unchanged.

## Performance

- No allocation in `update()` or `render()` — pre-initialise Vector2, Rect, Paint
- `SpriteBatch` for more than 20 identical sprites (the tiles on the board!)
- `debugMode = true` only in debug builds
- `FpsTextComponent` only in debug builds
- At most 200 active particles at once (GameConfig.maxParticles)
