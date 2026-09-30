# Game Concept: [Name]

## 0. Classification (MANDATORY — without it `/gate-check concept` returns FAIL)

- **Category**: [G1 Match & Cascade | G2 Tile & Sort | G3 Merge & Place | G4 Aim & Physics | G5 Arcade Reflex | G6 Logic & Progression]
- **Archetype**: [A–AB | UNIQUE] — [name]
- **Balance model**: [B1 Board simulation | B2 Solvable deals | B3 Run length | B4 Shot simulation | B5 Reflex ramp | B6 Solver curve]
- **Balance config**: `design/balance/[level-config | endless-config].json`
- **Target curve**: [e.g. "L1–3 ≥ 85% pass, final world 30–45%" / "median first run 60–90 s"]
- **Scoring**: points only — [how points are earned; what stars/milestones unlock]
- **Reference gameplay**: [n/a | the reference's own casual gameplay | the reference is a casino game → translated to <archetype> (look kept, mechanic replaced)]
- **No-gambling check**: no wagers, no currency, no chance-based rewards — `.claude/rules/no-gambling.md`
- **Game language**: English (default) | [another language, only if the user explicitly asked]
- **Product target**: portrait phone game (Android/iOS, portrait-locked, touch only); Web is the preview host

## 1. Elevator pitch
What is the main emotion this game delivers? Where is its hook?

## 2. Balance profile (filled in by balance-designer)

Filled in according to the model from §0 — see `.claude/docs/balance-models.md`:

- **B1/B4/B6 (levels)**: level count and worlds, the onboarding plateau, where new elements
  arrive, the target pass-rate band per world, move/shot/time budgets, star thresholds
- **B2 (deals)**: kinds/layers/containers per level, generator policy, par curve, undo/hints
- **B3 (runs)**: board size, tier chain, spawn table, goal tier, target session length
- **B5 (tempo)**: interval and reaction-window ramp, time to cap, grace period, lives

## 3. Core mechanic (filled in by game-designer)
- **Board / field topology**: [e.g. 7×8 match board | layered pile + 7-slot tray | 4×4 grid | tilted peg field | three lanes]
- **The move**: [swap | link | tap group | pick a tile | pour | slide | drop | aim & shoot | tap to time | drag a path]
- **Resolution**: [match → clear → gravity → refill → cascade | tray triple | merge | physics step | survive]
- **Goal and budget**: [score target / collect N / clear all / survive; moves / shots / time]
- **Special elements**: [specials from big matches, blockers, obstacles, boosters earned by milestones]
- **Fail and recovery**: [out of moves → retry / a rewarded extra move; run over → instant restart]

## 4. Juiciness
What state change is the decisive feedback moment, and how does the player read it? Record the
feedback character for routine, notable, and major events (a match, a combo, a level cleared),
including where motion/effects stay absent. Do not assume an explosion, shake, particle shower,
or full-screen takeover.

## 5. Full asset list
- `sprite_...`
- `ui_...`
- `background_...`

## 6. Asset/World Design DNA, Game UI Read, and Design Signature
> Every decision follows from this game's player, mechanic, state needs, world, and reference.
> See `.claude/rules/anti-slop-design.md`.
- **Asset/World Design DNA**: [fiction, subject cast, silhouette language, materials, lighting,
  illustration palette, and finish; no fixed color/font count]
- **Player/session and core decision**: [who, posture, duration, repeated choice]
- **Emotional arc and information pressure**: [read -> move -> resolve -> result; now vs later]
- **Visual world and memorable interface idea**: [specific, mechanic-linked]
- **Field framing / controls / HUD / navigation**: [choice + reason for each]
- **Geometry / surface / type / color-value**: [semantic roles; no fixed token count]
- **Motion / depth / sound-haptics**: [what they communicate, and where they stay absent]

## 7. State composition and layout direction
> See `.claude/docs/mobile-first-contract.md` and `.claude/docs/layout-archetypes.md`.
- **State map**: [read / move / resolve / result / recovery attention order]
- **Per-screen recipes**: [main menu M/O/P; live states F/C/H/O/P; secondary screens]
- **Store lead and menu role**: [lead_kind: character | object | mechanic;
  menu_role: dominant | supporting | absent, with reason from the M recipe]
- **Primary field alignment**: [centered, or documented mechanic/recipe reason for an offset]
- **Phone proof**: [360×640 / 360×800 / 390×844 / 430×932; thumb reach; no core scroll; the P
  strategy for short and tall phones]
- **Similarity Check**: [neighbors, intentional repeats, at least four material differences,
  remaining risk/correction; skip anti-repeat drift for an exact mapped reference]
- **Non-targets**: no desktop, tablet or landscape layout, no width breakpoints, no device frame,
  no hover/pointer/keyboard-only interaction.

## 8. Screen map (at least 12+, each with a job and appropriate recipe)
- Splash, main menu, level map / mode select, game + HUD, pause, level complete (stars), level
  failed / run over (retry), how to play, settings, achievements, collection album, stats/profile,
  daily challenge, loading.
- **No gambling surfaces** (`.claude/rules/no-gambling.md`): no shop, no currency balance, no
  paytable/odds, no spin/bet controls, no daily spin or chest.

## 9. Visual references and store direction
> Follow `.claude/docs/visual-context.md` and `.claude/docs/game-concept-examples.md`.
- **Lead kind / identity**: [character | object | mechanic; exact subject and runtime role]
- **Previews inspected**: [every mapped path and its role; exact traits, 2D/2.5D finish, and any deviations]
- **Reference ledger**: [character, every symbol (and its role in the casual mechanic), frame,
  background, UI materials and composition; source path(s) for each; direct reuse versus
  high-fidelity image edit]
- **Character tone**: [if relevant; Joker = mischievous/slightly vicious, playful, not horror or an elegant host]
- **Combo markers**: [x2/x5/x10 badges only for real points combos; exact scoring source, or omit]
- **Panorama map**: [anchors, gameplay location/span, critical regions and safe seam plan]
- **Feature graphic**: [independent horizontal composition; free or justified left-heavy arrangement; text-free, with one phone on the right holding a real capture]
- **Runtime continuity**: [asset identities, board topology, backgrounds and state to preserve]
