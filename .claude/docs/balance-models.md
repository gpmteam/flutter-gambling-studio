# Balance models — what is verified, and how

> Balance in this studio is a **verifiable contract**, not "it feels about right". Every game
> declares one balance model (out of six), keeps its difficulty numbers in one JSON config, and
> clears one simulation run that either lands inside the windows or blocks the release.
>
> The model follows from the game's category — see `.claude/docs/game-categories.md`. The owner of
> every model is the `balance-designer` agent; only they change the numbers.
>
> Balance here means *difficulty and pacing*: pass rates, par moves, run lengths, session time.
> There is no RTP, payout, odds or economy to balance — a config that contains one fails
> (`.claude/rules/no-gambling.md`).

## Summary table

| Model | Categories | Config | How it is measured | PASS windows |
|-------|-----------|--------|--------------------|--------------|
| **B1 — Board simulation** | G1 | `design/balance/level-config.json` | built-in board bots (`swap` / `link` / `blast`) or the game's bot report | L1–3 ≥ 80%, no wall < 15%, ramp ≥ 15 pp |
| **B2 — Solvable deals** | G2 | `design/balance/level-config.json` | built-in `sort` solver, or the game's solver report | 100% shipped deals solvable, par ramps ≤ 2× per step |
| **B3 — Run length** | G3 | `design/balance/endless-config.json` | built-in `slide` bots, or the game's bot report | median session 2–12 min, goal tier reachable 2–70% |
| **B4 — Shot simulation** | G4 | `design/balance/level-config.json` + `bot-report.json` | the game's headless physics bot (report) | the level-curve windows |
| **B5 — Reflex ramp** | G5 | `design/balance/endless-config.json` | built-in reaction-window model | median first run 30–180 s, ≤ 10% die in 10 s |
| **B6 — Solver curve** | G6 | `design/balance/level-config.json` + `bot-report.json` | the game's generator/solver report | 100% solvable, par ramps, level-curve windows |

One entry point runs every model:

```bash
python3 tools/simulate_balance.py --model b1 --config design/balance/level-config.json
python3 tools/simulate_balance.py --model report --config design/balance/bot-report.json
python3 tools/simulate_balance.py --selftest     # every built-in model on the reference templates
```

The report is always written to `design/balance/simulation-report.md`, and the run stamps the
config's `simulation` block (`last_run_date`, `last_verdict`, `model`). Exit codes: `0` PASS,
`1` CONCERNS, `2` FAIL. Reference configs that pass out of the box live in
`.claude/docs/templates/balance-configs/`.

### Built-in simulator or the game's own bot?

- **Built-in** — B1 (`swap`, `link`, `blast`), B2 (`sort`), B3 (`slide`) and B5 (`reflex`). The
  Python simulation implements the rules generically. It is deliberately conservative: bots
  simplify special pieces/boosters and use limited look-ahead. Their pass rates estimate the
  curve; validate custom rules with the actual game engine bot. Python and Dart RNG sequences
  need not match across languages; replay determinism is verified inside the game engine.
- **Bot report** — everything else (rotate match, tile tray, pairs, patience, drop merge, block
  place, merge grid, every G4 physics game, every G6 logic game). The game's pure rules engine
  (or headless Forge2D world) is driven by a bot in `test/balance/bot_sim_test.dart`, which writes
  `design/balance/bot-report.json`; `--model report` grades it. The game's own rules are then the
  simulator — always the most faithful option, and allowed for B1/B3 too.

Bot report format:

```json
{
  "game_name": "Olympus Pegs",
  "model": "b4",
  "bot": "headless Forge2D, fixed 1/60 s step; best of 12 sampled angles with ±3° noise (player), best of 24 (skilled)",
  "levels": [
    {"id": 1, "runs": 200, "passes": 191, "skilled_runs": 200, "skilled_passes": 200,
     "par": 4, "solvable": true}
  ],
  "endless": {"runs": 300, "median_run_s": 74, "p90_run_s": 260, "early_death_rate": 0.04,
              "time_to_cap_s": 150, "session_minutes": 4.2}
}
```

The report must declare its `model` (b1–b6) and `bot`. Every level needs positive player and
skilled trial counts and pass counts inside [0, runs]. B2/B6 levels also require positive `par`
and an explicit `solvable` boolean for every level; missing evidence fails. B1/B2/B4/B6 require
levels; B3/B5 require an `endless` object with a positive `runs` count.

B3 endless reports supply `session_minutes`, `early_move_rate` (runs ending before 40 moves),
`skilled_goal_rate` and `player_milestone_rate` (goal − 3). Rates are in [0, 1]. These use B3's
merge windows, rather than B5's shorter reflex session windows.
B5 endless reports supply `median_run_s`, `p90_run_s`, `early_death_rate` and `time_to_cap_s`.
Nonfinite numbers, invalid counts and a model mismatch fail instead of receiving a PASS.

---

## The level curve (B1, B2, B4, B6 and every level-based report)

**What we verify.** That the first levels teach, the middle ramps, breathers exist, and nothing is
a wall. Measured with a **player bot** (an average player: the best obvious move most of the time,
a mistake the rest) and a **skilled bot** (look-ahead).

| Metric | PASS | CONCERNS | FAIL |
|--------|------|----------|------|
| Levels in the curve | ≥ 12 | 3–11 | < 3 |
| Onboarding (L1–L3, worst, player bot) | ≥ 80% | 60–80% | < 60% |
| Hardest level (player bot) | ≥ 25% | 15–25% | < 15% (a wall) |
| Hardest level (skilled bot) | ≥ 40% | 25–40% | < 25% (unfair) |
| Ramp: first-quarter minus last-quarter pass rate | ≥ 15 pp | < 15 pp (flat) | — |
| Biggest level-to-level drop | ≤ 40 pp | 40–55 pp | > 55 pp |

A sawtooth is the goal: hard levels are followed by a breather, and every new mechanic (a new
blocker, a new symbol kind) arrives on an easier level.

## B1 — Board simulation (G1)

Config (`design/balance/level-config.json`):

```json
{
  "game_name": "Thunder Link",
  "model": "b1",
  "rule": "swap",                 // swap | link | blast
  "min_group": 3,                 // 2 for blast
  "diagonals": false,             // link only
  "points_per_piece": 10,
  "combo_bonus": 0.5,             // swap: +50% per cascade step
  "group_bonus": 0.1,             // link/blast: +10% per piece above min_group
  "dead_board": "reshuffle",      // required
  "levels": [
    {"id": 1, "cols": 7, "rows": 8, "kinds": 4, "moves": 20, "target_score": 1800},
    {"id": 13, "cols": 7, "rows": 8, "kinds": 6, "moves": 22, "target_score": 1100,
     "collect": {"kind": 2, "count": 18}}
  ]
}
```

Also reported: dead boards per 100 moves (the game must reshuffle automatically — a missing
`"dead_board": "reshuffle"` is a FAIL).

## B2 — Solvable deals (G2)

| Metric | PASS | CONCERNS | FAIL |
|--------|------|----------|------|
| Shipped deals solvable | 100% | — | any unsolvable deal can ship |
| Raw deals solvable (`generator: verify`) | ≥ 50% | 0–50% (slow generation) | 0% |
| First level par | ≤ 10 moves | 10–16 | > 16 |
| Biggest par step | ≤ 2.0× | 2–3× | > 3× |
| Par grows (late/early) | ≥ 1.5× | < 1.5× | — |

`generator` is `verify` (generate, solve, reject unsolvable), `reverse` (deal backwards from a
solved state) or `raw` (only with a proof that every deal is solvable). Undo is always available.

## B3 — Run length (G3)

| Metric | PASS | CONCERNS | FAIL |
|--------|------|----------|------|
| Median session (player bot) | 2–12 min | 1–2 or 12–20 min | outside |
| Runs over within 40 moves | ≤ 10% | 10–25% | > 25% |
| Skilled bot reaches the goal tier | 2–70% | < 2% or > 70% | 0% |
| Player bot reaches goal − 3 | ≥ 50% | 30–50% | < 30% |

The goal tier is the game's hero object at the top of its tier chain (`tier_chain` names the
chain, e.g. cherry → bell → seven → crown).

## B4 — Shot simulation (G4)

The game's physics is the simulator: a fixed 1/60 s Forge2D step, headless, with a bot that aims
from sampled angles with noise. Grade the report with the level-curve windows; also report
median shots used and the share of levels won on the last shot (a CONCERNS if above 30% — the
curve is too tight). A cap on simultaneous bodies keeps the simulation and the game stable.

## B5 — Reflex ramp (G5)

Config (`design/balance/endless-config.json`):

```json
{
  "game_name": "Thunder Dash",
  "model": "b5",
  "rule": "reflex",
  "lives": 1,
  "grace_s": 3,
  "tempo": {"interval_start_s": 1.3, "interval_cap_s": 0.6,
            "window_start_ms": 900, "window_cap_ms": 430,
            "time_to_cap_s": 150, "curve": "ease_in"},
  "player": {"reaction_ms_mean": 430, "reaction_ms_sd": 90, "lapse_rate": 0.006}
}
```

| Metric | PASS | CONCERNS | FAIL |
|--------|------|----------|------|
| Median first run | 30–180 s | 20–30 or 180–300 s | outside |
| Runs ending in the first 10 s | ≤ 10% | 10–20% | > 20% |
| 90th-percentile run | ≤ 600 s | 600–1200 s | > 1200 s |
| Time for the tempo to reach its cap | 60–300 s | 30–60 or 300–600 s | outside |

The game reads these same numbers from `GameConfig`; hazard telegraphing must fit inside the
reaction window.

## B6 — Solver curve (G6)

The game's level generator ships with a solver. The bot report proves every level solvable
(`"solvable": true` — any `false` is a FAIL), records par, and records a player bot's pass rate
under the level's move/time budget. Graded with the level-curve and par windows.

---

## Rules common to every model

1. **One source of truth.** The numbers live in the JSON config; Dart reads them into
   `GameConfig`/level data. Duplicating a value in JSON and code is a violation.
2. **Logic before animation.** Every move is resolved by the pure rules engine before the
   animation plays it back — that is what makes the bot simulation and the tests possible.
3. **One seeded `GameRng`.** All gameplay randomness (fills, deals, spawns, level generation)
   flows from one seeded generator, so the same seed reproduces a level exactly in the game, the
   tests and the bot.
4. **The report is mandatory.** A run that is not written to
   `design/balance/simulation-report.md` did not happen.
5. **The run date.** `simulation.last_run_date` is stamped by every run; a config change without a
   fresh run is rejected by `/gate-check`.
6. **No money, no odds.** A config field for a bet, price, currency, odds, payout, jackpot or pity
   fails the run.
7. **Changing a target window = an ADR.** Moving a threshold for one game goes through
   `/architecture-decision`, not a silent edit.

## Report format

```markdown
# Balance Report — [Game name]

- **Model**: B[1-6] — [name]
- **Config**: design/balance/[file].json
- **Method**: [bots and rules simulated]
- **Trials**: 40
- **Date**: YYYY-MM-DD

## Result
| Metric | Target | Measured | Verdict |
|--------|--------|----------|---------|
| Onboarding pass rate (L1–L3, worst) | ≥ 80% | 92.5% (level 2) | ✅ PASS |
| ... | | | |

## Levels
[per-level table]

## Verdict
✅ PASS — the difficulty curve is inside its windows.
⚠️ CONCERNS — [what is borderline, and the risk].
❌ FAIL — [what is outside]; balance-designer adjusts [specific parameters].
```
