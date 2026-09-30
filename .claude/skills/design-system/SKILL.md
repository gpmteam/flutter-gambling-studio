---
name: design-system
description: "Designs one individual system of a casual game: board rules and specials (G1), deal generation and the tray (G2), the tier chain and spawn table (G3), aim, layouts and shot budgets (G4), the tempo ramp and hazards (G5), the level generator and solver (G6), plus progression, scoring and stars. Generates a GDD document with balance-designer and game-designer involved."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
argument-hint: "<system-name> (e.g. board-rules, specials, deal-generator, tier-chain, tempo-ramp, progression)"
---

# `design-system` — detailing a game system

Interactively designs one **game** system of a casual game (mechanics/balance).

> The **interface direction** (asset/world Design DNA plus the Game UI Read, Design Signature,
> state map, and per-screen layout recipes) lives in `design/gdd/game-concept.md` and
> `design/art-direction.md`. See `.claude/rules/anti-slop-design.md` and
> `.claude/docs/layout-archetypes.md`. This skill is about game systems, not about the theme.
>
> No system may be a wager, a currency, a shop or a chance-based reward
> (`.claude/rules/no-gambling.md`).

## Workflow

1. **Context**: read `design/gdd/game-concept.md`, the **Classification** block —
   it sets the category (G1–G6) and the balance model (B1–B6).

2. **The system's type**: decide who leads the work.

   | Category | Balance (`balance-designer`) | Mechanics (`game-designer`) |
   |----------|------------------------------|-----------------------------|
   | **G1** 🧩 | kinds, move budgets, targets, the level curve | the move rule, specials, blockers, goals, reshuffle |
   | **G2** 🗂 | layout size, kinds, par curve, generator policy | tray/container rules, undo, earned hints |
   | **G3** 🔷 | board size, spawn table, goal tier, session length | the tier chain, next-piece preview, run over |
   | **G4** 🎯 | shot budgets, target counts, the bot curve | aim input and guide, layouts, the catch bucket |
   | **G5** ⚡ | the tempo ramp, reaction windows, grace period | the input, hazard types and telegraphs |
   | **G6** 🧠 | level sizes, par, the solver curve | the rule set, constraints, hints |

   **Audio/VFX** in every category: `juice-artist` / `sound-designer`
   (the move, the cascade/merge/shot, combos, clears, failure).

3. **The interactive part (questions)** — examples by system:

   `board-rules` (G1):
   - The move rule and the minimum group; diagonals or not.
   - What a 4, a 5 and an L/T create; what special + special does.
   - The dead-board reshuffle and how it is shown.

   `deal-generator` (G2):
   - Generate-then-verify with the solver, or deal backwards from a solved state?
   - How par grows; how many plausible wrong moves a level should offer.

   `tier-chain` (G3):
   - The game's object ladder from the smallest piece to the hero object.
   - Spawn weights for the lowest tiers; the milestone tiers that unlock things.

   `tempo-ramp` (G5):
   - Start and cap of speed/interval/reaction window; time to the cap; grace period.
   - Which hazards appear at which tempo, and how each is telegraphed.

   `progression` (any):
   - Star thresholds; world unlocks; achievements and their known rewards; album pages and the
     milestone that fills each; the daily challenge.

4. **Generating the draft**:
   Write it to `design/gdd/[system-name].md`, in English.
   Required fields:
   - *Balance impact* — how the system moves the model's curve (pass rate / par / run length)
   - *Visual feedback* — what feedback the player gets when it fires
   - *Edge cases* — boundary situations (no legal move, tap spam, a pause mid-move)
   - *Config keys* — which fields will appear in the balance config

5. **Next steps**:
   - `/balance-check` — mandatory if the system touches the model's numbers. A new mechanic
     without a simulator records its config, thresholds and headless-bot plan now; the actual
     engine bot must PASS after implementation and before integration/release.
   - Call `/team-dev` to program the system
