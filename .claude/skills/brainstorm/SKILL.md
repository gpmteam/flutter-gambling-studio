---
name: brainstorm
description: "Interactive generation of a casual game concept with a casino-grade or reference-matched look and never-gambling gameplay. Settles the category (G1-G6: match & cascade, tile & sort, merge & place, aim & physics, arcade reflex, logic & progression), the archetype, the balance model, the theme, the mechanic and the one unique piece of juice."
argument-hint: "[a theme, or 'open' for an open brainstorm]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# Brainstorm

Read `.claude/docs/visual-context.md` before planning or reviewing visuals. For a matching
new-game request, inspect the relevant `examples-games/` previews and read
`.claude/docs/game-concept-examples.md`. Carry the lead kind, references/adaptations, exact
board topology, Joker expression (when relevant), and verified combo-marker meanings from
the concept into the art direction, asset manifest and prompts. An unspecified match game uses a
7×8 board; store gameplay placement is flexible and object-led games need no invented character.


> **CASUAL GAMES, NEVER GAMBLING.** The studio makes casual skill games scored in points; their
> look may be casino-grade key art. If the user proposes a gambling idea (a slot, roulette,
> crash, mines, gacha…), say so directly in one sentence and offer the casual translation with
> the same feel from `.claude/docs/game-categories.md` → "Translating a gambling ask" (for
> example "a Zeus slot" → a Zeus link-chain board, G1, archetype B). See
> `.claude/rules/no-gambling.md`.
>
> The canonical reference for categories and archetypes: `.claude/docs/game-categories.md`.
> Every concept is a portrait phone game. Read `.claude/docs/mobile-first-contract.md`: design
> for a phone held upright and played by thumb; there is no tablet, desktop or landscape layout.

When this skill is invoked:

1. **Check the existing documents**: `design/gdd/game-concept.md`. If it exists, ask whether we
   are continuing that work.

2. **The interactive phases (ask the questions step by step)**:

   **Phase 0: choosing the category and archetype**
   The mandatory first step is to settle the category:

   | ID | Category | What it is | Archetypes |
   |----|----------|------------|------------|
   | **G1** 🧩 | Match & Cascade | Swap, link or tap matching symbols; cascades refill the board | A–D |
   | **G2** 🗂 | Tile & Sort | Clear a layered pile into a tray, pair tiles, sort containers, patience | E–H |
   | **G3** 🔷 | Merge & Place | Slide/drop/place pieces that merge up a tier chain or clear lines | I–L |
   | **G4** 🎯 | Aim & Physics | Bubble shooter, peg clear, brick breaker, knockdown, draw & guide | M–Q |
   | **G5** ⚡ | Arcade Reflex | Runner, stacker, catcher, slicer, one-tap flyer, target throw | R–W |
   | **G6** 🧠 | Logic & Progression | Connect paths, rotate pipes, unblock, memory, logic grid | X–AB |

   Then the specific archetype inside the category (or a hybrid at the seam of two categories).

   **Phase 1: theme and emotion**
   - What atmosphere are we creating? (A jewel carnival, Olympus, an Egyptian temple, a royal
     treasury, a candy land, a cosmic arcade, a cosy café?)
   - Is there a reference to match (a named `examples-games/` family or an image)?
   - Who is our target audience? (Relaxed casual or competitive score-chaser?)
   - ⚠️ Casino-grade *assets* are the studio look; a dark-neon *interface* on every game is slop.
     Ask about the world before you ask about the palette.

   **Phase 2: the balance model** (determined by the category)

   The thresholds are in `.claude/docs/balance-models.md`.

   *G1 → model B1 (board simulation):*
   - Board size and symbol kinds; the move rule; specials and blockers
   - How many levels and worlds; the onboarding plateau; the final-world pass band (30–45%)

   *G2 → model B2 (solvable deals):*
   - Layout size and layers, tray size or containers; the par curve; undo and hints

   *G3 → model B3 (run length):*
   - Board size, the tier chain and its hero object, the spawn table, the target session length

   *G4 → model B4 (shot simulation):*
   - Layout types, shot budgets, the catch bucket; the headless bot that proves the curve

   *G5 → model B5 (reflex ramp):*
   - The tempo start and cap, the time to cap, the grace period, the target first run (30–180 s)

   *G6 → model B6 (solver curve):*
   - The rule set, level sizes, the solver and par, earned hints

   **Phase 3: the mechanic**
   - What is the core move loop? (read → move → resolve → score → goal)
   - Which special elements will there be? (specials from big matches, blockers, boosters earned
     by milestones)
   - How complex are the controls? How many taps to the first move (target ≤ 3)?

   **Phase 4: juiciness**
   - Which decisive state transition will set the game apart, and what feedback vocabulary makes
     it readable? Consider restraint as well as spectacle; do not default to explosions, shake,
     particles, rolling counters, or full-screen overlays.
   - ⚠️ Feedback is HONEST: it shows exactly what the move did — no fake "almost" moments and no
     casino reveal theatre.

   **Phase 5: visual identity and composition**
   - **Asset/World Design DNA**: fiction, cast, silhouette language, materials, lighting,
     illustration palette, and finish. Keep this distinct from interaction architecture.
   - **Game UI Read and Design Signature**: audience/session, emotional arc, information pressure,
     field framing, controls, HUD behavior, materials, type, color/value, motion, and depth (see
     `.claude/rules/anti-slop-design.md`). Do not infer a fixed token count or default darkness.
   - **Per-screen layout recipes** (see `.claude/docs/layout-archetypes.md`): choose independent
     field/control/HUD/menu/overlay/phone-height ingredients for the menu, live states, result, and
     information screens. Compare with nearby games; changing only style is not enough.
   - **Phone proof**: how the one portrait composition holds across 360×640, 360×800, 390×844
     and 430×932 while keeping the primary action in thumb reach and the core loop above the fold.

   **Phase 6: progression**
   - Stars, world unlocks, achievements, the collection album, the daily challenge.
   - No currency, shop, random rewards or age gate (`.claude/rules/no-gambling.md`).

   **Phase 7: the game's language**
   - English by default — every player-facing string, plus store metadata.
   - Only ask about another language if the user brings it up; if they do, record the choice in
     the Classification block. See `CLAUDE.md` → Language.

3. **Synthesis**: produce 3 concepts to choose from. Each must include an elevator pitch, the
   category and archetype, the balance model with its target curve, the theme, the "juicy"
   feature, **Asset/World Design DNA**, the **Design Signature**, key state recipes, and Similarity
   Check — and ideally three materially different directions rather than three reskinned ones.

4. **Writing the document**: create `design/gdd/game-concept.md` from the
   `.claude/docs/templates/game-concept.md` template — starting with the **Classification**
   block (category, archetype, balance model, target curve, config, scoring, reference gameplay,
   no-gambling check). Record the portrait-phone target in the Classification and Layout sections.

5. **Next steps**:
   - "Use `/design-system [system]` to design the mechanic in detail"
   - "Use `/balance-check` to verify the difficulty curve before any code"
   - "Use `/prototype [mechanic]` to check the juiciness"
   - "Bring in `/team-dev` to start development"
