---
name: balance-check
description: "Verifies a casual game's balance model through tools/simulate_balance.py. Picks the model B1-B6 from the game's category (board simulation, solvable deals, run length, shot simulation, reflex ramp, solver curve) and checks the whole difficulty curve against the thresholds. Grades the game's own headless bot report for mechanics without a built-in simulator. Fails any config with a currency, wager or odds field."
user-invocable: true
allowed-tools: Bash, Read, Write
argument-hint: "[runs per level, defaults to the model's own]"
---

# `balance-check` — the balance model verifier

Balance in this studio is a verifiable contract, not a "feeling of difficulty".
Every game has exactly one declared model, one config and one run.

## 1. Determine the model

Read `design/gdd/game-concept.md`, the **Classification** block. It contains the category,
the model and the path to the config. If the block is missing, the concept is a FAIL — go back
to `/gate-check concept`.

| Category | Model | Default config | Built-in simulator | PASS windows |
|----------|-------|----------------|--------------------|--------------|
| G1 🧩 Match & Cascade | **B1** | `design/balance/level-config.json` | `swap`, `link`, `blast` | L1–3 ≥ 80%, hardest ≥ 25%, ramp ≥ 15 pp |
| G2 🗂 Tile & Sort | **B2** | `design/balance/level-config.json` | `sort` (others: bot report) | 100% shipped deals solvable, par ≤ 2× per step |
| G3 🔷 Merge & Place | **B3** | `design/balance/endless-config.json` | `slide` (others: bot report) | session 2–12 min, goal tier 2–70% |
| G4 🎯 Aim & Physics | **B4** | `design/balance/bot-report.json` | bot report | the level-curve windows |
| G5 ⚡ Arcade Reflex | **B5** | `design/balance/endless-config.json` | `reflex` | first run 30–180 s, ≤ 10% die in 10 s |
| G6 🧠 Logic & Progression | **B6** | `design/balance/bot-report.json` | bot report | 100% solvable, par ramps, level curve |

The complete thresholds and formats are in `.claude/docs/balance-models.md`.

## 2. The run

```bash
python3 tools/simulate_balance.py \
  --model [b1-b6] \
  --config design/balance/[file].json \
  --report design/balance/simulation-report.md
```

For a mechanic without a built-in simulator, the game's own rules engine is the simulator: run
the headless bot test first, then grade its report.

```bash
flutter test test/balance/bot_sim_test.dart        # writes design/balance/bot-report.json
python3 tools/simulate_balance.py --model report --config design/balance/bot-report.json
```

Exit codes: `0` = PASS, `1` = CONCERNS, `2` = FAIL — you can hang a hook or CI off that. Every
run stamps the config's `simulation` block (`last_run_date`, `last_verdict`, `model`).

If the config does not exist yet, take the reference from
`.claude/docs/templates/balance-configs/` (all pass a run out of the box) and adapt it to the game
without breaking the schema. To check the tool is alive: `python3 tools/simulate_balance.py --selftest`.

## 3. Reading the result

1. The report is always written to `design/balance/simulation-report.md` — a run without a
   report does not count as having happened.
2. **PASS** → the pipeline continues.
3. **CONCERNS** → record the risk in the report and decide with the user whether to proceed.
4. **FAIL** → production stops. Call `balance-designer`; they edit **only the numbers in the
   JSON**, never the code. Then run it again.
5. A FAIL on "No currency / wager / odds fields" is a no-gambling violation, not a tuning issue:
   remove the field and the system behind it (`.claude/rules/no-gambling.md`).

## 4. Full-curve validation (ALL the content, not one point)

> A complete game means a volume of content. You verify the whole surface, not the first level.

- **Levels (B1/B2/B4/B6)** — every level is simulated; the report's level table shows the player
  and skilled pass rates (or par) per level. Look for walls, spikes, missing breathers and new
  elements introduced on a hard level.
- **Endless (B3/B5)** — the whole run distribution, not the mean: early deaths, the median, the
  90th percentile, when the tempo caps.
- **Modes** — the daily challenge generator and any endless/zen mode run through the same model.

The curve report: a "level/stage → key parameters → metric → verdict" table in
`design/balance/curve-report.md`.

## 5. Cross-checking against what the player sees

The numbers shown to the player must match the config:

- level goals, move/shot/time budgets ↔ the config's levels;
- star thresholds ↔ the config's `stars` block;
- the tier chain and the goal tier ↔ the config's `tier_chain` / `goal_tier`.

A discrepancy is not cosmetic — it misleads the player: FAIL.
