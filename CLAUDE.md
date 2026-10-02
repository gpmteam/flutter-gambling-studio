# Flutter Casual Game Studio

> A specialised studio for building **casual mobile mini-games** on Flutter + Flame through
> coordinated Claude Code agents. (The repository keeps its historical name,
> `flutter-gambling-studio`; the studio no longer builds gambling games.)
>
> For OpenAI Codex, use `AGENTS.md` and `.codex/` as a compatibility layer over these same rules.

## What the studio specialises in

**Casino-grade looks, casual gameplay.** Games may look like premium casino key art — jewel-toned
symbols, gold trim, jokers, crowns, sevens, deities — or reproduce a reference exactly. Their
gameplay is always a **casual skill mechanic scored in points**: match and cascade, tile and sort,
merge and place, aim and physics, arcade reflex, logic. Every concept falls into one of the six
categories below and declares a **balance model** verified by a simulation run.

**Never gambling.** No bets, stakes or wagers; no money of any kind — real or virtual, no coins,
chips, gems or credits as a currency; no chance-based rewards (slots that spin for an outcome,
roulette, wheels, loot boxes, gacha, scratch cards, plinko-for-prizes); no casino games, even for
points. Points, stars, levels and unlocks by progress only. This is a hard gate on every concept,
code review and release: `.claude/rules/no-gambling.md`.

## Visual standard for assets

Choose the visual finish from the game's brief and references. Both polished 2D illustration and
modeled 2.5D art are valid, and a slot-style key-art finish is the studio's signature look for
original games. Keep the complete asset set coherent in silhouette, linework, depth, materials,
palette, detail and lighting; do not add glossy volume to a flat illustrated reference.

The theme, characters, objects, materials, shapes, details and colours come from the concept and
Design DNA of the specific game. Inspect matching `examples-games/` images by default. When a
reference matches the request, recreate its character, symbol cast, frame, background, palette,
composition and rendering style — and build the casual mechanic listed for it, not the casino
gameplay the image shows. Use the actual images as generation references and compare the runtime
result beside them (`.claude/docs/game-concept-examples.md` → "How close to the reference — match
it"). Read `.claude/docs/visual-context.md` and `.claude/docs/game-concept-examples.md` for lead
kinds, flexible store composition, board topology, Joker tone, combo markers and the five required
store-only combo balls. The reference's visual language is authoritative; reject unrequested style
substitutions.

**The concept carousel is approved before any code.** `/autocreate` renders the store panorama
once the concept, assets and data exist, slices it into the three carousel slides and stops until
the user approves it (`tools/concept_gate.py`). The approved panorama then governs the rest: the
game's field is built to look like its gameplay sample (finalization checks it as V23), the game
background is rendered in its world, and `/store-screenshots` exports it unchanged and renders the
banner from it. Its own review is bounded, because the user reviews it next: a composition guide
(`tools/store_compose.py composition-guide`) shows the image model where the carousel cuts the
picture, each revision gets three fresh renders and five region repairs (`concept_gate.py budget`,
enforced by the lineage ledger), and whatever is still off is published as a known issue on the
approval card. See `.claude/skills/store-screenshots/references/concept-panorama.md`.

**Generated art stays near its first generation.** Every image-model edit re-paints the whole
frame and every reference is copied with its artifacts, so a picture edited again and again — or
re-rendered from its own previous version — turns smeared and mushy. A change to generated art
starts from the original references; a picture gets at most one whole-frame edit; local fixes are
region repairs (`tools/region_repair.py`). `tools/art_lineage.py` records every generated
picture and refuses the compounding moves. See `.claude/docs/art-lineage.md`.

**Reference requests are detected, not guessed.** `/autocreate` Phase 0 runs
`tools/reference_detect.py` on the user's request: a named `examples-games/` family (English or
Russian spelling), images the user attached (`design/references/user/`), or an explicit "same as /
copy / по референсу" ask. It also resolves the mechanic: the family's casual build, a casual
mechanic the user named, or the casual translation of a gambling ask. Its result lives in
`design/reference-contract.md` and binds every later phase: the game's art — character, sprites
and symbols, frame, background, palette, finish — must read as the same world as its sources. The
detector's findings may be added to, never dropped.

## Technology stack

- **Engine**: Flutter 3.27+ / Flame 1.18+
- **Language**: Dart 3.6+ (null-safe, sealed classes, pattern matching)
- **Specialisation**: portrait phone casual mini-games, touch only
- **Product platforms**: Android and iOS phones (portrait-locked); Web is the verification and preview host
- **Rendering**: Flutter Impeller (Android/iOS), CanvasKit/Skia for Web
- **Balance**: `tools/simulate_balance.py` — the verifier for all six balance models

> **You are the creative director and producer.** The agents implement your idea.
> Run `/start` to begin.

## Language

**ALL work is produced in English.** This is a hard requirement for every agent.

That covers agent responses and questions, design documents, concepts, GDDs, reports,
session state and commit messages — as well as Dart/Flutter code, file paths, class names
and CLI commands, which are English by definition.

**The game itself ships in English too.** Every string the player sees — menus, buttons,
HUD labels, how-to-play, level goals, result messages, empty states, achievement names, plus store
metadata and screenshot captions — is written in English by default.

**The single exception is an explicit user request.** If the user asks for the game in another
language, produce the player-facing copy in that language and record the choice in
`design/gdd/game-concept.md`. Even then, everything else stays English: code identifiers,
file and asset names, comments, design documents, reports and session state. Never switch the
game's language on your own initiative, and never infer it from the language the user happens
to be typing in — only an explicit request counts.

## The six game categories

| ID | Category | Icon | Core | Balance model | Archetypes |
|----|----------|------|------|---------------|------------|
| **G1** | Match & Cascade | 🧩 | Clear groups of matching symbols; the board refills | **B1** board simulation | A–D |
| **G2** | Tile & Sort | 🗂 | Clear or sort a dealt layout; every deal is solvable | **B2** solvable deals | E–H |
| **G3** | Merge & Place | 🔷 | Combine or place pieces to grow tiers and keep space | **B3** run length | I–L |
| **G4** | Aim & Physics | 🎯 | Aim, shoot, bounce or draw; physics resolves the shot | **B4** shot simulation | M–Q |
| **G5** | Arcade Reflex | ⚡ | Timing and reflex against a rising tempo | **B5** reflex ramp | R–W |
| **G6** | Logic & Progression | 🧠 | Logic levels with one clean solution path | **B6** solver curve | X–AB |

A full description of every category, its required systems, its balance model and its
archetypes — plus the table that translates a gambling ask into a casual mechanic — lives in
`.claude/docs/game-categories.md`. That is the canonical reference; it outranks memory.

@.claude/docs/game-categories.md

## Archetypes A–AB (short index)

| Category | Archetypes |
|----------|------------|
| **G1** 🧩 | **A** swap match-3 · **B** link chain · **C** tap blast · **D** rotate match |
| **G2** 🗂 | **E** triple tile tray · **F** pair tiles · **G** sort puzzle · **H** card patience |
| **G3** 🔷 | **I** slide merge · **J** drop merge · **K** block place · **L** merge grid |
| **G4** 🎯 | **M** bubble shooter · **N** peg clear · **O** brick breaker · **P** knockdown · **Q** draw & guide |
| **G5** ⚡ | **R** lane runner · **S** stacker · **T** catcher · **U** slicer · **V** one-tap flyer · **W** target throw |
| **G6** 🧠 | **X** connect paths · **Y** rotate pipes · **Z** unblock · **AA** memory match · **AB** logic grid |

## Quick start

```
/start             — Orientation: where to begin right now
/brainstorm        — Interactive casual game concept generation
/auto-idea         — Autonomous generation of a finished idea (no questions)
/autocreate        — Zero-to-Production: a complete working game from one command
                     (concept + balance model + assets → concept carousel for YOUR approval →
                      code + tests + audit + balancing → store kit)
```

## The full path to a finished game

```
Idea → Concept → Balance → Design → Gate → Code → UI audit → Runtime → Gate → QA → Gate → Release
  │       │         │         │       │      │       │          │        │      │      │       │
/start /brain-  /balance-  /design- /gate  /team-  /ui-     /emulator- /code- /balance /gate /release-
       storm     check     system   check  dev     audit    test       review  check   check checklist
```

## Studio commands (skills)

### Building a game (in order)

| Command | Description | When to use |
|---------|-------------|-------------|
| `/start` | Onboarding and routing | At the start of every session |
| `/brainstorm [hint]` | Interactive casual game concept | No idea yet, or one that needs shaping |
| `/auto-idea` | Autonomous concept (28 archetypes A–AB across 6 categories + Variety Dimensions) | Fast generation with no questions |
| `/auto-idea --list` | Show every archetype A–AB by category | Choosing an archetype by hand |
| `/auto-idea --archetype [A-AB]` | Expand one specific archetype | You already have a preference |
| `/auto-idea --category [G1-G6]` | A random archetype inside one category | You know the category, not the mechanic |
| `/autocreate` | Zero-to-Production: concept, assets and data, then the concept carousel (the store panorama in three slides) for approval; after approval the game is built to match it and the store kit follows | You want a fully working game |
| `/autocreate --revise "<feedback>"` | Apply your feedback to the pending concept carousel and present it again | The carousel needs changes before you approve it |
| `/autocreate --from-concept` | Implement a saved idea | After `/auto-idea` |
| `/map-systems` | Decompose into technical systems | After the concept |
| `/design-system [system]` | A GDD for one game system | One system at a time |
| `/prototype [mechanic]` | A juiciness / feel prototype | Before full implementation |
| `/generate-asset [type] [name]` | SVG assets by default, no format question | Before writing code |
| `/generate-asset [type] [name] --png` | PNG/image generation; GPT Image 2 built-in, or `tools/gpt_image.py` in headless Codex CLI | When you need raster |
| `/generate-png-asset [description]` | PNG via GPT Image 2; the headless bridge uses the per-user API key, and simple assets go through a local cutout | High-quality raster, fast |
| `/generate-png-asset --batch "items"` | Batch-generate several PNGs at once | Generating all assets |
| `/generate-png-asset --from-concept` | Generate every PNG from the concept | After design |
| `/svg-to-png [path]` | Convert SVG to PNG via Codex GPT Images 2.0 → GPT Images/default fallback | You have SVG, you need raster |

### Quality gates (pass one before every transition)

| Command | Description | When |
|---------|-------------|------|
| `/gate-check concept` | Is the concept ready (category + balance model + no-gambling check)? | After brainstorm |
| `/gate-check design` | Is the GDD ready for implementation? | Before the programming team |
| `/gate-check code` | Is the code ready for QA? | After coding is finished |
| `/gate-check qa` | Is it ready for release? | After all tests |

### Review and quality

| Command | Description |
|---------|-------------|
| `/code-review` | Full code review (architecture, Flame API, rules-engine purity, seeded RNG, no-gambling, state, tests) |
| `/ui-audit` | Automatic UI/UX audit for anti-slop quality + no-gambling copy + auto-fix |
| `/asset-review` | Vision review of the asset set for consistency (style/light/palette/readability, AR1–AR11) + regeneration of rejects (art-director agent) |
| `/emulator-test` | Runtime verification on Chrome/Web (primary) or ADB/emulator: launch, screenshots, vision analysis, log parsing, automatic bug fixes |
| `/playtest` | Deep GAMEPLAY verification via CDP: actually plays N moves/rounds, checks that the score changes, that clear/fail paths work, that the board responds, that progression unlocks (P1–P10) |
| `/design-review` | GDD review for completeness and balance correctness |
| `/balance-check` | Balance verification: `tools/simulate_balance.py` against the category's model B1–B6 |
| `/release-checklist` | Final GO/NO-GO checklist before release, including the no-gambling gate (release-manager agent) |
| `/release-engineering` | Ship engineering: app icons (adaptive + iOS) + native splash + versioning + **signed AAB** + iOS scaffold + store metadata (casual category, "simulated gambling: no") + CI |
| `/release-package` | Release packaging: screenshots of every screen + release APK/AAB + `flutter clean` + a `.zip` in `project_zip/` |
| `/store-screenshots` | Context-based store kit, started after `/autocreate-finalize`: exports the concept panorama the user approved before implementation unchanged as the carousel, renders the banner (→ feature graphic), icon and emblem in its world, puts real captures on the game background, and packages the ZIP. Read `.claude/skills/store-screenshots/SKILL.md`. |

### Diagnostics and debt

Record evidence of concrete reusable failures, corrections, or faster approaches during production.
Finish the requested deliverable or report its blocker before a separate `/auto-learn` task.
Do not implement or validate learning proposals inside store-kit delivery. Dedicated learning
tasks produce tested `learning/*` proposals under standing push authorization; the owner merges.
Explicitly requested framework fixes remain the primary task. See `.claude/docs/auto-learning.md`.

| Command | Description |
|---------|-------------|
| `/perf-profile [area]` | FPS / memory / particle profiling |
| `/tech-debt` | Technical debt scan and register |
| `/auto-learn` | Evidence-based framework improvements on tested review branches; no auto-merge |
| `/hotfix [description]` | Emergency fix for critical bugs |
| `/architecture-decision [decision]` | Create an ADR for a significant decision (including a change of balance window) |

### Teamwork

| Command | What it orchestrates |
|---------|----------------------|
| `/team-dev [description]` | game-designer + balance-designer + mechanics-programmer + juice-artist + sound-designer + qa |

### Working with an existing project

| Command | Description |
|---------|-------------|
| `/continue-project` | Continue from where work stopped |
| `/add-feature [feature]` | Add a feature to a finished game |

## Studio agents

### Tier 1 — Directors (high-level decisions)

| Agent | Role |
|-------|------|
| `creative-director` | Overall vision, concept, game category, creative decisions |
| `technical-director` | Architectural decisions, ADRs, resolving technical conflicts |

### Tier 2 — Gameplay specialists

| Agent | Role |
|-------|------|
| `balance-designer` | **Owner of the balance model**: level curves, move/shot budgets, tempo ramps, scoring and star thresholds, deal generation. The only agent who changes the model's numbers |
| `game-designer` | GDD: rules, level goals, specials and boosters, progression, scoring, screens |
| `mechanics-programmer` | Implementation: the pure rules engine, seeded `GameRng`, logic before animation, Forge2D physics |
| `meta-systems-programmer` | Meta systems: SaveService, Progression, Achievements, Collection + Analytics/Ads/IAP/RemoteConfig abstractions (no-op). Turns one level into a full game |
| `art-director` | Visual consistency of the asset set: vision review (uniform style/light/palette, readability at 64px, AR1–AR11), regeneration of rejects |
| `juice-artist` | VFX, particles, match/combo/clear celebrations — what makes a move feel "juicy" |

### Tier 3 — Core specialists

| Agent | Role |
|-------|------|
| `lead-programmer` | Architecture, code review |
| `performance-analyst` | FPS, memory, Flame optimisation, profiling |
| `ui-programmer` | Flutter screens, HUD, level map, result screens |
| `sound-designer` | Audio: tap, match, cascade, combo, clear, fail |
| `qa-tester` | Test cases, edge cases, rules-engine determinism, state leakage |
| `release-manager` | Release preparation, no-gambling and store audit |
| `auto-learner` | Diagnose reusable failures/improvements, validate bounded framework changes, push review branches |

## Critical rules (game integrity)

> Breaking these rules blocks the release. They are **unconditional** across all six categories.

1. **No gambling**: no wagers, no currency, no chance-based rewards, no casino games —
   `.claude/rules/no-gambling.md`. Points, stars and progress-based unlocks only.
2. **Logic before animation**: the pure rules engine resolves a move (matches, cascades, merges,
   collisions, score) before the animation plays it back. The animation never decides anything.
3. **One seeded `GameRng`**: all gameplay randomness (fills, deals, spawns, level generation) comes
   from one injectable seeded generator, so levels, bot simulations and tests reproduce. No
   scattered `Random()` in game logic; purely cosmetic randomness uses a separate `VfxRng`.
4. **GameState**: a sealed class — no boolean flags.
5. **GameConfig**: every game constant lives in the config file (`game_config.dart`), and the
   balance model's numbers live in its JSON config.
6. **No magic numbers**: no hardcoded gameplay parameters outside the config.
7. **Double protection**: input is locked while a move resolves (300 ms debounce on the primary action).
8. **The balance model is verified**: `tools/simulate_balance.py` returns PASS for the category's
   model. A game without a green run does not ship.
9. **No dead ends**: a board with no legal move reshuffles; a failed level offers an instant retry;
   every deal and generated level is solvable.

@.claude/docs/balance-models.md

@.claude/rules/no-gambling.md

## Collaboration protocol

**User-directed collaboration, not autonomous execution.**

The pattern: **Question → Options → Decision → Draft → Approval**

- Agents MUST ask "May I write this to [path]?" before Write/Edit
- Exception: `/autocreate` and `/auto-idea` run autonomously — that is deliberate. `/autocreate`
  stops exactly once, for the user to approve the concept carousel before implementation

## Contextual Design (human-crafted UI)

> Every visual decision follows from the context of THIS specific game — its theme, mood and
> mechanics. There is no single template. Neon trapezoids for EVERY game are just as much slop
> as purple gradients. **"Casino-grade look" does not mean "dark neon and gold" every time**: a
> jewel match-3 can be warm and bright, a sort puzzle pastel and toy-like, a logic game strict and
> typographic. The test: if the UI could be moved to another game unchanged, the design failed.
>
> Distinctiveness rests on a documented **Design Signature** (field framing, controls, HUD
> behavior, information density, materials, type, color/value, motion, and depth) plus
> **per-screen composition recipes**. The menu, live level, result, and information screens may
> use different compatible recipes from the layout grammar. Changing only palette and mascot over
> one recurring shell is not variety. See anti-slop-design.md and layout-archetypes.md.

@.claude/rules/anti-slop-design.md

@.claude/docs/layout-archetypes.md

### Gameplay-screen composition

The live game must own the viewport. The mechanic is a dominant, integrated surface—not a small
window floating above a generic scrolling card. Core play, essential HUD (score, moves/time,
goal), and the primary action or direct-manipulation surface remain visible together without page
scrolling. The implementation and runtime gates use the measurable contract below.

@.claude/docs/gameplay-screen-contract.md

### Portrait phone product target — mobile only

Every game is a portrait phone game played by touch. Concepts, layout recipes, assets and screens
are designed for a phone held upright and verified at 360×640, 360×800, 390×844 and 430×932.
There is no tablet, desktop or landscape layout at any stage; a tablet or desktop browser shows
the same phone screens in the phone column over the game's background, never in a device frame.

@.claude/docs/mobile-first-contract.md

## Professional quality bar

> One shared benchmark for "professional level" across every skill in the pipeline. The main
> test: "would a player give this 4+ stars without knowing an AI made it?" With concrete,
> checkable thresholds: TTF ≤ 10 s, response ≤ 100 ms, scaled feedback, a living board,
> 60 fps during celebrations, product completeness.

@.claude/docs/quality-bar.md

## Code standards

@.claude/docs/technical-preferences.md

@.claude/docs/coding-standards.md

## Directory structure

@.claude/docs/directory-structure.md

## Coordination rules

@.claude/docs/coordination-rules.md

## Context management

@.claude/docs/context-management.md
