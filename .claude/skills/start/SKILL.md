---
name: start
description: "The introductory skill. Presents the casual game studio (casino-grade looks, never gambling gameplay), its six categories and 28 archetypes, and points the user in the right direction. Run it at the beginning of any new project."
user-invocable: true
allowed-tools: Bash, Read
---

# `flutter-gambling-studio` — meet the studio

Hello! You are in a studio that specialises in building **casual mini-games** with
**Flutter + Flame** — games that can look as rich as casino key art, or exactly like a reference
you bring, and play as skill games scored in points.

We make match-3 and link boards, tile trays and sort puzzles, merge games, bubble shooters and peg
clearers, runners and stackers, and logic puzzles. We never make gambling games: no bets, no money
of any kind, no rewards left to chance. Ask for a slot and you get the slot's world as a casual
game (a Zeus slot becomes a Zeus link-chain board).

> **Rule 1**: everything here is produced in **English** — the conversation, the design
> documents, the code and the game's own copy. If you want the game itself in another language,
> say so explicitly and the player-facing text will use it.
>
> **Rule 2**: **never gambling** — points, stars and unlocks only
> (`.claude/rules/no-gambling.md`). No age gate is needed: these are casual games.

### The main commands to get started

| Command | What it does |
|---------|--------------|
| `/brainstorm` | Step-by-step idea generation. Together we pick the category, the archetype, the balance model, the theme and the "juice". |
| `/auto-idea` | Instantly generates a complete concept (no questions) from the 28 archetypes A–AB, building a Design Signature, state recipes, and anti-repeat comparison. |
| `/autocreate` | Builds the game from concept to a finished Flutter project in one session. |
| `/continue-project` | Continue an existing game from where you stopped. Your usual entry point. |

### The six game categories

| ID | Category | What it is | Balance model |
|----|----------|------------|---------------|
| **G1** 🧩 | Match & Cascade | Swap, link or tap matching symbols; cascades | B1 board simulation |
| **G2** 🗂 | Tile & Sort | Tile trays, pairs, sort puzzles, patience | B2 solvable deals |
| **G3** 🔷 | Merge & Place | Slide/drop merges, block placement | B3 run length |
| **G4** 🎯 | Aim & Physics | Bubbles, pegs, bricks, knockdowns | B4 shot simulation |
| **G5** ⚡ | Arcade Reflex | Runners, stackers, catchers, slicers, flyers | B5 reflex ramp |
| **G6** 🧠 | Logic & Progression | Paths, pipes, unblock, memory, logic grids | B6 solver curve |

### The archetype catalogue (A–AB)

| ID | Name | Mechanic | Cat. |
|----|------|----------|------|
| A | Jewel Parade | Swap match-3 with specials | G1 |
| B | Storm Link | Link chain, bolts for long chains | G1 |
| C | Pop Carnival | Tap blast of connected groups | G1 |
| D | Gear Garden | Rotate match | G1 |
| E | Relic Tray | Triple tile tray | G2 |
| F | Temple Pairs | Mahjong-style pair tiles | G2 |
| G | Potion Shelf | Sort puzzle | G2 |
| H | Crown Peaks | TriPeaks card patience | G2 |
| I | Crown Ladder | Slide merge up a tier chain | G3 |
| J | Fruit Tower | Suika-style drop merge | G3 |
| K | Brick Garden | Block place, line clears | G3 |
| L | Treasure Workshop | Merge grid with goals | G3 |
| M | Cloud Pop | Bubble shooter | G4 |
| N | Prism Pegs | Peg clear with a catch bucket | G4 |
| O | Palace Bricks | Brick breaker | G4 |
| P | Tower Toppler | Knockdown | G4 |
| Q | Honey Path | Draw & guide | G4 |
| R | Chicken Dash | Lane runner | G5 |
| S | Sky Stack | Stacker | G5 |
| T | Star Catch | Catcher | G5 |
| U | Lantern Slice | Slicer | G5 |
| V | Thunder Glide | One-tap flyer | G5 |
| W | Wheel Strike | Target throw | G5 |
| X | Rune Paths | Connect paths | G6 |
| Y | Lightning Circuit | Rotate pipes | G6 |
| Z | Vault Slide | Unblock | G6 |
| AA | Mask Memory | Memory match | G6 |
| AB | Oracle Grid | Logic grid (no guessing) | G6 |

> Screen composition is planned per screen/state using the **layout grammar**
> (`.claude/docs/layout-archetypes.md`). Interaction and presentation come from the
> **Design Signature**, and the Similarity Check prevents reskinned repeats.
> One archetype + different world DNA, Design Signature, and state recipes = different games.
>
> The full category reference: `.claude/docs/game-categories.md`.

### The team of specialists

You are served by specialised agents:
- **`balance-designer`** — owner of the balance model: level curves, budgets, tempo ramps, stars.
- **`game-designer`** — designs the rules, goals, specials, progression and screens.
- **`mechanics-programmer`** — writes the pure rules engine with a seeded `GameRng` on Flame `1.18.x`.
- **`juice-artist`** — makes matches, cascades, combos and clears feel juicy.

***

**Where shall we start?** Type `/brainstorm` to build a game interactively,
`/auto-idea` to generate a concept instantly, or `/autocreate` for a fast start.
