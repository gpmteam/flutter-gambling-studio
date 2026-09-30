---
name: team-dev
description: "Orchestrates development of a casual game mechanic across several specialists. Coordinates the game designer, the balance designer, the mechanics programmer, the VFX artist and the sound designer."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write, Agent
argument-hint: "<feature/system description> (e.g. 'Specials from 5-matches', 'Undo with three charges', 'A daily challenge on a seeded level')"
---

# `team-dev` — studio orchestration

Runs the agents in the right order to implement a complex feature.

## Instructions

1. Clarify the task with the user: which feature, and is there already a GDD?
   Read the **Classification** block in `design/gdd/game-concept.md` — the category (G1–G6)
   and the balance model (B1–B6) determine who to call and in what order.

2. If there is no GDD, call `game-designer` to write one.
   They must consult `balance-designer` on anything involving the model's numbers.

3. **No gambling, ever.** If the feature is a wager, a currency, a shop, a chance-based reward or a
   casino game, stop and offer the casual alternative (`.claude/rules/no-gambling.md`).

4. **Plan balance before implementation.** If the feature touches the numbers:
   - `balance-designer` edits the model's JSON config
   - run it: `python3 tools/simulate_balance.py --model [b1-b6|report] --config design/balance/[file].json`
   - use a built-in simulator or the existing rules-engine bot where available
   - for a new/custom mechanic with no simulator yet, record the B1–B6 windows, JSON data and
     headless-bot plan before coding; implement that bot with the rules engine, then require a
     real PASS before integration/release. Never fabricate a passing report.

   | Category | What the balance designer tunes |
   |----------|---------------------------------|
   | G1 | kinds, move budgets, targets, blockers per level |
   | G2 | layout size, kinds, par, the generator policy |
   | G3 | board size, spawn table, goal tier |
   | G4 | shot budgets, layouts, target counts |
   | G5 | tempo ramp, reaction windows, grace period |
   | G6 | level sizes, constraints, par |

5. For the implementation call `mechanics-programmer` (the rules engine) and `juice-artist` (VFX
   animation) in the right order. Always pass them the links to the GDD and to the balance config.
   Remind them: one seeded `GameRng`, logic before animation, and not one balance number as a Dart
   literal.

6. Where needed, bring in `sound-designer` for the audio events
   (the move, the match/cascade, combos, clears, failure).

7. Every UI pass must follow `.claude/docs/mobile-first-contract.md`: a portrait phone game, touch
   only, verified at the four phones, with no desktop/tablet/landscape layout or device frame.

8. All player-facing copy the feature introduces is written in English (unless the user
   explicitly asked for the game in another language).

9. Verify the completed change with `/balance-check` and `/ui-audit`; a missing bot report is
   incomplete work, not a PASS.
