# Game categories — the studio's canonical reference

> **The studio builds casual mobile games, never gambling games.** A game may *look* like premium
> casino key art — jewel-toned symbols, gold trim, jokers, crowns, Zeus, sevens, glossy gems — or
> reproduce a reference's look exactly. Its *gameplay* is always one of the casual mechanics below,
> scored in points. `.claude/rules/no-gambling.md` is the hard gate that keeps it that way.
>
> This document is the single source of truth for the taxonomy. It is referenced by `CLAUDE.md`,
> `/auto-idea`, `/brainstorm`, `/autocreate`, `/balance-check`, `/design-system`, `/gate-check`
> and `/release-checklist`.

## What "a studio game" means

A game belongs to this studio when:

- **The player's skill and decisions produce the result.** Randomness only sets up the puzzle —
  a board fill, a spawn order, a piece queue, a deal — and the player then plays it. Nothing is
  decided by a draw that the player merely watches.
- **Points, not money.** The game counts score, stars, levels, streaks, best times and unlocks.
  There is no currency of any kind — real or virtual, "coins", "chips", "gems", "credits" — no
  balance, no wallet, no price and no shop that spends one.
- **Nothing is staked.** The player never risks points, lives or progress on a chance outcome, and
  never chooses a bet size, a risk level or a cash-out moment.
- **Rewards are deterministic.** A level cleared, a milestone reached or an achievement earned
  grants a known reward. There are no loot boxes, capsules, mystery chests, prize wheels, scratch
  reveals, card packs or daily spins.

**The look is free, the mechanic is not.** Casino-style art direction is welcome: a match-3 board
dressed as golden reel frames, cherry/seven/bell/gem tiles, a jester host, a crown, a lightning
god. Casino *mechanics* are not — no slots, reels that spin for an outcome, roulette, poker,
blackjack, bingo, keno, crash, mines-for-multipliers, plinko-for-prizes, pachinko, coin pushers,
gacha. When a request or a reference points at one of those, translate it (see "Translating a
gambling ask" below).

---

## The six categories

| ID | Category | Icon | Core | Balance model | Archetypes |
|----|----------|------|------|---------------|------------|
| **G1** | Match & Cascade | 🧩 | Clear groups of matching symbols on a grid; the board refills | **B1** board simulation | A–D |
| **G2** | Tile & Sort | 🗂 | Clear or sort a dealt layout; every deal is solvable | **B2** solvable deals | E–H |
| **G3** | Merge & Place | 🔷 | Combine or place pieces to grow tiers and keep space open | **B3** run length | I–L |
| **G4** | Aim & Physics | 🎯 | Aim, shoot, bounce or draw; physics resolves the shot | **B4** shot simulation | M–Q |
| **G5** | Arcade Reflex | ⚡ | Timing and reflex against a rising tempo | **B5** reflex ramp | R–W |
| **G6** | Logic & Progression | 🧠 | Handcrafted-feel logic levels with one clean solution path | **B6** solver curve | X–AB |

The models and their thresholds live in `.claude/docs/balance-models.md`.

---

## G1 — Match & Cascade 🧩

**What it is.** A grid of themed symbols. The player swaps, links or taps to clear matching
groups; the pieces above fall and new ones drop in. Levels set a move limit and a goal (a score, a
number of one symbol collected, blockers cleared).

**Feel references:** Candy Crush Saga, Bejeweled, Two Dots, Toon Blast, Hexic.

**Core loop:** read the board → choose a move → clear → cascade/refill → progress toward the level
goal → level complete with 1–3 stars → next level on the map.

**Required systems:** a pure board engine (match detection, gravity, refill, cascades, specials),
dead-board detection with an automatic reshuffle, level data (board size, symbol kinds, moves,
goals, blockers), star thresholds, a level map with unlock-by-progress.

**Balance model:** **B1** — the board rules are simulated with a player bot over every level; pass
rates must form an onboarding plateau followed by a ramp with breathers and no walls.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **A** | Swap Match-3 | Swap two neighbours to line up 3+; 4, 5, L and T shapes create specials | Special + special combos that sweep rows, columns and colours |
| **B** | Link Chain | Drag a path through 3+ adjacent same symbols (diagonals optional) | Chain length raises a visible combo multiplier on the points |
| **C** | Tap Blast | Tap a connected group of 2+ same symbols to pop it | 5+ groups leave a rocket/bomb; clearing big groups is the skill |
| **D** | Rotate Match | Rotate a small cluster (2×2 or a hex trio) to form matches | Rotations that chain into cascades several steps deep |

---

## G2 — Tile & Sort 🗂

**What it is.** A layout is dealt — tiles stacked in layers, containers of mixed pieces, a
patience deal — and the player clears or sorts it. Every shipped deal is solvable; the challenge
is finding the order.

**Feel references:** Tile Master, Zen Match, Mahjong solitaire, Ball Sort / Water Sort, TriPeaks.

**Core loop:** survey the layout → pick the next piece → avoid locking yourself out → clear the
layout → stars by moves or time → next deal.

**Required systems:** a deal generator that only ships solvable deals (generate-then-verify with a
solver, or deal backwards from a solved state), an undo/hint system, a tray or foundation model,
level data (layout, piece kinds, depth), a solver used in tests.

**Balance model:** **B2** — every generated deal is solved by the reference solver; minimum-move
(par) counts ramp through the levels without walls.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **E** | Triple Tile Tray | Tap free tiles off a layered pile into a 7-slot tray; three alike clear | Tray pressure: the eighth unmatched tile ends the attempt |
| **F** | Pair Tiles | Remove free matching pairs from a layered layout (mahjong-style solitaire) | Layer reveals — clearing uncovers the next tier of the design |
| **G** | Sort Puzzle | Move pieces between containers until each holds one kind | Stacked pours: a move carries every matching top piece at once |
| **H** | Card Patience | TriPeaks/Pyramid solitaire: play a card one rank higher or lower onto the pile | Streak points for long runs; a patience game, never a casino table game |

---

## G3 — Merge & Place 🔷

**What it is.** Pieces arrive one by one — slid, dropped or placed — and equal pieces merge into
the next tier of the game's object chain, or full lines clear. The run lasts as long as the player
keeps space open. Endless by default, with milestone goals.

**Feel references:** 2048, Suika Game, Block Blast / 1010!, Merge Dragons (board only).

**Core loop:** see the next piece → place/slide/drop it → merge or clear → keep the board open →
beat the best score, reach the next tier milestone.

**Required systems:** a tier chain (the game's own object ladder, e.g. cherry → bell → seven →
crown), a spawn table, a next-piece preview, a run-over condition, milestone goals, best-score
persistence.

**Balance model:** **B3** — a player bot plays full runs; run length, reachable tiers and session
time must land in their windows.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **I** | Slide Merge | Swipe the grid; equal tiles merge into the next tier (2048-style) | The top tier is the game's hero object |
| **J** | Drop Merge | Drop objects into a container; equal objects merge on contact (Suika-style) | Physical, wobbly stacks and chain merges |
| **K** | Block Place | Place the offered pieces on a grid; full rows/columns clear | Multi-line clears grant a combo multiplier on points |
| **L** | Merge Grid | Drag equal items together on a board to evolve them toward level goals | The board fills over time; clever ordering keeps space |

---

## G4 — Aim & Physics 🎯

**What it is.** The player aims and releases; Forge2D (or a simple trajectory model) resolves the
shot. Levels are layouts of targets, pegs, bricks or structures with a limited number of shots.

**Feel references:** Bubble Witch / Bubble Shooter, Peggle, Arkanoid, Angry Birds, Cut the Rope.

**Core loop:** read the layout → aim (a trajectory guide helps) → release → physics plays out →
targets clear → level complete with stars by shots left.

**Required systems:** a fixed-timestep physics world (Forge2D) or deterministic trajectory model,
an aim guide, shot count, level layouts, a body cap for performance.

**Balance model:** **B4** — the game's own headless physics runs a player bot (aim with noise)
through every level; pass rates and shots-to-clear follow the level-curve thresholds.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **M** | Bubble Shooter | Aim and shoot to form groups of 3+; unsupported clusters drop | Bank shots off the walls with a visible guide |
| **N** | Peg Clear | Aim a ball through a peg field to clear all target pegs with limited balls | A moving catch bucket returns the ball — no prize buckets, no multipliers by slot |
| **O** | Brick Breaker | Paddle and ball; bricks drop power-ups | Multi-ball and themed bricks |
| **P** | Knockdown | Sling or throw projectiles to topple structures or clear targets | Chain collapses from one well-placed shot |
| **Q** | Draw & Guide | Draw lines or cut ropes to guide a falling object to its goal | Minimal-ink / minimal-cut star goals |

---

## G5 — Arcade Reflex ⚡

**What it is.** A short, repeatable run against a rising tempo: dodge, catch, slice, stack or
throw with good timing. Endless, with a best score and daily seeded runs.

**Feel references:** Crossy Road, Subway Surfers, Stack, Fruit Ninja, Flappy Bird, Knife Hit.

**Core loop:** start instantly → read the next threat → react → survive longer / score more → run
ends → instant retry → beat the best.

**Required systems:** a difficulty ramp (speed, spawn interval, reaction window) in config, a fair
start, hazard telegraphing, a best-score record, a daily seeded run.

**Balance model:** **B5** — a reaction-time model of an average player runs the ramp; first-run
length, early-death rate and ramp timing must land in their windows.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **R** | Lane Runner | Run or hop across lanes, dodging obstacles and collecting points | Themed lanes that change as distance grows |
| **S** | Stacker | Tap to drop a moving slab onto the tower; overhang is trimmed | Perfect drops restore width and build a streak |
| **T** | Catcher | Move to catch good falling items and dodge bad ones | Catch combos and rare golden items worth more points |
| **U** | Slicer | Swipe to slice thrown objects; avoid the hazards | Multi-slice combos in one swipe |
| **V** | One-Tap Flyer | Tap to rise through gaps; distance is the score | A themed flyer and parallax world |
| **W** | Target Throw | Throw knives/darts/arrows into a rotating target without hitting earlier ones | Boss targets with changing rotation patterns |

---

## G6 — Logic & Progression 🧠

**What it is.** Pure-logic levels, each with a clean solution. Difficulty comes from size, rules
and interaction between constraints, not from luck.

**Feel references:** Flow Free, Infinity Loop / pipes, Unblock Me, Memory Match, Minesweeper-style
logic, nonograms.

**Core loop:** read the constraints → deduce → act → the solution completes → stars by moves or
time → next level; hints are earned, never bought.

**Required systems:** a level generator with a solver (every level provably solvable without
guessing), par moves, hints earned by progress, a level map.

**Balance model:** **B6** — the solver proves every level and measures par; a player bot measures
completion; the curve follows the level-curve thresholds.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **X** | Connect Paths | Connect matching pairs with non-crossing paths that fill the board | Themed pairs (the game's symbols) and bridges |
| **Y** | Rotate Pipes | Rotate tiles to complete a circuit or light path | Light/energy flowing through the finished path |
| **Z** | Unblock | Slide blocks to free the key piece | Par-move stars |
| **AA** | Memory Match | Flip cards to find pairs within a move or time budget | Consecutive-pair combos for points |
| **AB** | Logic Grid | Deduce hidden cells from numeric clues (minesweeper-style, no guessing) or nonogram clues | Every level solvable by logic alone — the generator proves it |

---

## The full archetype index A–AB

| Category | Archetypes |
|----------|------------|
| G1 Match & Cascade 🧩 | **A** swap match-3 · **B** link chain · **C** tap blast · **D** rotate match |
| G2 Tile & Sort 🗂 | **E** triple tile tray · **F** pair tiles · **G** sort puzzle · **H** card patience |
| G3 Merge & Place 🔷 | **I** slide merge · **J** drop merge · **K** block place · **L** merge grid |
| G4 Aim & Physics 🎯 | **M** bubble shooter · **N** peg clear · **O** brick breaker · **P** knockdown · **Q** draw & guide |
| G5 Arcade Reflex ⚡ | **R** lane runner · **S** stacker · **T** catcher · **U** slicer · **V** one-tap flyer · **W** target throw |
| G6 Logic & Progression 🧠 | **X** connect paths · **Y** rotate pipes · **Z** unblock · **AA** memory match · **AB** logic grid |

---

## Translating a gambling ask

Users and references often name a casino game. The studio keeps the *look* and the *feel of the
moment* and replaces the mechanic with the nearest casual one. Record the translation in the
concept's Classification block (`Reference gameplay`).

| Asked for | Build instead | Why it keeps the feel |
|-----------|---------------|-----------------------|
| Slot / reels / "spins" / scatter-pays / cluster pays | **G1-A** swap match-3, **G1-B** link chain or **G1-C** tap blast on a board dressed as the reel frame, with the slot's symbol cast as tiles | The same symbols lining up and cascading, earned by the player's move |
| Hold & Spin / link & win | **G1-B** link chain with sticky special tiles | Collecting and linking the special symbols |
| Plinko / pachinko | **G4-N** peg clear | The same peg field and bouncing balls, aimed by the player |
| Coin pusher / dozer | **G4-P** knockdown or **G3-J** drop merge | Pushing and tumbling a heap of the game's objects |
| Crash | **G5-V** one-tap flyer | The climb and the tension, measured in distance |
| Mines | **G6-AB** logic grid (numbers reveal adjacent hazards; no guessing) | Revealing cells with tension, solved by deduction |
| Dice | **G3-I** slide merge or **G3-K** block place with dice-pip tiles | Dice as objects to combine, not to roll for a payout |
| Hi-lo / cards / poker / blackjack | **G2-H** card patience (TriPeaks/Pyramid) | Higher/lower card play as a patience puzzle, never against a dealer |
| Tower climb | **G5-S** stacker | Climbing floor by floor on timing |
| Roulette / prize wheel / wheel of fortune | **G5-W** target throw at the rotating wheel | The spinning wheel as a skill target |
| Keno / bingo / lottery | **G6-AB** logic grid or **G6-AA** memory match | Numbers and cards on a grid, solved rather than drawn |
| Scratch cards | **G6-AA** memory match or a **G6** reveal-and-deduce level | Revealing hidden faces with purpose |
| Gacha / loot box / card packs / case opening / capsule | **G6-AA** memory match with a deterministic **collection album** filled by clearing levels and milestones | The joy of a new collectible, earned by progress |

If a request is nothing *but* a gambling mechanic ("a roulette game", "a slot machine"), still
build the translated casual game in that theme and say so in the concept and the final report.

---

## How the archetype is chosen (in `/auto-idea` and `/autocreate`)

The archetype sets the **mechanic**. So that games of the same archetype do not repeat, two
independent axes are cycled on top of it:

```
Game = Archetype (WHAT the mechanic is)
     × Per-screen layout recipes (HOW each state is composed — layout-archetypes.md)
     × Design Signature (HOW interaction and presentation behave — anti-slop-design.md)
```

A pseudo-random choice that avoids repeating the previous one:

```python
import time
ARCHETYPES = [
    "A", "B", "C", "D",             # G1
    "E", "F", "G", "H",             # G2
    "I", "J", "K", "L",             # G3
    "M", "N", "O", "P", "Q",        # G4
    "R", "S", "T", "U", "V", "W",   # G5
    "X", "Y", "Z", "AA", "AB",      # G6
]
archetype = ARCHETYPES[int(time.time()) % len(ARCHETYPES)]
```

A reference request does not roll: its family entry in `game-concept-examples.md` names the
archetype (see `tools/reference_detect.py` → `casual_mechanic`).

> **Unique Mode.** If the user asks for a unique mechanic, invent a new one at the seam of two
> categories ("a link chain whose cleared symbols drop into a merge ladder", "a stacker whose
> slabs are sorted by colour"). It must stay a casual skill mechanic, pass
> `.claude/rules/no-gambling.md`, and declare one balance model before production begins.

## The mandatory concept block

Every `design/gdd/game-concept.md` MUST open with a classification block — downstream phases read
it literally:

```markdown
## Classification
- **Category**: G1 | G2 | G3 | G4 | G5 | G6 — [category name]
- **Archetype**: [A–AB | UNIQUE] — [name]
- **Balance model**: [B1 | B2 | B3 | B4 | B5 | B6] — [name]
- **Balance config**: design/balance/[level-config | endless-config].json
- **Target curve**: [e.g. "L1–3 ≥ 85% pass, final world 30–45%" | "median first run 60–90 s"]
- **Scoring**: points only — [how points are earned; what stars/milestones unlock]
- **Reference gameplay**: [n/a | the reference's own casual gameplay | the reference is a casino
  game → translated to <archetype> (look kept, mechanic replaced)]
- **No-gambling check**: no wagers, no currency, no chance-based rewards — `.claude/rules/no-gambling.md`
- **Game language**: English (default) | [another language, only if the user explicitly asked]
```

Without this block, `/gate-check concept` returns FAIL.
