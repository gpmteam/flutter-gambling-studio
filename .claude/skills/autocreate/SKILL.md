---
name: autocreate
description: "Zero-to-Production factory for complete G1-G6 casual games with casino-grade or reference-matched looks and never-gambling gameplay. Session 1 produces an English game concept and production plan, reference-matched or concept-derived 2D/2.5D PNG assets, synthesized WAV audio and structured level/progression data, then renders the concept carousel — the store panorama sliced into three slides, with the gameplay sample the game will be built to match — and stops for the user's approval. After approval the pipeline builds the complete Flutter/Flame game to match it (tests, no-gambling gate, balance, runtime verification, release preparation) and finishes with the store kit. --revise applies the user's feedback to a pending carousel."
argument-hint: "[--from-concept | --idea-only | --revise \"<feedback>\"]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# AutoCreate — Zero-to-Production Complete Game Factory

Read `.claude/docs/visual-context.md` before planning or reviewing visuals. Whether this is a
reference request — and which mechanic governs play — is decided by `tools/reference_detect.py`
in Phase 0, not by reading the table by eye. For a reference request, inspect every source it
lists and read `.claude/docs/game-concept-examples.md`. Carry the lead kind,
references/adaptations, exact board topology, Joker expression (when relevant), and verified
combo-marker meanings from the concept into the art direction, asset manifest and prompts. An
unspecified match game uses a 7×8 board; store gameplay placement is flexible and object-led
games need no invented character. The named requests Book of Ra, Royal Joker (or a plain
Joker), Joker Jewels, Shining Crown, and Plinko must use the preview mapping in that document;
Joker Jewels resolves to every file in `examples-games/joker-jewels/` and to the swap match-3
board, not to the Royal Joker row. For an exact family, recreate what the preview shows — theme,
character, symbol cast, palette, frame and composition are matched, not reinterpreted, and
Variety Dimensions are not scrolled. Royal Joker is a loose reference (`binding: loose`, below). Build
the casual mechanic the family lists, never the casino gameplay a preview shows. Follow the
source-quality and branding limits in `game-concept-examples.md`. Never add a character to Shining
Crown or Plinko.

Build a complete production-ready **casual** game. Its look may be casino-grade key art or match a
reference exactly; its gameplay is never gambling — no wagers, no currency, no chance-based
rewards, no casino games, no age gate (`.claude/rules/no-gambling.md`). If the request asks for a
gambling mechanic, build the casual translation the detector names and say so in the final report.
Do not ask the user questions: derive reasonable choices from the concept and record them.

All conversation, design documents, reports, prompts, code comments, generated game copy, store metadata, and screenshot captions must be in English. Use another player-facing language only when the user explicitly requests it and record that choice in the concept.

## Mandatory execution contract

The pipeline does not rush from assets into code. It stops once, for the user:

1. **Session 1 — pre-production and the concept carousel (this skill, Phases 0–3.10):**
   reference/mechanic detection, concept, project bootstrap, structure and layout, assets, audio,
   level/progression data, the handoff, then the **concept carousel** — the store panorama,
   rendered from the real assets under the store's own rules and sliced into the same three
   carousel slides `/store-screenshots` exports — and **stop at the approval gate**.
2. **The user approves the carousel** (the web service's Approve button, or "approve" in a
   standalone session) — or asks for changes, which `--revise` applies and presents again.
3. **Session 2 — implementation (`autocreate-implement`, Phases 4.0–10):** only on an approved
   concept. It first renders the game background in the approved panorama's world and aligns the
   field's assets to the panorama's gameplay sample, then writes the game code, meta systems,
   content wiring, integration, build fixes, feel pass, tests, UI/no-gambling audit, balance and
   crash prevention — with the field built to look like the gameplay sample.
4. **Session 3 — finalize (`autocreate-finalize`, Phases 10.4–13):** runtime/soak verification
   (including V22, the game on its campaign background, and V23, the field against the approved
   gameplay sample), playtest, session state, release-engineering preparation, the final report,
   and the handoff to the store kit.
5. **Store kit (`/store-screenshots`):** exports the approved panorama unchanged — crops, grading
   and a detail pass only — as the carousel, renders the banner in its world, and packages the kit.
   The web service starts it as its own run after a production-ready finalization; standalone,
   finalization starts it.

Session 2 hands control to Session 3, and Session 3 to the store kit, with the Agent tool. If Agent
is unavailable, write the handoff and continue in the same session by reading the next skill. Do
not copy full history into a phase agent; give it only the handoff path, skill path, and exit
criterion. Session 1 hands control to nobody: it ends at the gate.

The product is a **portrait phone game** for Android and iOS, played by touch
(`.claude/docs/mobile-first-contract.md`). Every concept, recipe, asset and screen is designed for
a phone held upright — there is no tablet, desktop or landscape layout at any stage. Chrome/Web is
only the verification host, at the four phone sizes. This pipeline prepares release
metadata and native branding but does not build an AAB/APK or upload keystore.
`/release-package` and the full `/release-engineering` run are explicit user actions.

Session 1 must produce:

- `design/gdd/game-concept.md` with classification, production plan, Asset/World Design DNA,
  Game UI Read, Design Signature, state map, per-screen layout recipes, Similarity Check, screen
  map, data flow, complete loop, and edge cases.
- A Flutter project created for Web plus Android and iOS, portrait-locked, with the portrait-phone
  target recorded in design artifacts.
- `design/reference-contract.md` from Phase 0 (a "not a reference request" record when none).
- `design/structure.md` and `design/art-direction.md`.
- A budgeted, validated asset set and `design/asset-manifest.md`.
- Eight real sound-effect WAV files created by `tools/synth_sfx.py` (no background music).
- `design/asset-review.md` with an asset-cohesion verdict.
- Category-appropriate JSON level/progression data under `assets/data/` and the balance config in `design/balance/`.
- `production/session-state/autocreate-handoff-1.md` with the `Concept gate: required` line.
- The concept carousel in `production/store-art/concept/` — panorama, three exported slides,
  gameplay sample and its spec — published PENDING with `tools/concept_gate.py publish`.

Session 1 must not write gameplay code, screens, services, stubs, or TODO implementations, must
not start Session 2 or approve its own carousel, and must not claim that the game is complete.

## Asset policy

In Codex, create PNG assets with the built-in image-generation tool. In headless Codex where that tool is unavailable, use `python3 tools/gpt_image.py` with `gpt-image-2`. A missing built-in tool is not a reason to fall back to SVG. If both GPT Image 2 transports fail technically, retry through the default Codex image-generation path with the same prompt. SVG is allowed only outside Codex, after an explicit `--svg`, or after all PNG paths fail and the user approves the fallback.

Choose a coherent 2D or 2.5D finish from the concept and Design DNA. For a reference game, the
reference's actual linework, depth, shading, palette, lighting and texture are the style anchor;
do not impose the studio's former glossy 2.5D default. Use the reference files as image inputs
for assets that need their identity preserved, and compare the resulting runtime composition.

Use `design/asset-manifest.md` as the budget ledger. The 12-source default applies to original
concepts; a mapped reference needs enough distinct sources to cover its complete visible cast.
Record the inventory and planned call count before generation. Build UI, typography, icons, VFX,
and safe variants in code or derive/reuse them locally.

## Phase 0 — is this a reference request?

Run the detector on the user's exact request text before anything else. Images the user attached
are saved by the web service under `design/references/user/` (older runs: `user_reference*` in the
repository root); on a first request they are always the reference.

```bash
mkdir -p design/references production/session-state
cat > production/session-state/user-request.txt <<'REQ'
<the user's request, verbatim>
REQ
python3 tools/reference_detect.py --prompt-file production/session-state/user-request.txt \
  --attachments-dir design/references/user --new-game --json > design/references/detection.json
python3 tools/reference_detect.py --prompt-file production/session-state/user-request.txt \
  --attachments-dir design/references/user --new-game --markdown > design/reference-contract.md
```

The detector recognizes the named families in English and Russian spellings (Joker Jewels before
Joker, Book of Ra, Shining Crown, Plinko), binds attached images, flags an explicit
"same as / copy / по референсу" ask, and resolves the **mechanic**: the family's casual build, a
casual mechanic the user named, or the casual translation of a gambling mechanic the user named
(`mechanic`, `topology_source`, `gambling_asks`). Its result only adds obligations: you may add a
reference it missed; you may never drop one it found, downgrade an attachment to "inspiration", or
build a gambling mechanic it translated.

When `reference` is true:

- **Identity is the reference's.** The character (costume, headwear, face, build, expression),
  the symbol and sprite cast object for object, the frame and its ornament, the background,
  palette, finish and UI materials are the source's — the finished game's art must read as the
  same world. Variety Dimensions are not scrolled and the Similarity Check does not push away
  from it (`game-concept-examples.md` → "How close to the reference — match it").
- **Play follows `topology_source`.** `family` → the family's casual build and topology (the
  mechanic in the "Build as" column); `user mechanic` → the user's casual mechanic; `translated`
  → the casual translation of the user's gambling ask; `user grid` → the user's grid where the
  mechanic can be played on it. In every case the reference still governs identity (e.g. "Book of
  Ra dice" is a dice-merge game in the Book of Ra temple with its explorer). A slot's symbols
  become tiles, its reel frame becomes the board frame, its reel strips become column backing —
  nothing spins for an outcome.
- Before Phase 3, view every source at full size and complete the contract's identity ledger. A
  missing mapped file is a blocker, not a reason to improvise.
- Every identity asset is generated **from its source image** (built-in edit path or
  `tools/gpt_image.py edit --image <source> --fidelity high`); text-only generation is allowed only
  for an asset with no visual source. Phase 3.6 AR11 and finalization's V21 compare side by side
  against these sources.
- The studio's generic art direction for original concepts does not apply; the reference's
  rendering style does.

`binding: loose` (Royal Joker, or a plain Joker): the sources are a common reference, not a
recreation. The bullets above apply with these changes — the character is the sources' own and
is generated from them; the symbol family, palette and finish fit their world, while the symbol
designs, the composition and the background are designed for this game, so Variety Dimensions and
the Similarity Check apply to them. The background is abstract slot style (`.claude/docs/visual-context.md` → "Backgrounds — abstract slot style"),
not the sources' backdrop every time and never a place such as a palace or ballroom. Complete the contract's "Shared world" section instead of an identity ledger.
AR11 and V21 hold the character to the sources and the background to the abstract slot style,
not to the sources' backdrop
(`game-concept-examples.md` → "Loose references").

`binding: description` (the user named an unmapped game with no image): match every described
visual trait, record that no pixels were available, and never claim pixel fidelity.

When `reference` is false but `gambling_asks` is non-empty (for example "a roulette game"), the
concept is built on the translated `mechanic` in the requested theme.

## Phase 1 — concept

Run the logic from `.claude/skills/auto-idea/SKILL.md`, unless `--from-concept` was supplied. Save the result to `design/gdd/game-concept.md`.

The concept must include:

- Category G1–G6, balance model B1–B6, archetype, the reference-gameplay decision, the no-gambling check, and English game language.
- A reference bar naming 2–3 successful casual games in the category, the specific feel/timing lesson from each, and the new game's differentiating hook. Never copy their content or art. This bar is separate from a mapped local preview: a named request's preview is close context to stay with, not a competitor to differentiate from.
- A complete production plan with content volume (≥ 12 levels or an endless mode with milestones), 2–3 modes, progression by stars and milestones (no currency), achievements, the collection album, the daily challenge, service abstractions and telemetry.
- A context-derived Game UI Read, multidimensional Design Signature, per-screen layout recipes,
  explicit `lead_kind` plus `menu_role: dominant | supporting | absent`, and a recorded
  Similarity Check.
- For a reference request (Phase 0), the source paths from `design/reference-contract.md`, the
  identity ledger, `lead_kind`, and the mechanic/topology decision with its `topology_source`. Do
  not proceed to asset generation until this reference record is explicit, and the concept's
  theme, character, symbol cast, palette, frame and composition must be the reference's,
  described file by file at full size
  (`.claude/docs/game-concept-examples.md` → "How close to the reference — match it").
  Variety Dimensions are not scrolled for a mapped request. On `--from-concept`, a saved concept that names a mapped family
  (for example Joker Jewels) without that record must have it added from
  `.claude/docs/game-concept-examples.md` before Phase 3, leaving the concept's other decisions
  untouched.
- At least 12 connected screens, their data flow, the complete game loop, and all failure/edge states.
- A portrait-phone declaration following `.claude/docs/mobile-first-contract.md`: the 390×844
  composition of each key screen and its P strategy for 360×640 and 430×932. No tablet, desktop
  or landscape layout is planned.

If `--idea-only` is supplied, stop only after writing and reporting the concept.

## Phase 2 — Flutter project bootstrap

Android and iOS are the product targets; Web is included only as the verification and preview
host. Never create desktop scaffolds.

```bash
flutter create . --project-name game_app --platforms web,android,ios --org com.gamestudio

if [[ ! -f web/index.html ]]; then
  echo "Web project was not created; stopping."
  exit 1
fi
```

Apply `.claude/docs/mobile-first-contract.md` to the scaffold now: portrait lock in the Android
manifest (`android:screenOrientation="portrait"`) and the iOS plist (portrait-only orientations,
`UIRequiresFullScreen`). Session 2 adds the `SystemChrome` lock in `main()` and the phone column in
`MaterialApp.builder`, and builds one portrait composition per screen — never a width-based
variant.

Use Flutter 3.27+, Dart 3.6+, Flame 1.18.x, `flame_audio ^2.1.0`, `flame_svg ^1.10.0`, `google_fonts`, and `shared_preferences`. Retain those compatible audio and SVG constraints with the studio's Flame 1.18.x baseline; newer `flame_audio` or `flame_svg` releases can require newer Flame or Flutter versions. Register these directories in `pubspec.yaml`:

```yaml
flutter:
  assets:
    - assets/images/sprites/
    - assets/images/ui/
    - assets/images/backgrounds/
    - assets/audio/sfx/
    - assets/data/
```

Do not hardcode studio-default fonts. Select display and body fonts from the game's Design DNA and use `google_fonts`.

Read `.claude/docs/directory-structure.md`, choose one V1–V5 structure, create the directories, and write the exact path map to `design/structure.md`. Read `.claude/rules/anti-slop-design.md`, `.claude/docs/mobile-first-contract.md`, `.claude/docs/layout-archetypes.md` and `.claude/docs/gameplay-screen-contract.md`; then write the Game UI Read, Design Signature, state composition map, per-screen layout recipes, and Similarity Check to `design/art-direction.md`. Design every one of them for a portrait phone and touch: the art-direction file specifies the 390×844 composition of each key screen, its P strategy for 360×640, 360×800 and 430×932, where the thumb reaches the primary action, where the integrated HUD/controls sit, and how the 55% area / normal 88% width thresholds are met. It must not plan a tablet, desktop or landscape layout, a width breakpoint, hover or keyboard interaction, a nested mini-game, a page-scrolling core loop, or a fake device frame.

## Phase 3 — asset generation and validation

Detect the environment without asking the user. Write `design/asset-format.md`, `design/asset-prompts.md`, and `design/asset-manifest.md` before generating assets.

Each manifest row must include a logical ID, output path, dimensions, class (`generate`, `derive`, `code`, or `reuse`), source ID, generator, prompt/style anchor, attempt count, SHA-256, alpha requirement, and validation verdict.

For a reference game, the identity ledger in `design/reference-contract.md` is the brief: copy it
into `design/art-direction.md` with the source path and role for every image (mapped previews and
user attachments alike), character traits, complete symbol cast (and each symbol's role in the
casual mechanic), frame and board materials, the casual board geometry, background, palette,
2D/2.5D finish and screen composition. Add source image paths and any direct-reuse crop
to each relevant asset-manifest row. Use the built-in image edit path with the source images, or
`python3 tools/gpt_image.py edit --image <source> --fidelity high` in headless Codex. Supply the
character image to character generation, gameplay image to symbols and board materials, and
background/key art to scene generation. A text-only `generate` call is appropriate only when no
usable visual source exists for that asset. Respect the transport's image/byte limits by making
separate focused calls; do not silently omit a required source file.

In PNG mode:

- Generate sprites/symbols on a flat chroma-key background with no border, frame, UI or baked shadow.
  No text except verified combo-marker inscriptions from `.claude/docs/visual-context.md`.
- Keep the full set consistent in light direction, materials, palette, perspective, and detail.
- Use one game background by default; derive menu variants locally unless a genuinely different world/composition is required.
  It is abstract slot style — gradient, glow, light, bokeh and the game's objects out of focus,
  never a place — unless the user asked for a setting or an exact reference's own background is
  one (`.claude/docs/visual-context.md` → "Backgrounds — abstract slot style").
  It is the game's **original** background: the campaign background is rendered from it in the
  approved panorama's world after approval, and both the carousel and that call attach it.
- Include at least one round game object — a gem, orb, bubble, ball or token from the game's own
  cast — that can model the store's five flying multiplier balls. Most casts already have one;
  name it in the manifest as the multiplier reference. The concept carousel needs it.
- When the field has a framed board or tile backing in the art direction, generate it now as a UI
  asset (`ui_board_frame`, `ui_tile`), so the carousel's gameplay sample is rendered from the
  same pieces the game will draw.
- Build ordinary controls, panels, icons, typography, shadows, glows, and VFX in code.
- Remove backgrounds only with `python3 tools/cutout.py`; never use fuzz-based global color transparency.
- Before Phase 3.6, compare the source with the generated asset set and documented board/layout
  plan; correct mismatched character, symbol, background, palette and finish. After implementation,
  compare a real phone gameplay screenshot beside the source for board and composition fidelity.

```bash
python3 tools/cutout.py --dir assets/images/sprites --check
python3 tools/cutout.py --dir assets/images/ui --check
flutter pub get
```

Validate that every generated file is a real PNG, required sprites/icons have clean alpha, no accidental SVG files exist in PNG mode, every declared asset exists, and the prompt/manifest ledgers are complete.

Outside Codex, the SVG fallback must use valid `<svg>` documents with a `viewBox`, consistent Design DNA, and no baked text. Validate every referenced path with `flutter pub get`.

## Phase 3.5 — real audio synthesis

Derive the mood from the concept and synthesize playable 16-bit/44.1 kHz WAV files:

```bash
python3 tools/synth_sfx.py --from-concept --sfx-dir assets/audio/sfx

ls -1 assets/audio/sfx/*.wav 2>/dev/null | wc -l
```

Required names: `sfx_button`, `sfx_navigate`, `sfx_action`, `sfx_score`, `sfx_error`, `sfx_win_small`, `sfx_win_big`, `sfx_win_mega`. Expect **8** files.

**Sound effects only — do not synthesize background music.** The generator can
render a BGM bed behind `--with-bgm`, but the result is weak next to the rest of
the game, so a game ships with SFX and silence unless the user explicitly asks
for music. Do not add `assets/audio/bgm/` to the pubspec `assets:` list: an asset
directory that does not exist is a hard `flutter build` failure. Ship the settings
screen's music toggle anyway — it costs nothing and means adding music later is a
content change, not a UI change. Silence here is the intended result: never report
it as a missing asset, a gap, or a TODO.

## Phase 3.6 — asset cohesion review

Follow `.claude/skills/asset-review/SKILL.md` as the art director. Create contact sheets including a mandatory 64 px gameplay-size sheet, evaluate AR1–AR11, and write `design/asset-review.md`. Fix only failed assets. Spend a recovery call only when the generated source itself is defective.

Exit only when the review records PASS, or when every REGENERATE item has been corrected and re-reviewed.

## Phase 3.7 — level and progression data

Generate data before implementation so Session 2 builds against a stable schema. Keep all numeric
content in JSON as the single source of truth. There is no economy: no currency, prices, shop or
random rewards (`.claude/rules/no-gambling.md`).

- Always create the category's balance config in `design/balance/`, using
  `.claude/docs/templates/balance-configs/` as the baseline, and run
  `python3 tools/simulate_balance.py` on it when the mechanic has a built-in simulator (B1 `swap`/
  `link`/`blast`, B2 `sort`, B3 `slide`, B5 `reflex`); otherwise record that the Session 2 bot
  report will verify it.
- G1/G2/G4/G6: `assets/data/levels.json` — at least 12 levels in worlds, each with the board/deal
  size, the budget (moves/shots/time), the goal and the new element it introduces; generated from
  or identical to the balance config.
- G3/G5: `assets/data/ramp.json` (or `stages.json`) — the spawn table / tier chain or the tempo ramp,
  plus milestone goals for endless play.
- Progression: `assets/data/progression.json` — star thresholds, world unlocks, achievements with
  their known rewards, collection album pages and the milestone that fills each, the daily
  challenge rules, earned booster grants (if the concept has boosters).
- Record 2–3 modes in the concept and handoff (e.g. Levels, Daily challenge, Endless/Zen).

Parse every JSON file before exit. Do not duplicate these values as inline constants in the future
game code.

## Phase 3.8 — handoff for Session 2

Write `production/session-state/autocreate-handoff-1.md` with:

- `Concept gate: required` on its own line — `tools/concept_gate.py` keys on it: implementation of
  this project waits for an approved concept carousel.
- Timestamp, game name, category, archetype, balance model, package ID, structure variant, Design Signature, per-screen recipe codes, audio mood, game language, and the reference-gameplay/translation decision.
- Links to the concept, production plan, structure, art direction, asset format/prompts/manifest/review, balance config, and level/progression data.
- Counts and paths for generated/derived assets, WAV files, levels/worlds or ramp stages, achievements/album pages, and modes.
- The lead kind and lead asset, the multiplier reference, the original game background, and the
  board/tile assets the carousel's gameplay sample is rendered from.
- A checklist confirming that Session 1 is complete and that gameplay implementation has not started.
- Session 2's required exit criteria: an approved concept (`concept_gate.py check --for implement`), the campaign background rendered in its world, `dart analyze` with zero errors, green tests, complete content wiring, a field that matches the approved gameplay sample, passed UI/no-gambling audit, a passed full-screen portrait gameplay-screen gate at the four phone sizes, verified balance, and 20/20 crash-prevention checks.
- A portrait-phone checklist: portrait lock, phone column, touch-only input, one composition per
  screen verified at 360×640, 360×800, 390×844 and 430×932 — and no desktop/tablet/landscape layout.
- The reference contract path and its binding (`exact`, `loose`, `description` or none).

Then continue to Phase 3.9 in this session.

## Phase 3.9 — the concept carousel

Run [the concept panorama procedure](../store-screenshots/references/concept-panorama.md),
Steps 1–7, in full: the layout draft from the real symbols and the composition guide that marks
the panel cuts (`store_compose.py composition-guide`), the `panorama-*` template rendered and
proved with `tools/prompt_template.py check`, one generation call with the identity asset, the
multiplier reference, the guide, the draft and the field's own assets attached, the bounded review
(three fresh renders and five region repairs per revision — `concept_gate.py budget` — with what
is still off published as known issues), the `triptych` export with the store's own flags, the
gameplay sample and its spec, and `tools/concept_gate.py publish`.

This is the store panorama, made now so the user can see the game before it is built. It obeys
every `/store-screenshots` rule — torso-to-head character on the first panel (or a gameplay-led
opening for an object/mechanic game, never an invented character), the field at a
three-quarter/3D angle caught mid-clear, all five labelled `x5`–`x100` balls in flight with at
least one per panel, the close-up lower-edge band, vivid key-art lighting — because after
approval it is exported unchanged. Its gameplay is also a promise: Session 2 builds the field to
look like it, so render it from the assets the game will draw, in the topology the data defines.

A reference game's carousel is the reference's world: attach its sources, and the AR11 identity
bar applies to the panorama too.

## Phase 3.10 — the approval gate

End Session 1 with a final report that presents the carousel and asks for a decision:

```text
CONCEPT READY FOR APPROVAL — <game name> (revision N)

Slides (production/store-art/concept/panels/):
  1. store-01.png — <what the first slide shows>
  2. store-02.png — <…>
  3. store-03.png — <…>
Panorama: production/store-art/concept/panorama.png
Gameplay sample: <topology, symbols, board housing, the moment shown> — the game is built to look like this
Known issues: <each one, as published with --known-issue — or "none">
Concept: <category, archetype, balance model, one-line pitch>

Approve to build the game, or describe what to change.
```

Then **stop**. Do not start Session 2 and do not approve the carousel yourself.

- **Web service** — the chat shows the three slides and the panorama with an Approve button. The
  service records the approval and starts `/autocreate-implement` in a new run; a typed message is
  revision feedback and arrives as `/autocreate --revise "<feedback>"`.
- **Standalone** — when the user approves, run `python3 tools/concept_gate.py approve --by user`,
  then start a clean-context agent with the instruction below. When the user asks for changes,
  follow `--revise`.

```text
You are Session 2 of /autocreate. The user approved the concept carousel. First read:
1. production/session-state/autocreate-handoff-1.md
2. .claude/skills/autocreate-implement/SKILL.md
3. production/store-art/concept/gameplay-sample.md, design/structure.md, design/art-direction.md, and design/gdd/game-concept.md

Execute Phases 4.0–10 exactly as specified by autocreate-implement: render the campaign background in the approved panorama's world, align the field's assets to the gameplay sample, then build the game to match it. Preserve Session 1's concept, assets, audio, balance, and level data. Exit only with zero analyzer errors, green tests, completed content wiring, a passed UI/no-gambling audit, verified full-curve balance, and 20/20 crash prevention. Then write autocreate-handoff.md and start Session 3 with autocreate-finalize.
```

If Agent is unavailable, continue locally by reading `autocreate-implement/SKILL.md`. If Session 2
fails, report the exact failure and the manual restart command `/autocreate-implement --resume`;
never claim the game is ready.

## `--revise "<feedback>"` — the user asked for changes

Follow concept-panorama.md → "Revisions". In short: an approval-only message changes nothing; a
change to the game itself goes through the Session 1 phase that owns it (concept, assets, data) and
regenerates only what it affects, fresh from the original references; `concept_gate.py revise`
archives the shown revision; the panorama is rendered again (fresh, or a region repair for a purely
local change) and published as the next revision; and the session ends at the approval gate again,
reporting what changed against the feedback.

If no concept was ever published (`concept_gate.py status` → NONE or DRAFTING after an interrupted
first run), treat the message as additional direction: resume Session 1 from the first phase
whose artifacts are missing or incomplete, then Phases 3.8–3.10. Never repeat completed asset
generation.

An approved concept is not revised — the game, its background and its store kit are built from it.
A look change after approval is an ordinary follow-up request against the built game.

## Final pipeline quality gates

The full pipeline succeeds only when:

- The user approved the concept carousel before implementation, and the store kit exports that
  approved panorama unchanged (`tools/check_store_kit.py --concept`).
- The complete game is playable in English and all screens, buttons, navigation, data, modes, progression, audio, animation, and edge states work.
- The no-gambling gate holds: no wager, currency, chance-based reward, casino control or gambling copy, and no age gate.
- `dart analyze` reports zero errors and `flutter test` is green.
- The declared B1–B6 balance model passes `tools/simulate_balance.py` over the complete content curve.
- Runtime verification and playtest produce at least five screenshots plus `REPORT.md`, with no exceptions or severe layout defects. The four portrait phones (360×640, 360×800, 390×844, 430×932) must pass `.claude/docs/mobile-first-contract.md`; idle and active gameplay captures must pass `.claude/docs/gameplay-screen-contract.md`: dominant integrated field, core controls visible without scrolling, usable buttons.
- The live field reads as the approved gameplay sample, side by side (V23): topology, symbols, board housing, tile backing, the clearing moment and palette.
- A reference game's art reads as the same world as its sources, side by side (AR11, V21), on the casual mechanic.
- The campaign background is ACCEPTED, rendered in the approved panorama's world, and the game runs on it (V22).
- `production/session-state/active.md` contains the current runtime verdict.
- Icons, splash, version, store metadata, and CI preparation are complete.

Release artifacts remain an explicit next action: `/release-package` for the downloadable project archive/APK, or full `/release-engineering` for a signed AAB.
