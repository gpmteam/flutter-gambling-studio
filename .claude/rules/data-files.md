---
description: JSON config validation rules for casual-game balance configs (B1-B6) consumed by tools/simulate_balance.py, and the level/content data the game loads
globs: ["design/balance/**/*.json", "assets/data/**/*.json", "lib/game/game_config.dart"]
---

# Data Files Rules — balance configs and level data

Every game MUST have exactly one balance config, matching its category. The config is the input
for `tools/simulate_balance.py`; reference files that pass a run out of the box live in
`.claude/docs/templates/balance-configs/`.

| Category | Model | Config | Reference |
|----------|-------|--------|-----------|
| G1 🧩 | B1 | `design/balance/level-config.json` | `templates/balance-configs/board-levels-config.json` |
| G2 🗂 | B2 | `design/balance/level-config.json` (+ `bot-report.json` for non-sort mechanics) | `templates/balance-configs/sort-levels-config.json` |
| G3 🔷 | B3 | `design/balance/endless-config.json` (+ `bot-report.json` for non-slide mechanics) | `templates/balance-configs/slide-merge-config.json` |
| G4 🎯 | B4 | `design/balance/level-config.json` + `design/balance/bot-report.json` | `templates/balance-configs/bot-report-example.json` |
| G5 ⚡ | B5 | `design/balance/endless-config.json` | `templates/balance-configs/reflex-ramp-config.json` |
| G6 🧠 | B6 | `design/balance/level-config.json` + `design/balance/bot-report.json` | `templates/balance-configs/bot-report-example.json` |

The run command and the thresholds are in `.claude/docs/balance-models.md`.

## level-config.json — the board schema (G1 / model B1)

```json
{
  "game_name": "Game name",
  "model": "b1",
  "rule": "swap",
  "min_group": 3,
  "points_per_piece": 10,
  "combo_bonus": 0.5,
  "dead_board": "reshuffle",
  "stars": { "two_star_ratio": 1.25, "three_star_ratio": 1.5 },
  "levels": [
    { "id": 1, "cols": 7, "rows": 8, "kinds": 4, "moves": 20, "target_score": 1800 },
    { "id": 2, "cols": 7, "rows": 8, "kinds": 4, "moves": 20, "target_score": 2600 },
    { "id": 13, "cols": 7, "rows": 8, "kinds": 6, "moves": 22, "target_score": 1100,
      "collect": { "kind": 2, "count": 18 } }
  ],
  "simulation": {
    "last_run_date": "2026-01-01",
    "last_verdict": "PASS",
    "model": "b1"
  }
}
```

## Required fields

| Field | Type | Constraints |
|-------|------|-------------|
| `model` | string | `b1`–`b6` |
| `rule` | string | the built-in rule (`swap`/`link`/`blast`/`sort`/`slide`/`reflex`) or the mechanic name for a bot report |
| `levels[]` (level-based) | array | ≥ 12 levels; each with the board/deal size, the budget (moves/shots/time) and the goal |
| `levels[].kinds` | int | ≥ 3 for boards |
| `dead_board` (G1) | string | `"reshuffle"` |
| `generator` (G2/G6) | string | `verify` / `reverse` / `raw` (raw only with a proof) |
| `tempo` (G5) | object | start/cap interval and reaction window, `time_to_cap_s` |
| `simulation.last_run_date` | date | stamped by `tools/simulate_balance.py` |

## Rules for game_config.dart and level data

```dart
// ✅ THE REQUIRED STRUCTURE
class GameConfig {
  // Loaded from design/balance/level-config.json (mirrored into assets/data/levels.json) —
  // do not change without balance-designer!
  static const int boardCols = 7;
  static const int boardRows = 8;
  static const int pointsPerPiece = 10;
  static const double comboStep = 0.5;

  // Animation (approved by juice-artist)
  static const Duration swapDuration = Duration(milliseconds: 160);
  static const Duration cascadeStep = Duration(milliseconds: 180);
  static const Duration clearCelebration = Duration(seconds: 2);

  // Feedback thresholds (points-based, never money)
  static const int bigComboStep = 3;   // cascade step 3+ = big combo feedback
  static const int maxParticles = 200; // particle limit
}
```

Level data the game reads at runtime lives in `assets/data/levels.json` (or `stages.json` /
`ramp.json`) and is generated from — or identical to — the balance config's `levels`/`tempo`
block. Never maintain two diverging copies.

## Forbidden in data files

1. Duplicating a config value in both JSON and Dart — one source of truth
2. Any money, wager, odds or chance-for-reward field: `bet`, `stake`, `wager`, `price`, `cost` in a
   currency, `currency`, `coins`, `chips`, `credits`, `balance`, `wallet`, `rtp`, `payout`,
   `paytable`, `house_edge`, `jackpot`, `odds`, `pity`, `gacha` — `simulate_balance.py` FAILS on them
3. A level whose goal cannot be met by any sequence of moves (unsolvable) — the generator must
   verify it
4. A weight of 0 in a spawn table — delete the entry instead of zeroing it
5. Committing a changed config without a fresh `simulate_balance.py` run (`simulation.last_run_date`)
6. Values shown to the player (level goals, star thresholds, move budgets) that disagree with the config
