---
name: autocreate
description: "Zero-to-Production factory for complete C1-C6 gambling games. Produces an English game concept and production plan, reference-matched or concept-derived 2D/2.5D PNG assets in Codex, synthesized WAV audio, structured content/economy data, complete Flutter/Flame implementation, tests, compliance, math verification, runtime verification, and release preparation. The result is a complete publishable game, not a mini-demo."
argument-hint: "[--from-concept | --idea-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# AutoCreate — Zero-to-Production Complete Game Factory

Read `.claude/docs/visual-context.md` before planning or reviewing visuals. Whether this is a
reference request is decided by `tools/reference_detect.py` in Phase 0, not by reading the table
by eye. For a reference request, inspect every source it lists and read
`.claude/docs/game-concept-examples.md`. Carry the lead kind, references/adaptations, exact
board topology, Joker expression (when relevant), and verified multiplier-coin meanings from
the concept into the art direction, asset manifest and prompts. Classic unspecified slots
use 3×3; store gameplay placement is flexible and object-led games need no invented character.
The named requests Book of Ra, Joker, Joker Jewels, Shining Crown, Zeus Game, and Plinko must use
the exact preview mapping in that document; Joker Jewels resolves to every file in
`examples-games/joker-jewels/` and to a 5×3 board, not to the plain Joker row's 3×3. Recreate what
the preview shows — theme, character, symbol cast, palette, board and composition are matched, not
reinterpreted, and Variety Dimensions are not scrolled. Follow the source-quality and branding
limits in `game-concept-examples.md`. Never add a character to Shining Crown
or Plinko.

Build a complete production-ready gambling game. Do not ask the user questions: derive reasonable choices from the concept and record them.

All conversation, design documents, reports, prompts, code comments, generated game copy, store metadata, and screenshot captions must be in English. Use another player-facing language only when the user explicitly requests it and record that choice in the concept.

## Mandatory execution contract

The pipeline is split into three context sessions:

1. **Session 1 — pre-production (this skill, Phases 1–3.8):** concept, project bootstrap, structure and layout, assets, audio, content/economy data, then a handoff to Session 2.
2. **Session 2 — implementation (`autocreate-implement`, Phases 4–10):** game code, meta systems, content wiring, integration, build fixes, feel pass, tests, UI/compliance audit, balance, and crash prevention.
3. **Session 3 — finalize (`autocreate-finalize`, Phases 10.4–12):** campaign art — the store banner (the exact `/store-screenshots` banner prompt) and the game background with the main character whole in frame, wired into the game — then runtime/soak verification, playtest, session state, release-engineering preparation, and final report.

Every session must hand control to the next one with the Agent tool. If Agent is unavailable, write the handoff and continue in the same session by reading the next skill. Do not copy full history into a phase agent; give it only the handoff path, skill path, and exit criterion.

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
- Category-appropriate JSON content and economy data under `assets/data/` and `design/balance/`.
- `production/session-state/autocreate-handoff-1.md`, followed by Session 2.

Session 1 must not write gameplay code, screens, services, stubs, or TODO implementations. It must not claim that the game is complete.

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
Joker, Book of Ra, Shining Crown, Zeus, Plinko), binds attached images, flags an explicit
"same as / copy / по референсу" ask, and says whether the user's own mechanic or grid overrides
the family default. Its result only adds obligations: you may add a reference it missed; you may
never drop one it found or downgrade an attachment to "inspiration".

When `reference` is true:

- **Identity is the reference's.** The character (costume, headwear, face, build, expression),
  the symbol and sprite cast object for object, the reel strips, board and frame ornament, the
  background, palette, finish and UI materials are the source's — the finished game must read as
  the same game. Variety Dimensions are not scrolled and the Similarity Check does not push away
  from it (`game-concept-examples.md` → "How close to the reference — match it").
- **Play follows `topology_source`.** `family` → the family's classification and topology;
  `user mechanic` / `user grid` → the user's mechanic or grid, with the reference still governing
  identity (e.g. "Zeus Lightning Dice" is a dice game in Zeus's world with Zeus himself).
- Before Phase 3, view every source at full size and complete the contract's identity ledger. A
  missing mapped file is a blocker, not a reason to improvise.
- Every identity asset is generated **from its source image** (built-in edit path or
  `tools/gpt_image.py edit --image <source> --fidelity high`); text-only generation is allowed only
  for an asset with no visual source. Phase 3.6 AR11 and finalization's V21 compare side by side
  against these sources.
- The studio's generic art direction for original concepts does not apply; the reference's
  rendering style does.

`binding: description` (the user named an unmapped game with no image): match every described
trait, record that no pixels were available, and never claim pixel fidelity.

## Phase 1 — concept

Run the logic from `.claude/skills/auto-idea/SKILL.md`, unless `--from-concept` was supplied. Save the result to `design/gdd/game-concept.md`.

The concept must include:

- Category C1–C6, math model M1–M6, archetype, compliance obligations, and English game language.
- A reference bar naming 2–3 successful games in the category, the specific feel/timing lesson from each, and the new game's differentiating hook. Never copy their content or art. This bar is separate from a mapped local preview: a named request's preview is close context to stay with, not a competitor to differentiate from.
- A complete production plan with content volume, 2–3 modes, progression, virtual economy, achievements/daily loop, service abstractions, telemetry, and compliance.
- A context-derived Game UI Read, multidimensional Design Signature, per-screen layout recipes,
  explicit `lead_kind` plus `menu_role: dominant | supporting | absent`, and a recorded
  Similarity Check.
- For a reference request (Phase 0), the source paths from `design/reference-contract.md`, the
  identity ledger, `lead_kind`, and the mechanic/topology decision with its `topology_source`. Do
  not proceed to asset generation until this reference record is explicit, and the concept's
  theme, character, symbol cast, palette, board and composition must be the reference's,
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
user attachments alike), character traits, complete symbol cast, reel strips and board geometry,
background, palette, 2D/2.5D finish and screen composition. Add source image paths and any direct-reuse crop
to each relevant asset-manifest row. Use the built-in image edit path with the source images, or
`python3 tools/gpt_image.py edit --image <source> --fidelity high` in headless Codex. Supply the
character image to character generation, gameplay image to symbols and board materials, and
background/key art to scene generation. A text-only `generate` call is appropriate only when no
usable visual source exists for that asset. Respect the transport's image/byte limits by making
separate focused calls; do not silently omit a required source file.

In PNG mode:

- Generate sprites/symbols on a flat chroma-key background with no border, frame, UI or baked shadow.
  No text except verified multiplier-coin inscriptions from `.claude/docs/visual-context.md`.
- Keep the full set consistent in light direction, materials, palette, perspective, and detail.
- Use one game background by default; derive menu variants locally unless a genuinely different world/composition is required.
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

Required names: `sfx_button`, `sfx_navigate`, `sfx_action`, `sfx_coin`, `sfx_error`, `sfx_win_small`, `sfx_win_big`, `sfx_win_mega`. Expect **8** files.

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

## Phase 3.7 — content and economy data

Generate data before implementation so Session 2 builds against a stable schema. Keep all numeric content in JSON as the single source of truth.

- Always create the category's canonical math config in `design/balance/`, using `.claude/docs/templates/math-configs/` as the baseline.
- C1/C2: `assets/data/bet-tiers.json` with bet levels, limits, and bonus-mode parameters.
- C3: `assets/data/stage-config.json` with more than one unlock/season stage.
- C4: `assets/data/banners.json` with more than one banner, pools, rates, and rotation.
- C5: `assets/data/run-config.json` with round thresholds, at least three modifiers, and shop prices.
- C6: `assets/data/board-config.json` with more than one board/risk profile.
- Economy: `assets/data/economy-config.json` with starting balances, catalog prices, and progression/daily/achievement rewards.
- Record 2–3 modes in the concept and handoff.

Parse every JSON file before exit. Do not duplicate these values as inline constants in the future game code.

## Phase 3.8 — handoff to Session 2

Write `production/session-state/autocreate-handoff-1.md` with:

- Timestamp, game name, category, archetype, math model, package ID, structure variant, Design Signature, per-screen recipe codes, audio mood, and game language.
- Links to the concept, production plan, structure, art direction, asset format/prompts/manifest/review, balance configs, and content data.
- Counts and paths for generated/derived assets, WAV files, levels/stages/banners/boards, economy entries, and modes.
- A checklist confirming that Session 1 is complete and that gameplay implementation has not started.
- Session 2's required exit criteria: `dart analyze` with zero errors, green tests, complete content wiring, passed UI/compliance audit, a passed full-screen portrait gameplay-screen gate at the four phone sizes, verified balance, and 20/20 crash-prevention checks.
- A portrait-phone checklist: portrait lock, phone column, touch-only input, one composition per
  screen verified at 360×640, 360×800, 390×844 and 430×932 — and no desktop/tablet/landscape layout.
- The reference contract path and its binding (`exact`, `description` or none).

Then start a clean-context agent with this instruction:

```text
You are Session 2 of /autocreate. First read:
1. production/session-state/autocreate-handoff-1.md
2. .claude/skills/autocreate-implement/SKILL.md
3. design/structure.md, design/art-direction.md, and design/gdd/game-concept.md

Execute Phases 4–10 exactly as specified by autocreate-implement. Preserve Session 1's concept, assets, audio, balance, and content data. Exit only with zero analyzer errors, green tests, completed content wiring, a passed UI/compliance audit, verified full-curve balance, and 20/20 crash prevention. Then write autocreate-handoff.md and start Session 3 with autocreate-finalize.
```

If Agent is unavailable, continue locally by reading `autocreate-implement/SKILL.md`. If Session 2 fails, report the exact failure and the manual restart command `/autocreate-implement`; never claim the game is ready.

## Final pipeline quality gates

The full pipeline succeeds only when:

- The complete game is playable in English and all screens, buttons, navigation, data, modes, progression, economy, audio, animation, and edge states work.
- `dart analyze` reports zero errors and `flutter test` is green.
- The declared M1–M6 model passes its verifier over the complete content curve.
- Runtime verification and playtest produce at least five screenshots plus `REPORT.md`, with no exceptions or severe layout defects. The four portrait phones (360×640, 360×800, 390×844, 430×932) must pass `.claude/docs/mobile-first-contract.md`; idle and active gameplay captures must pass `.claude/docs/gameplay-screen-contract.md`: dominant integrated field, core controls visible without scrolling, usable buttons.
- A reference game reads as the same game as its sources, side by side (AR11, V21).
- Campaign art is ACCEPTED and the game runs on the campaign background (V22).
- `production/session-state/active.md` contains the current runtime verdict.
- Icons, splash, version, store metadata, and CI preparation are complete.

Release artifacts remain an explicit next action: `/release-package` for the downloadable project archive/APK, or full `/release-engineering` for a signed AAB.
