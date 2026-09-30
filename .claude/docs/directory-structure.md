# Game Studio directories

The studio supports **5 variants of project architecture**.
On every `/autocreate` run one variant is chosen automatically and recorded in `design/structure.md`.
This creates variety between games — each one gets its own code organisation.

---

## V1 — Layer Architecture

The classic MVC-like organisation: every layer in its own folder.

```text
lib/
├── main.dart
├── app.dart                          # MaterialApp, named routes
├── assets.dart                       # Path constants for every asset
├── game/
│   ├── [name]_game.dart              # FlameGame
│   ├── [name]_world.dart             # World with HasCollisionDetection
│   └── game_config.dart              # Every game constant
├── components/
│   ├── [main_component].dart
│   ├── [element_component].dart
│   ├── clear_animation.dart
│   ├── ambient_particles.dart
│   └── screen_shake.dart
├── systems/
│   ├── game_rng.dart                 # The one seeded source of gameplay randomness
│   ├── [rules]_engine.dart           # The pure rules engine (match/deal/merge/physics step)
│   └── scoring.dart                  # The pure scoring function
├── models/
│   ├── game_state.dart               # The sealed state class
│   └── [game_element].dart
├── screens/
│   ├── splash_screen.dart
│   ├── main_menu.dart
│   ├── game_screen.dart
│   ├── hud_widget.dart
│   └── [others].dart                 # 12+ screens
├── widgets/
│   └── [shared_widgets].dart
├── audio/
│   └── audio_service.dart
└── theme/
    ├── game_theme.dart
    └── animations.dart
```

---

## V2 — Feature Slice

Gameplay (Flame) is separated from UI (Flutter) and services — each feature in its own folder.

```text
lib/
├── main.dart
├── assets.dart
├── core/
│   ├── app.dart                      # MaterialApp, routes
│   └── theme/
│       ├── game_theme.dart
│       └── animations.dart
├── gameplay/                         # Everything Flame: game + components + logic
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   ├── components/
│   │   ├── [main_component].dart
│   │   ├── clear_animation.dart
│   │   └── ambient_particles.dart
│   └── systems/
│       ├── game_rng.dart
│       ├── [rules]_engine.dart
│       └── scoring.dart
├── ui/                               # Everything Flutter: screens + widgets
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── main_menu.dart
│   │   ├── game_screen.dart
│   │   ├── hud_widget.dart
│   │   └── [others].dart
│   └── widgets/
│       └── [shared_widgets].dart
├── domain/                           # Models + states + config
│   ├── game_config.dart
│   ├── game_state.dart
│   └── [game_element].dart
└── services/                         # External services
    └── audio_service.dart
```

---

## V3 — Presentation-Domain-Data (PDD)

A clean separation: presentation (Flutter UI), domain (business logic + Flame), data (configs).

```text
lib/
├── main.dart
├── app.dart
├── assets.dart
├── presentation/                     # The Flutter UI layer
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── main_menu.dart
│   │   ├── game_screen.dart
│   │   ├── hud_widget.dart
│   │   └── [others].dart
│   ├── widgets/
│   │   └── [shared_widgets].dart
│   └── theme/
│       ├── game_theme.dart
│       └── animations.dart
├── domain/                           # Business logic + Flame
│   ├── game/
│   │   ├── [name]_game.dart
│   │   └── [name]_world.dart
│   ├── systems/
│   │   ├── game_rng.dart
│   │   ├── [rules]_engine.dart
│   │   └── scoring.dart
│   └── models/
│       ├── game_state.dart
│       └── [game_element].dart
├── data/                             # Configs and services
│   ├── config/
│   │   └── game_config.dart
│   └── services/
│       └── audio_service.dart
└── components/                       # Flame visual components
    ├── [main_component].dart
    ├── clear_animation.dart
    └── ambient_particles.dart
```

---

## V4 — Module Architecture

By functional module: engine, mechanics, visuals, interface, infrastructure.

```text
lib/
├── main.dart
├── app.dart
├── assets.dart
├── engine/                           # The Flame core
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   └── game_config.dart
├── mechanics/                        # Game logic
│   ├── systems/
│   │   ├── game_rng.dart
│   │   ├── [rules]_engine.dart
│   │   └── scoring.dart
│   └── models/
│       ├── game_state.dart
│       └── [game_element].dart
├── visuals/                          # The visual layer (Flame components + theme)
│   ├── components/
│   │   ├── [main_component].dart
│   │   ├── clear_animation.dart
│   │   └── ambient_particles.dart
│   └── theme/
│       ├── game_theme.dart
│       └── animations.dart
├── interface/                        # Flutter UI
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── main_menu.dart
│   │   ├── game_screen.dart
│   │   ├── hud_widget.dart
│   │   └── [others].dart
│   └── widgets/
│       └── [shared_widgets].dart
└── infrastructure/                   # External dependencies
    └── audio/
        └── audio_service.dart
```

---

## V5 — Vertical Slice

Organised by game area: bootstrap, arena, rules, hud, menus, foundation.

```text
lib/
├── main.dart
├── bootstrap/                        # The application entry point
│   ├── app.dart
│   └── assets.dart
├── arena/                            # The play field (Flame)
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   └── components/
│       ├── [main_component].dart
│       ├── clear_animation.dart
│       └── ambient_particles.dart
├── rules/                            # Rules and mechanics
│   ├── systems/
│   │   ├── game_rng.dart
│   │   ├── [rules]_engine.dart
│   │   └── scoring.dart
│   ├── models/
│   │   ├── game_state.dart
│   │   └── [game_element].dart
│   └── config/
│       └── game_config.dart
├── hud/                              # HUD and in-game overlays
│   ├── hud_widget.dart
│   ├── combo_overlay.dart
│   └── result_overlay.dart
├── menus/                            # Menu screens
│   ├── splash_screen.dart
│   ├── main_menu.dart
│   ├── game_screen.dart
│   └── [others].dart
└── foundation/                       # The shared base
    ├── audio/
    │   └── audio_service.dart
    ├── theme/
    │   ├── game_theme.dart
    │   └── animations.dart
    └── widgets/
        └── [shared_widgets].dart
```

---

## How the variant is chosen

In Phase 2 of `/autocreate` a Python snippet writes the chosen variant to `design/structure.md`:

```python
import time
variant = (int(time.time()) % 5) + 1  # uniformly 1–5
```

`design/structure.md` contains the full path mapping for every file category.
The Phase 4 agents read this file through `lib/contracts.md` and create every file at the
paths it specifies.

---

## Invariants (identical in ALL variants)

- `lib/main.dart` — the entry point, always at the root of `lib/`
- `assets/` — the assets folder, always at the project root
- `design/` — GDD and balance docs, always at the root
- `GameConfig` contains ONLY constants, no logic
- `GameState` — a sealed class, present in every variant
- `AudioService` — at most 3 concurrent sounds
- Asset paths are registered in `pubspec.yaml` under the same `assets/` directories

---

## Key file examples by game category (V1 paths)

Every category shares the same skeleton — one seeded source of randomness, a pure rules engine
that resolves a move before the animation, and the balance model's config. Only what fills them
changes.

```
lib/systems/game_rng.dart           # Random(seed) — the ONLY source of gameplay randomness
lib/systems/[rules]_engine.dart     # Pure function: resolves a move BEFORE the animation
design/balance/[level|endless]-config.json  # The balance model's numbers (read by simulate_balance.py)
```

### G1 — Match & Cascade (swap match-3 / link chain / tap blast)
```
lib/systems/board_engine.dart       # Matches, gravity, refill, cascades, specials, reshuffle
lib/systems/scoring.dart            # Points, combo multiplier, stars
lib/components/board_component.dart # The board, playing back resolved cascades
lib/components/tile_component.dart
design/balance/level-config.json    # model B1
```

### G2 — Tile & Sort (triple tile tray / pair tiles / sort / patience)
```
lib/systems/deal_generator.dart     # Seeded deals, verified solvable
lib/systems/deal_solver.dart        # The solver used by the generator and the tests
lib/systems/tray_rules.dart         # Tray / foundation / container rules
lib/components/tile_stack_component.dart
design/balance/level-config.json    # model B2 (+ bot-report.json)
```

### G3 — Merge & Place (slide merge / drop merge / block place / merge grid)
```
lib/systems/merge_engine.dart       # Slides or placements, merges, run-over detection
lib/systems/spawn_table.dart        # The next piece from the seeded GameRng
lib/components/merge_board_component.dart
design/balance/endless-config.json  # model B3
```

### G4 — Aim & Physics (bubble / peg clear / bricks / knockdown / draw)
```
lib/systems/physics_world.dart      # Forge2D, a FIXED 1/60 s timestep, body cap
lib/systems/aim_guide.dart          # The predicted trajectory
lib/components/ball_component.dart
lib/components/peg_component.dart
design/balance/level-config.json    # model B4 (+ bot-report.json from test/balance/)
```

### G5 — Arcade Reflex (runner / stacker / catcher / slicer / flyer / thrower)
```
lib/systems/tempo_ramp.dart         # Speed, spawn interval, reaction window over time
lib/systems/hazard_spawner.dart     # Spawns from the seeded GameRng within the ramp
lib/components/player_component.dart
design/balance/endless-config.json  # model B5
```

### G6 — Logic & Progression (paths / pipes / unblock / memory / logic grid)
```
lib/systems/level_generator.dart    # Seeded generation, proven solvable
lib/systems/level_solver.dart       # Solver + par moves
lib/components/logic_board_component.dart
design/balance/level-config.json    # model B6 (+ bot-report.json)
```
