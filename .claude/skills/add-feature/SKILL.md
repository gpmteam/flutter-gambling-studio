---
name: add-feature
description: "Adds a new feature to a finished casual game. G1: a new special or blocker. G2: undo or hints. G3: a new tier or milestone. G4: a new target type. G5: a new hazard. G6: a new rule. Any category: a daily challenge, achievements, a collection page, a new world. Never a wager, currency or chance-based reward."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write, Agent
argument-hint: "<feature-name>"
---

# `add-feature` — adding a feature

The correct way to add a new mechanic to a finished game.

## Instructions

1. Read `design/gdd/game-concept.md`, the **Classification** block — the category (G1–G6),
   the balance model (B1–B6) and the path to its config.

2. Check the feature against `.claude/rules/no-gambling.md`. A wager, a currency, a shop, a
   chance-based reward (spins, chests, packs, scratch reveals) or a casino game is not added; offer
   the casual alternative (a milestone reward, a daily challenge, an album page) instead.

3. Ask the user:
   - How does the feature work?
   - Where does it appear (which levels/worlds, which mode)?
   - How much should it change difficulty?

4. **Update the balance config** — a feature almost always changes the numbers:

   | Category | Config | What typically changes |
   |----------|--------|------------------------|
   | G1 | `design/balance/level-config.json` | kinds, budgets, targets, blockers per level |
   | G2 | `design/balance/level-config.json` | layout size, kinds, par, generator policy |
   | G3 | `design/balance/endless-config.json` | the tier chain, spawn weights, goal tier |
   | G4 | `design/balance/level-config.json` + bot report | layouts, shot budgets, targets |
   | G5 | `design/balance/endless-config.json` | the tempo ramp, hazards, grace period |
   | G6 | `design/balance/level-config.json` + bot report | constraints, sizes, par |

5. **Verify the balance contract** before code, and rerun after implementation:
   ```bash
   python3 tools/simulate_balance.py --model [b1-b6|report] --config design/balance/[file].json
   ```
   - Call `balance-designer` to bring the curve back into its windows.
   - Run `/balance-check` to confirm it and write the report.
   - Use the built-in simulator or the existing engine bot. If new rules need a bot that does
     not yet exist, record the windows/data/bot plan first and build it with the rules engine.
     A final PASS from the actual new rules is required before integration/release; never
     substitute a fabricated report or an old rules simulation for this evidence.

6. **Implementation**: call `mechanics-programmer`. They read the new values from the config —
   not one of the feature's numbers appears as a Dart literal.

7. Any new player-facing copy is written in English (unless the user explicitly asked for the
   game in another language), and uses the game's own words — never gambling vocabulary.

8. Create an issue in `production/session-state/` and call `/team-dev` for the full implementation.

9. After the code: `/balance-check` to verify, `/code-review` for the review.
