# Quick start

Welcome to the **Flutter Casual Game Studio** — a studio for casual mini-games with casino-grade
looks: match-3 and link boards, tile trays and sort puzzles, merge games, bubble shooters and peg
clearers, runners and stackers, logic puzzles.

Here you act as the **studio director**, and the AI agents are your team.
Your job is to make the decisions; the team handles the rest.

> **IMPORTANT**: all work in the studio is produced in **English** — the conversation, the
> design documents, the code and the game's own copy. If you want the game itself in another
> language, say so explicitly and the player-facing text will use it.
>
> **Never gambling.** Games may look like slot key art, but nobody bets, there is no money of any
> kind, and no reward is left to chance — points, stars and unlocks only
> (`.claude/rules/no-gambling.md`). Ask for "a Joker slot" and you get a Joker tap-blast game.

## The six categories the studio works in

| ID | Category | Examples |
|----|----------|----------|
| G1 🧩 | Match & Cascade | swap match-3, link chain, tap blast, rotate match |
| G2 🗂 | Tile & Sort | triple tile tray, mahjong-style pairs, sort puzzle, TriPeaks patience |
| G3 🔷 | Merge & Place | 2048-style slide merge, Suika-style drop merge, block place, merge grid |
| G4 🎯 | Aim & Physics | bubble shooter, peg clear, brick breaker, knockdown, draw & guide |
| G5 ⚡ | Arcade Reflex | lane runner, stacker, catcher, slicer, one-tap flyer, target throw |
| G6 🧠 | Logic & Progression | connect paths, rotate pipes, unblock, memory match, logic grid |

The full reference is `.claude/docs/game-categories.md`.

## 🚀 How do I start a new game?

There are two paths:

### Path 1: automatic (I want a finished game)
Just type:
```bash
/autocreate
```
The studio picks an archetype out of 28 (A–AB across the six categories), declares a balance
model, writes the design, draws the assets, writes the code, runs the balance simulation and sets
up `pubspec.yaml`.

### Path 2: manual (I want to build a unique game)

**Step 1. Idea and category**
```bash
/brainstorm
```
Together with the agent you choose the category, the archetype, the theme and the unique
piece of "juice".

**Step 2. Break it into components**
```bash
/map-systems
```
The studio produces a build plan with a map of systems.

**Step 3. Detailed mechanic design**
```bash
/design-system board-rules        # G1: matching, cascades, specials, reshuffle
/design-system deal-generator     # G2: solvable deals and par
/design-system tier-chain         # G3: the merge ladder and spawn table
/design-system tempo-ramp         # G5: speed, spawn interval, reaction windows
```
`balance-designer` and `game-designer` step in and tune the curve for your category.

**Step 4. Write the code**
```bash
/team-dev "Implement the game core from our concept"
```
This orchestrates `mechanics-programmer` (the rules engine) and `juice-artist` (animation).

---

## 👥 Your team (the agents)

| Specialist | Who to call | What they do |
|------------|-------------|--------------|
| Balance designer | `@balance-designer` | Owner of the balance model: level curves, budgets, tempo ramps, stars |
| Game designer | `@game-designer` | GDD: rules, goals, specials, progression, screens |
| Mechanics programmer | `@mechanics-programmer` | The pure rules engine, seeded `GameRng`, logic before animation, Forge2D |
| Meta systems | `@meta-systems-programmer` | Save, progression, achievements, collection album, ads/iap abstractions |
| VFX artist | `@juice-artist` | Match, cascade, combo and clear celebrations, particles |
| UI/UX | `@ui-programmer` | Every Flutter screen, HUD, level map, anti-slop design |
| Sound | `@sound-designer` | Tap, match, cascade, combo, clear, fail |

---

## 🛠 Useful commands along the way

Generating assets:
```bash
/generate-asset symbol crown      # a board tile
/generate-asset sprite bubble-red # a ball / piece / target
```

Check the game's balance:
```bash
/balance-check                    # picks the model B1–B6 from the game's category
```

Directly, when you need it quickly:
```bash
python3 tools/simulate_balance.py --model b1 --config design/balance/level-config.json
python3 tools/simulate_balance.py --selftest   # the reference configs for the built-in models
```

Add a feature to a finished game:
```bash
/add-feature "Add a colour-bomb special"          # G1
/add-feature "Add an undo with three charges"     # G2
/add-feature "Add a daily challenge on a seeded level"
```

Take a break and continue tomorrow:
```bash
/continue-project
```

Ready to start? Type `/start` right now.
