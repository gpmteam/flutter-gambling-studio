---
name: auto-idea
description: "Autonomously generates a ready-made concept for a casual game (without asking the user). Selects from 28 A-AB archetypes in six categories (match & cascade, tile & sort, merge & place, aim & physics, arcade reflex, logic & progression) or invents a unique casual mechanic. Casino-grade or reference-matched looks; never gambling gameplay. Builds a mechanic-derived Design Signature, per-screen layout recipes, and a nearest-neighbor Similarity Check so games do not become reskinned copies. Includes Classification (category + balance model + no-gambling check), full MVP screen map, UX flow and craft-level tokens."
argument-hint: "[--list] | [--archetype A-AB] | [--category G1-G6]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# Auto-Idea - Automatic Casual Game Idea Generator

Read `.claude/docs/visual-context.md` before planning or reviewing visuals. For a matching
new-game request, inspect the relevant `examples-games/` previews and read
`.claude/docs/game-concept-examples.md`. Carry the lead kind, references/adaptations, exact
board topology, Joker expression (when relevant), and verified combo-marker meanings from
the concept into the art direction, asset manifest and prompts. An unspecified match game uses a
7×8 board; store gameplay placement is flexible and object-led games need no invented character.
The named requests Book of Ra, Royal Joker (or a plain Joker), Joker Jewels, Shining Crown,
and Plinko must use the preview mapping in that document, including the casual mechanic each
family is built as; Joker Jewels resolves to every file in `examples-games/joker-jewels/` and to
the swap match-3 board, not to the Royal Joker row. For an exact family, recreate what the preview
shows — theme, character, symbol cast, palette, frame and composition are matched, not
reinterpreted, and Variety Dimensions are not scrolled. Royal Joker is a loose reference: keep its
jester, and design the background, symbols and composition for the game — do not copy the
previews' backdrop every time ("Loose references" in that document). Follow the source-quality and
branding limits in `game-concept-examples.md`. Never add a character to Shining Crown or Plinko.

Don't ask the user questions! Create `design/gdd/game-concept.md` completely autonomously.

> **CASUAL GAMES, NEVER GAMBLING.** The studio makes casual skill games scored in points. Their
> look may be casino-grade key art; their gameplay may never be a wager, a currency or a
> chance-based reward (`.claude/rules/no-gambling.md`). Any idea must fall into one of six
> categories and declare a balance model. Canonical reference: `.claude/docs/game-categories.md`.
> If the brief names a gambling mechanic, build its casual translation ("Translating a gambling
> ask") in the requested theme and say so in the concept.
>
> **ANTI-SLOP**: Read `.claude/rules/anti-slop-design.md` (principle + Craft Fundamentals)
> `.claude/docs/mobile-first-contract.md`, and `.claude/docs/layout-archetypes.md` before generation.
> The concept MUST include a mechanic-derived Design Signature, state composition map, per-screen
> layout recipes, and Similarity Check. For a mapped named request the signature and composition
> are the reference's, recorded from it rather than invented — matching it is the goal, not a slop
> risk. "Casino-grade look" ≠ "dark neon and gold" every time: a gem match-3 can be warm and bright,
> a sort puzzle pastel, a logic game strictly typographic. Vary both style and composition.
> Every concept is a portrait phone game played by touch (`.claude/docs/mobile-first-contract.md`):
> design each screen for a phone held upright, and plan no tablet, desktop or landscape layout.

## Catalog of Archetypes (A–AB)

### 🧩 G1 – Match & Cascade (A–D) · B1 model · board simulation

**A – Swap Match-3 "Jewel Parade"**
> Swap neighbours to line up 3+; 4, 5, L and T shapes make specials; cascades refill the board. Feature: special + special combos that sweep rows, columns and colours.

**B – Link Chain "Storm Link"**
> Drag a path through 3+ adjacent same symbols; longer chains spawn bolts that clear a column. Feature: chain length raises a visible points multiplier.

**C – Tap Blast "Pop Carnival"**
> Tap a connected group of 2+ same symbols to pop it; 5+ leaves a rocket. Feature: planning big groups is the skill.

**D – Rotate Match "Gear Garden"**
> Rotate a 2×2 cluster to form matches; rotations chain into cascades. Feature: rotation puzzles several steps deep.

### 🗂 G2 – Tile & Sort (E–H) · B2 model · solvable deals

**E – Triple Tile Tray "Relic Tray"**
> Tap free tiles off a layered pile into a 7-slot tray; three alike clear. Feature: tray pressure — the eighth unmatched tile ends the attempt.

**F – Pair Tiles "Temple Pairs"**
> Remove free matching pairs from a layered layout. Feature: clearing reveals the next layer of the design.

**G – Sort Puzzle "Potion Shelf"**
> Pour pieces between containers until each holds one kind. Feature: stacked pours carry every matching top piece.

**H – Card Patience "Crown Peaks"**
> TriPeaks: play a card one rank higher or lower; clear the peaks. Feature: streak points — a solo patience puzzle, never a casino table game.

### 🔷 G3 – Merge & Place (I–L) · B3 model · run length

**I – Slide Merge "Crown Ladder"**
> Swipe the grid; equal tiles merge up the game's object chain to the hero object. Feature: the top tier is the game's crown.

**J – Drop Merge "Fruit Tower"**
> Drop objects into a container; equal objects merge on contact. Feature: wobbly physical stacks and chain merges.

**K – Block Place "Brick Garden"**
> Place the offered pieces on a grid; full rows/columns clear. Feature: multi-line clears grant a combo multiplier on points.

**L – Merge Grid "Treasure Workshop"**
> Drag equal items together to evolve them toward level goals. Feature: the board fills over time; ordering keeps space.

### 🎯 G4 – Aim & Physics (M–Q) · B4 model · shot simulation

**M – Bubble Shooter "Cloud Pop"**
> Aim and shoot to form groups of 3+; unsupported clusters drop. Feature: bank shots with a visible guide.

**N – Peg Clear "Prism Pegs"**
> Aim a ball through a peg field to clear all target pegs with limited balls. Feature: a moving catch bucket returns a ball.

**O – Brick Breaker "Palace Bricks"**
> Paddle and ball; bricks drop power-ups. Feature: multi-ball and themed bricks.

**P – Knockdown "Tower Toppler"**
> Sling projectiles to topple structures. Feature: chain collapses from one well-placed shot.

**Q – Draw & Guide "Honey Path"**
> Draw lines or cut ropes to guide a falling object to its goal. Feature: minimal-ink star goals.

### ⚡ G5 – Arcade Reflex (R–W) · B5 model · reflex ramp

**R – Lane Runner "Chicken Dash"**
> Hop across lanes of hazards; points by distance and pickups. Feature: themed lanes that change with distance.

**S – Stacker "Sky Stack"**
> Tap to drop a moving slab; overhang is trimmed. Feature: perfect drops restore width and build a streak.

**T – Catcher "Star Catch"**
> Move to catch good falling items, dodge bad ones. Feature: catch combos and rare golden items.

**U – Slicer "Lantern Slice"**
> Swipe to slice thrown objects; avoid hazards. Feature: multi-slice combos.

**V – One-Tap Flyer "Thunder Glide"**
> Tap to rise through gaps; distance is the score. Feature: a themed flyer and parallax world.

**W – Target Throw "Wheel Strike"**
> Throw darts at a rotating target without hitting earlier ones. Feature: boss targets with changing rotation.

### 🧠 G6 – Logic & Progression (X–AB) · B6 model · solver curve

**X – Connect Paths "Rune Paths"**
> Connect matching pairs with non-crossing paths that fill the board. Feature: bridges and themed pairs.

**Y – Rotate Pipes "Lightning Circuit"**
> Rotate tiles to complete a circuit. Feature: energy flows through the finished path.

**Z – Unblock "Vault Slide"**
> Slide blocks to free the key piece. Feature: par-move stars.

**AA – Memory Match "Mask Memory"**
> Flip cards to find pairs within a move budget. Feature: consecutive-pair combos.

**AB – Logic Grid "Oracle Grid"**
> Deduce hidden cells from numeric clues, no guessing. Feature: every level solvable by logic alone.

## Procedural Unique Generation (Unique Mode)

If the `--archetype` flag is not passed or the user has explicitly requested a "unique idea", you
**MAY** invent a new casual mechanic that does not coincide with A–AB — it must stay a skill
mechanic scored in points and fall into one of six categories.

The best unique ideas live at the intersection of two categories:
- "A link chain whose cleared symbols drop into a merge ladder" (G1 × G3)
- "A stacker whose slabs must be sorted by colour" (G5 × G2)
- "A peg-clear shot whose targets form a logic picture" (G4 × G6)
- "A tile tray where each triple rotates a pipe on a circuit board" (G2 × G6)

It is prohibited to invent anything whose core is a wager, a currency or a chance-based reward —
even with points instead of money. A wager on points is still a wager.

**The category and balance model are recorded in the "Classification" block BEFORE the other sections.**

## Variety Dimensions - why the same archetype ≠ the same game

> **Not for a mapped named request.** When the request maps to a local preview
> (`.claude/docs/game-concept-examples.md`), skip this whole section: the setting, mood, palette,
> brightness, composition and art treatment are all read off the reference and matched.
> Scrolling these axes is exactly the drift that section forbids. Variety Dimensions exist for
> concepts the studio invents on its own.

The archetype sets the MECHANICS. To make two games of the same archetype look and feel different,
**scroll these axes and select values that are different from the last game**. Record your choice in the concept.

| Axis | Examples of meanings (choose varied) |
|-----|------------------------------------------|
| **Setting/world** | underwater, space, ancient Egypt, Olympus, carnival, enchanted forest, candy land, royal treasury, wild west, zen garden, steampunk, myths, coffee shop |
| **Mood/mood** | energetic, cozy, epic, ironic, mystical, upbeat, meditative |
| **Palette family** | warm earthy, jewel tones, pastel, monochrome+1 accent, royal gold and purple, burnt retro |
| **Brightness** | light / dark / twilight - NOT always dark |
| **Interaction/composition signature** | field framing, controls, HUD behavior, menu, overlays, phone-height adaptation |
| **Art finish and depth** | slot-style key-art 2.5D (the studio signature), crisp 2D illustration, hand-drawn, cut paper, shallow layers; use the mapped reference's actual finish when present |
| **Audience/tone** | relaxed casual, competitive score-chaser, children's, premium elegant, retro nostalgia |

> Goal: even two "A" match-3 games should look like DIFFERENT games - one warm Egyptian light,
> another cool Olympus sky, with different interaction and composition signatures.
>
> **Against "casino-slop"**: neon + black + gold IS a default, not a style. Casino-grade *assets*
> (jewels, gold trim, glossy symbols) are the studio look; a dark-neon *interface* on every game is not.

## Work algorithm

1. Read the flag:
   - `--list` — display a table of archetypes A–AB, grouped into categories G1–G6.
   - `--category G1..G6` - choose an archetype randomly INSIDE this category.
   - `--archetype A..AB` - take a specific one.
2. Otherwise, if the request maps to a reference family or names a mechanic (casual or a
   gambling ask to translate), use that mechanic (`tools/reference_detect.py` → `mechanic`).
3. Otherwise, choose an archetype pseudo-randomly, **without repeating the previous one**:
   ```python
   import time
   ARCHETYPES = ["A","B","C","D",                 # G1
                 "E","F","G","H",                 # G2
                 "I","J","K","L",                 # G3
                 "M","N","O","P","Q",             # G4
                 "R","S","T","U","V","W",         # G5
                 "X","Y","Z","AA","AB"]           # G6
   archetype = ARCHETYPES[int(time.time()) % len(ARCHETYPES)]
   ```
4. **Define the category and balance model** of the archetype by
   `.claude/docs/game-categories.md`. This is the first thing that will be included in the concept.
5. **Build and compare the Design Signature**: setting / mood / field framing / control topology /
   HUD behavior / information density / menu / overlays / palette / brightness / motion / art style.
   Compare it with recent or nearest games and change at least four material axes when the mechanic
   and reference do not justify repetition.
   **Skip this step entirely for a mapped named request** — take the setting, mood, palette,
   brightness, layout and art treatment from the reference instead, and record where each came
   from.
6. Create a detailed GDD in `design/gdd/game-concept.md`.

## Required sections of GDD

### Section 0: Classification (FIRST, mandatory)

> Without this block `/gate-check concept` returns FAIL, and downstream `/autocreate` phases
> cannot select the correct balance model. Fill it out literally in machine-readable form.

```markdown
## Classification
- **Category**: [G1 | G2 | G3 | G4 | G5 | G6] - [category name]
- **Archetype**: [A–AB | UNIQUE] - [name]
- **Balance model**: [B1 | B2 | B3 | B4 | B5 | B6] - [name]
- **Balance config**: design/balance/[level-config | endless-config].json
- **Target curve**: ["L1–3 ≥ 85% pass, final world 30–45%" | "median first run 60–90 s" | …]
- **Scoring**: points only — [how points are earned; what stars/milestones unlock]
- **Reference gameplay**: [n/a | reused | casino game → translated to <archetype>]
- **No-gambling check**: no wagers, no currency, no chance-based rewards, no age gate
- **Product target**: portrait phone game (Android/iOS, portrait-locked, touch only); Web is the preview host
```

### Section 1: Overview
- Title, category, archetype, one sentence
- Target audience
- Unique Selling Proposition (USP)

### Section 1.5: Reference Bar (quality bar calibration)

> The game competes with REAL games in the store, not with other demos.
> See `.claude/docs/quality-bar.md`.

- **2–3 named real category hits**:
  - G1 → Candy Crush Saga, Bejeweled, Two Dots, Toon Blast
  - G2 → Tile Master, Zen Match, Microsoft Mahjong, Water Sort Puzzle, Solitaire TriPeaks
  - G3 → 2048, Suika Game, Block Blast, Merge Mansion (board only)
  - G4 → Bubble Witch Saga, Peggle, Arkanoid, Angry Birds, Cut the Rope
  - G5 → Crossy Road, Stack, Fruit Ninja, Flappy Bird, Knife Hit
  - G6 → Flow Free, Infinity Loop, Unblock Me, Minesweeper-style logic
- For each: what do we borrow **IN FEELING** (the weight of a cascade, the snap of a merge, the
  arc of a shot, the rhythm of a run, the click of a solved circuit) — not the content and not the
  visuals
- **Hook**: one line — how OUR game differs from the references

### Section 2: Balance Profile

Filled in according to the model from Section 0. Thresholds — `.claude/docs/balance-models.md`.

**B1 (G1) — Board simulation:**
- Board size and symbol kinds per world, the move rule and minimum group
- Level goals (score / collect / blockers) and move budgets; where each new element arrives
- Target pass-rate band per world (onboarding ≥ 80%, final world 30–45%), breathers after spikes
- Specials and the combo formula; the dead-board reshuffle

**B2 (G2) — Solvable deals:**
- Layout size, piece kinds, layers/containers per level; the generator policy (verify/reverse)
- The par curve (first level ≤ 10 moves, ≤ 2× per step); undo and earned hints

**B3 (G3) — Run length:**
- Board size, the tier chain (topped by the hero object), the spawn table
- Target median session (2–12 min), the goal tier and milestone tiers

**B4 (G4) — Shot simulation:**
- Level layouts, target counts, shot budgets, the catch bucket, the body cap
- Target pass-rate band per world; the headless bot in `test/balance/bot_sim_test.dart`

**B5 (G5) — Reflex ramp:**
- Tempo start and cap (interval, reaction window), time to cap, grace period, lives
- Target median first run (30–180 s), ≤ 10% early deaths

**B6 (G6) — Solver curve:**
- Level size and constraints per world, the generator + solver, par, hint rules

### Section 2.5: Production Plan (which makes the game FULL and not a mini-demo)

> **This is the key section for the "full game".** One game loop = mini demo. The full game is
> loop + content (many levels/modes) + meta-loop (progression/achievements/collection) +
> monetization/telemetry points + the no-gambling gate. Describe them SPECIFICALLY — downstream
> phases of `/autocreate` (3.5 audio, 4 meta-systems agent, 4.5 content) build exactly this.

```markdown
## Production Plan

### Content Plan (volume of content - NOT one level)
- **Content model**: [levels in worlds | endless with milestones | daily seeded levels] - what suits the mechanic
- **Number**: [for example, 36 levels in 3 worlds | endless + 10 milestone tiers]
- **Parameters per content unit** (what changes from level to level): [kinds/budget/goal/blockers/tempo]
- **Progression curve**: [how the budgets, goals and elements ramp; link to the balance config]
- **Stars**: [how success is counted, 1–3 stars by score or moves-left thresholds]

### Game Modes (2-3 modes - replayability)
- **Mode 1 (main)**: [Levels — the map in order]
- **Mode 2**: [Daily challenge — one seeded level per day, a streak and a badge]
- **Mode 3 (optional)**: [Endless / Zen / Time attack — best score]

### Progression Model (meta-loop retention — no currency)
- **What unlocks**: [worlds at star thresholds, themes/backgrounds/card backs at milestones]
- **Player level / XP**: [yes/no; XP from points, never spent]
- **Stored progress**: [stars, best scores, unlocked levels, statistics, streaks]

### Boosters (optional)
- **Kinds**: [hammer, shuffle, +moves …] — granted in known counts by level rewards,
  achievements and milestones; never bought with a currency

### Achievements, Collection & Daily (retention hooks)
- **Achievements**: [5–12: id + condition + known reward]
- **Collection album**: [pages of the game's objects, each filled by a named milestone]
- **Daily challenge**: [the seeded level, the streak, the badge]

### Monetization Placements (integration points - implemented as abstractions/no-op)
- **Rewarded**: [+5 moves after running out | continue a run] - where exactly
- **Interstitial**: [between levels, frequency cap N]
- **IAP catalog**: [remove-ads, fixed theme packs — never currency, never random content]
- **Banner**: [yes/no; default off]

### Telemetry Events (taxonomy - implemented via AnalyticsService no-op)
- Key events: app_open, session_start/end, screen_view, level_start/complete/fail, move,
  booster_used, ad_shown/reward, achievement_unlocked, daily_challenge_cleared
- **Remote-config keys** (live-tuning): [ad frequency, difficulty offsets inside the verified windows]

### No-gambling check (MANDATORY - `.claude/rules/no-gambling.md`)
- No wagers, no currency/balance/shop/prices, no chance-based rewards, no casino controls or copy
- No age gate and no gambling disclaimer — the rating follows from the content (normally Everyone)
- [If the brief named a gambling mechanic: the casual translation and why it keeps the feel]
```

> Keep the volume realistic for auto-generation: content is DATA (JSON + parameters in
> GameConfig), rather than N handwritten screens. 36 levels = one GameScreen + a level list.
> This is the "full game" at the low cost of context.

### Section 3: Asset/World Design DNA, Game UI Read, and Design Signature (MANDATORY)

Read `.claude/rules/anti-slop-design.md`. Infer the interface from the player, repeated decision,
emotional arc, information pressure, world, reference, and platform constraints before selecting
visual tokens.

```markdown
## Game UI Read
- Player and session: [audience, posture, duration, one/two-handed]
- Core decision: [the repeated move the player makes]
- Emotional arc: [setup -> commitment -> anticipation -> result -> recovery/progression]
- Information pressure: [instant vs contextual information]
- World and tone: [specific world]
- Reference contract: [mapped reference, or named patterns borrowed]
- Memorable interface idea: [one spatial or interactive idea]

## Asset/World Design DNA
- Emotional core and visual world: [specific feeling, fiction, and subject cast]
- Silhouette and form language: [what makes objects recognizable at game size]
- Materials and surface behavior: [world materials, not generic UI effects]
- Illustration palette and value structure: [semantic/world roles; no fixed color count]
- Lighting and finish: [2D/2.5D choice, linework, texture and light from mapped reference or concept]
- Asset typography constraints: [wordmark/display character if relevant; body UI remains readable]

## Design Signature
- Field framing: [choice + why]
- Control topology: [choice + why]
- HUD behavior: [choice + why]
- Information density: [choice + why]
- Navigation model: [choice + why]
- Geometry: [choice + role rules]
- Surface/material: [choice + why]
- Type voice and semantic roles: [choice + readability rationale]
- Color/value logic and semantic roles: [choice + contrast rationale]
- Motion/feedback: [choice + what each family communicates]
- Depth model: [choice + why]
- Sound/haptics: [choice + why]
```

Do not require exactly five colors, two fonts, one accent, or one preset type scale. Define as many
semantic roles as this game's content needs, and no more.

### Section 3.5: State Composition and Layout Recipes (MANDATORY)

Use the independent axes in `.claude/docs/layout-archetypes.md`; do not choose one L1-L6 template.
Apply `.claude/docs/mobile-first-contract.md` and `.claude/docs/gameplay-screen-contract.md`.

```markdown
## State Composition Map
### Read / setup
- Job and attention order: [...]
- Persistent vs contextual information: [...]
- Recipe: [F# + C# + H# + O# + P#]
### Move / resolution
[same fields]
### Result / celebration or failure
[same fields]
### Recovery / progression
[same fields]

## Layout & Composition Direction
- Main Menu: [M# + O# + P#; why; `menu_role: dominant | supporting | absent` for the recorded
  `lead_kind`]
- Live Game: [state recipes; primary field alignment and any documented offset reason]
- How to play: [recipe; teaching and scan strategy]
- Level map/Collection/Profile: [recipe appropriate to category]
- Phone proof: [360x640, 360x800, 390x844, 430x932; P strategy for short and tall phones]

## Similarity Check
- Compared with: [up to three recent/nearest games]
- Repeated intentionally: [mechanic/reference/platform reasons]
- Material differences: [at least four Design Signature axes]
- Nearest-neighbor risk and correction: [...]
```

For a mapped reference, record its actual composition and skip anti-repeat drift. For an original,
changing only art and palette does not pass the Similarity Check.

### Section 4: MVP Screen Map

**NECESSARILY. Minimum 12 screens with description and UX flow. Give each screen a job and an
appropriate recipe; reuse structure only where consistency helps the player. No gambling
surfaces: no shop, no balance, no paytable/odds, no daily spin, no age gate.**

```markdown
## Screen Map

### Screen 1: Splash Screen
- What it shows: [animated game logo/symbol]
- Duration: 1.5-2 sec
- Go to: Main Menu

### Screen 2: Main Menu
- Elements: title, PLAY / Continue level N, level map, settings, how to play
- Background: [description of atmospheric background]
- Transitions: → Level Map, → Game Screen, → Settings, → Help

### Screen 3: Level Map / Mode Select
- Worlds and levels (locked / open / stars) or modes (Levels, Daily, Endless) with best scores
- Go to: → Game Screen (selected level/mode)

### Screen 4: Game Screen + HUD
- Playing field: [match board / tile pile + tray / merge grid / peg field / lanes / logic grid]
- HUD elements: score, the level goal and its progress, moves/shots/time left, pause
- Viewport composition: [dominant integrated field; compact control attachment; no nested window,
  large competing info card, or page-scrolling core loop]
- Overlays: combo callouts (3 tiers), level complete, level failed

### Screen 5: Pause
- Resume, Restart, How to play, Settings, Menu

### Screen 6: Level Complete
- Stars fill (1–3), score, new best, the host reacts; Next / Retry / Map

### Screen 7: Level Failed / Run Over
- Stylized overlay (NOT AlertDialog): what happened, how close the goal was
- Retry / optional rewarded "+5 moves" / Map

### Screen 8: How to Play
- Step-by-step guide with the game's real pieces

### Screen 9: Settings
- Music, SFX, vibration, reduce motion, reset progress, version

### Screen 10: Achievements
- Unlocked / in progress, with the known reward of each

### Screen 11: Collection Album
- Pages of the game's objects, each filled by a named milestone

### Screen 12: Stats / Profile
- Avatar, nickname, levels cleared, total stars, best score, longest chain, daily streak

### Screen 13: Daily Challenge
- Today's seeded level, the streak, the badge

### Screen 14: Combo / Event Overlays (3 tiers)
- Routine: local pop + score tick
- Notable: "CHAIN x6!" callout with a combo badge
- Major: level clear / new best takeover
```

**UX Flow (navigation):**
```
Splash → Menu → Level Map → Game ←→ Pause (→ How to play / Settings)
                               ↓
                 Level Complete → Next level / Map
                 Level Failed   → Retry / Map

          Menu ←→ Daily Challenge
          Menu ←→ Achievements / Collection
          Menu ←→ Stats / Profile
          Menu ←→ Settings
```

### Section 5: Asset Manifest (FULL, format-aware)
```markdown
## Asset Manifest

**Default for Codex `/autocreate`: PNG via GPT Images 2.0 → GPT Images/default fallback.**
SVG is only valid as a fallback outside of Codex or with an explicit `--svg`. In concept, DO NOT call
assets `.svg`, if the game will be played through `/autocreate` in Codex: downstream agents read this
manifesto literally.

### Shared Visual Style Anchor
- Render style: [2D or 2.5D; mapped reference's actual linework, shading and depth, or the
  concept's chosen finish]
- Lighting: [single source, for example soft top-left key + subtle rim]
- Palette: [semantic color roles from the Design Signature; use the number this game needs]
- Camera/composition: single centered hero object for sprites/icons; 9:16 layered scene for backgrounds
- Cutout policy: sprites/icons/tiles/items = generate on a flat solid chroma-key background
  (default pure magenta #FF00FF; pure green #00FF00 if the palette contains magenta/pink/purple),
  then cut with `tools/cutout.py`; backgrounds = full scene, no alpha removal
- Negative prompt: [exclude styles and artifacts that conflict with this game's reference or DNA],
  no unintended logo or text, no sprite sheet, no casino UI (reels, bet panels, coin payouts),
  no generic neon unless explicitly intended

### Sprites (assets/images/sprites/)
- sprite_[name].png — [subject identity from the game world; material/texture; role in gameplay; readable at 64px]
- ... (minimum 5-8 elements)

### UI Elements (assets/images/ui/)
- ui_action_button.png — action button; shape from shape language DNA
- ui_frame.png — frame of the playing field
- ui_panel.png - control panel / rates / resources
- ui_separator.png — decorative separator
- ui_icon_sound.png — sound icon
- ui_icon_settings.png — settings icon
- ui_icon_info.png — help icon

### Backgrounds (assets/images/backgrounds/)
- background_menu.png — 9:16 background of the main menu; peace, depth and brightness from DNA
- background_game.png — 9:16 background of the game screen; quiet center area, does not argue with the field

### Audio (assets/audio/) — sound effects only, no background music
- assets/audio/sfx/sfx_action.wav - main action (tap/swap/shoot/drop)
- assets/audio/sfx/sfx_score.wav — match / score tick
- assets/audio/sfx/sfx_error.wav - illegal move / out of moves / run over
- assets/audio/sfx/sfx_win_small.wav - small success (a match, a merge)
- assets/audio/sfx/sfx_win_big.wav - big success (a combo, a special, a clear)
- assets/audio/sfx/sfx_win_mega.wav - exceptional (3 stars, a new best)
- assets/audio/sfx/sfx_button.wav — pressing the UI button
- assets/audio/sfx/sfx_navigate.wav — transition between screens
```

### Section 6: Code Architecture (FULL with Data Flow)
```markdown
## Dart Classes

### Game Core
- [GameName]Game extends FlameGame - entry point, controls ValueNotifiers
- [GameName]World extends World with HasCollisionDetection - game world
- GameConfig - ALL numerical constants (board size, budgets, scoring, timings)
- GameState (sealed) — Ready, Resolving, Paused, LevelCleared, LevelFailed

### Systems
- GameRng - the one seeded source of gameplay randomness
- [Rules]Engine - the pure rules engine (resolves a move BEFORE the animation)
- Scoring - a pure function for points, combos and stars

### Components
- [MainComponent] - the board / field / player
- [ElementComponent] - tiles, pieces, balls, hazards
- ComboFeedbackComponent - VFX scaled to what the player earned
- AmbientParticles - optional background atmosphere

### UI
- GameApp (MaterialApp) → named routes
- SplashScreen → MainMenu → LevelMap → GameScreen (GameWidget + HUD overlay)
- HudWidget - ValueListenableBuilder for score/goal/moves/state
- LevelComplete / LevelFailed overlays
- All other screens (12+)

## ValueNotifier Contracts (between Flame Game and Flutter UI)
| Notifier | Type | Writes | Reads |
|----------|------|--------|-------|
| score | ValueNotifier<int> | Game | HUD, LevelComplete |
| movesLeft | ValueNotifier<int> | Game | HUD, LevelFailed |
| goalProgress | ValueNotifier<GoalProgress> | Game | HUD |
| isResolving | ValueNotifier<bool> | Game | HUD (input lock) |
| currentState | ValueNotifier<GameState> | Game | HUD, Overlays |
| combo | ValueNotifier<int> | Game | ComboOverlay |

## Complete Game Loop
1. The player makes a move (swap / link / tap / pick / slide / shoot / tap-to-time)
2. Check isResolving (false) and that the move is legal; lock input
3. The rules engine resolves the move completely (BEFORE any animation)
4. Play back the resolved steps (clear → gravity → refill → cascade, merge, flight, …)
5. Update score, goal progress and moves left; show combo feedback scaled to the gain
6. Goal met → LevelComplete with stars; budget exhausted → LevelFailed with Retry
7. No legal move → reshuffle automatically (never a dead end)
8. Unlock input → return to Ready
9. Save stars/best score; check achievements and album milestones

## Edge Cases (FULL list)
- Double tap on the field/button → second input ignored (isResolving check)
- No legal move on the board → automatic reshuffle
- Goal met mid-cascade → the cascade finishes, then LevelComplete
- App pause during resolution → the resolved move finishes on resume
- Back button on GameScreen → pause overlay
- Settings changed mid-game → apply immediately (audio volume)
- Daily challenge already cleared today → show the streak and "come back tomorrow"
- First launch → level 1 teaches the move with a guided first swap/tap
```

### Section 7: Juiciness Requirements - COMPLETE

```markdown
## Anticipation
- [The beat before a special fires / the last link of a chain / the final target]

## Honest feedback
- Feedback shows exactly what the move did; no fake "almost" moments, no casino reveal theatre

## Celebration (3 tiers, points-based)
- Routine (a match, a merge): [local pop + score tick]
- Notable (a special, a 3+ cascade, a long chain): [callout + combo badge + burst]
- Major (level clear, 3 stars, new best): [result takeover + stars filling + flourish]

## Idle Animations (when the player does not interact)
- Main element: [a hint shimmer on a legal move after a pause, or deliberately still]
- Background: [ambient drift if the DNA supports it]

## Micro-Interactions
- Each button: scale 0.95 when pressed → 1.0 when released + shadow change
- Numbers: animate only meaningful gains
- Navigation: a transition that communicates continuity, or a direct cut
- Switches: custom toggle with animation

## Sound Design Map
| Event | Sound | Character |
|---------|------|----------|
| Move start | sfx_action.wav | Short, crisp |
| Match / cascade step | sfx_score.wav | Pitch rises with the step |
| Special / combo | sfx_win_big.wav | Bright flourish |
| Level cleared | sfx_win_mega.wav | Celebration |
| Button tap | sfx_button.wav | Short click |
| Navigation | sfx_navigate.wav | Swoosh |
| Illegal move / fail | sfx_error.wav | Soft buzz |
```

### Section 8: Anti-Slop Checklist + Production Readiness
```markdown
## Anti-Slop (intent + craft, NOT imposed style)
- [ ] Game UI Read and complete Design Signature are recorded with reasons
- [ ] State Composition Map covers setup, anticipation, result, and recovery/progression
- [ ] Per-screen layout recipes are selected from independent F/C/H/M/O/P axes
- [ ] Similarity Check names real neighbors and records at least four material differences,
      unless a mapped reference or mechanic justifies repetition
- [ ] Semantic type, spacing, color, shape, material, and motion roles are defined without a
      studio-wide count or aesthetic preset
- [ ] Gameplay screen contract satisfied: dominant full-screen portrait field, integrated controls,
      core loop visible without scrolling, and usable button proportions at all four target sizes
- [ ] Motion/transition choices communicate feedback, hierarchy, continuity, or anticipation
- [ ] All 12+ screens are described with full content
- [ ] Micro-interactions on each interactive element
- [ ] Idle animations defined
- [ ] Loading/committed state fits the screen and remains accessible; a standard control is allowed
      when it is the clearest choice
- [ ] Depth and overlay behavior follow the Design Signature instead of default cards/glass
- [ ] Every key state has an intentional attention order; text contrast ≥ 4.5:1
- [ ] Centralized animation timings (animations.dart)
- [ ] The interface remains distinct in wireframe/grayscale; variety is not only palette and mascot

## Production Readiness
- [ ] Complete Game Loop described (step by step)
- [ ] ALL edge cases are listed with solutions
- [ ] Data Flow defined (ValueNotifier contracts)
- [ ] Asset Manifest full (Codex PNG + Audio WAV; SVG fallback only)
- [ ] Sound Design Map defined
- [ ] SharedPreferences for: Settings, Profile, Progression (stars/best), Daily Challenge
- [ ] No-gambling check clean: no wager, currency, shop, chance-based reward, casino UI or age gate
```

## Conclusion

Print the message:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTO-IDEA COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Game: [Name]
Category: [G1-G6] - [title]
Archetype: [A-AB | UNIQUE] - [name]
Balance model: [B1-B6] - target curve [...]
Reference gameplay: [n/a | reused | casino game translated to <archetype>]
Setting / Mood: [world] / [mood]
Layout: [key per-screen F/C/H/M/O/P recipes]
Content: [N levels in M worlds | endless + milestones] | Modes: [Levels + Daily + Endless/Zen]
Meta: [stars + unlocks + achievements + collection album + daily challenge] (no currency)
No gambling: [clean]
MVP screens: [N] screens
Design Signature: [key interaction, composition and visual decisions]

Saved: design/gdd/game-concept.md

Next step:
  /autocreate --from-concept - implement as a game
  /map-systems - decompose into systems
  /design-review - concept review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
