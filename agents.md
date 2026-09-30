# Repository Guidelines — Flutter Casual Game Studio

## Codex CLI Instructions

This is a **casual game studio** (the repository keeps its historical name,
`flutter-gambling-studio`). Every concept falls into one of six categories — G1 match & cascade,
G2 tile & sort, G3 merge & place, G4 aim & physics, G5 arcade reflex, G6 logic & progression — and
declares a verifiable balance model (B1–B6). See `.claude/docs/game-categories.md`.

**Casino-grade looks, never gambling gameplay.** A game may look like premium casino key art or
reproduce a reference exactly, but it plays as a casual skill game scored in points. There are no
bets, stakes or wagers; no money of any kind — real or virtual (no coins, chips, gems or credits as
a currency, no balance, no shop); no chance-based rewards (no slot reels that spin for an outcome,
roulette, prize wheels, loot boxes, gacha, scratch cards, plinko-for-prizes, pachinko, coin
pushers, crash); no casino games (poker, blackjack, roulette), even for points. Points, stars,
levels and progress-based unlocks only. When a user or a reference asks for a gambling mechanic,
keep the look and build the casual translation from `.claude/docs/game-categories.md` →
"Translating a gambling ask". This is a hard gate: `.claude/rules/no-gambling.md`.

Every generated game is a **portrait phone game**, played by touch. Design every concept,
layout recipe, asset and screen for a phone held upright and verify it at 360×640, 360×800,
390×844 and 430×932. There is no tablet, desktop or landscape layout at any stage; a wide host
shows the same phone screens in the phone column, never a device frame. Follow
`.claude/docs/mobile-first-contract.md`.

Choose each game's rendering style from its brief and visual references. Polished 2D and modeled
2.5D are both valid; a slot-style key-art finish (jewel-toned symbols, gold edging, glossy
highlights) is the studio's signature for original games. Keep the asset set coherent in
linework, depth, materials, palette, detail and light. Inspect matching `examples-games/` images by
default. Whether a request is a reference request is decided by `tools/reference_detect.py` (named
families in English or Russian, attached images under `design/references/user/`, explicit "same
as / copy / по референсу" asks) and recorded in `design/reference-contract.md`, together with the
mechanic that governs play. A reference game must match its sources' character, sprites and
symbols, frame, background, palette, composition and visual finish closely — and build the casual
mechanic the detector names, never the casino gameplay a preview shows (Zeus is the one mapped
reference whose own gameplay, a 7×6 link grid, is already casual). Pass the actual reference
images into image generation when the tool supports it, and compare the runtime game beside the
references. See `.claude/docs/visual-context.md` and `.claude/docs/game-concept-examples.md` for
the reference contract and limits.

All store screenshot sets use premium key-art marketing composition: lead with the decisive
moment of play — the chain lighting up, the cascade, the merge, the clearing shot — with premium
depth and tactility, controlled anticipation and reward focus, and real active gameplay large and
readable. This is composition—not a mandatory black/neon/gold skin; every palette, material,
character and type choice still comes from the current game's Design DNA. Never use cropping or
device chrome to hide a weak gameplay layout.
For panorama carousel panels, use the actual gameplay capture only as image-generation context.
Generate the entire scene, including a natural three-quarter/3D view of the mechanic, as one
image. Never paste, warp, or texture-map the capture or a gameplay board plate into the panorama,
and never generate a placeholder scene to fill with gameplay afterward. Verify the generated
topology, symbols, and scoring state against the capture; stop if the image cannot preserve them.
Record `lead_kind: character | object | mechanic` before composing. Zeus, Joker and chicken games
default to a large character on the first panel. Object/mechanic games such as Shining Crown and
Plinko need no invented mascot or character-only opening. When the game has a main character,
it is mandatory to show that character from torso to head in the banner and the panorama. The
bottom edge or the foreground band cuts the body through the torso, so no legs or feet are
visible, and the character is never standing full length or flying. Leave visible space above the
complete head/headwear in the final panel crop (at least 2% of panel height). Keep attached forms
clear of the first seam. Animal framing fits the species but also shows no legs or feet.
Real game objects form the cropped bottom frame and fall through the picture, while the far
background stays broad, smooth, and subordinate so
those subjects lead. Store grading is restrained and theme-led by default: preserve the Design DNA's
exposure and add only enough saturation for the game objects to read cleanly. Brightness lifts, bloom,
blown light sources, and aggressively saturated treatments are opt-in art direction, never universal
delivery requirements. Generic stage furniture does not count as game objects, and a dark,
hyper-detailed far plane can still fail the readability contract. The Google Play feature graphic
uses its own horizontal composition.
A left-heavy 3/5–2/5 split is optional; object/mechanic scenes may use the full width. Keep the real
object frame across the lower edge and no reserved device-shaped zone. The shipped feature graphic
is text-free — the scene plus one framed phone on the right with a real capture, and no title,
tagline, logo or copy on the left or anywhere else.
Across both formats, place decisive gameplay wherever it reads best, with many real sprite assets in a spill
across the full lower edge, varied in scale, height, rotation, overlap, and depth rather than arranged
as a tidy row or a lower-left pile.
Gameplay may appear on any panel, span the right two, or span all three. Noncritical board
structure may cross seams; protect faces, inscriptions and decisive symbols from gaps.
A narrower field is valid when its proportions or readability require it. Preserve the
bottom spill and add recognizable flying/falling game objects at varied depths above it. Choose
an expressive marketing background when the theme benefits, with the far plane subordinate.
Matching `examples-games/` previews are default references; other relevant `examples/` images may also guide composition;
record what is borrowed and keep the actual game's assets, mechanics and Design DNA authoritative.
Store-screenshot generation preserves the actual game's existing menu, gameplay, splash, and shared
background assets and wiring. A runtime-background redesign is a separate, explicit opt-in; never
replace the game's background merely to make it match newly generated marketing art. The one
exception is campaign art (`.claude/skills/store-screenshots/references/campaign-art.md`), run by
`/autocreate-finalize` Phase 10.4: it renders the banner from the shared template (the exact
store-screenshots banner prompt, proven with `tools/prompt_template.py check`), generates a
portrait game background in the banner's world with the main character whole inside the frame
(no combo balls, lettering, board or UI), and wires that background into the game before
runtime verification. `/store-screenshots` then builds the panorama, icon and feature graphic on
the banner and puts the phone slides on the same game background; it runs campaign art itself only
when the handoff is missing or stale.

An unspecified match game uses a 7×8 board; reference families use the "Build as" topology in
`.claude/docs/game-concept-examples.md` (Zeus keeps its 7×6 grid). Preserve explicit or existing
variants. Joker defaults to a mischievous, slightly vicious theatrical trickster, playful rather than
an elegant courtier or horror character. Prefer x2/x5/x10 combo badges in gameplay where the game's
scoring model has a combo multiplier on points; never invent runtime multipliers or change balance
solely for promotional art. Every generated game's store screenshot set includes theme-matched
combo balls marked x5, x10, x25, x50 and x100 as store-only scene decoration, even when those
values are absent from the game. Across all six categories, plan each ball as a prominent
secondary subject at roughly 35-40% of the final portrait panel width. The flying balls are
mandatory: all five appear in the banner and the panorama, and every panorama panel carries at
least one. Keep the balls visibly flying at varied heights and depths around the character and
across the gameplay. They may cover gameplay, symbols, foreground objects, and other scene
elements; the main character is the only subject they must never cover. Keep them out of real
gameplay captures, and never present them as prizes.

All agent responses must be in English, and every artifact the pipeline writes — design documents, concepts, reports, session state and commit messages — must be in English as well. Dart/Flutter code, file paths, class names and CLI commands are English by definition.

The generated game ships in English too: every player-facing string (menus, buttons, HUD, how-to-play, level goals, result messages, empty states) plus store metadata and screenshot captions. The only exception is an explicit user request for a different language — then the player-facing copy uses that language, the choice is recorded in `design/gdd/game-concept.md`, and everything else (identifiers, file names, comments, design docs, reports) stays English. Do not switch the game's language on your own initiative and do not infer it from the language the user is typing in. Before writing code, read `CLAUDE.md`, `.claude/docs/game-categories.md`, `.claude/docs/balance-models.md`, `.claude/rules/no-gambling.md`, `.claude/rules/game-code.md`, `.claude/rules/engine-code.md`, `.claude/rules/ui-code.md`, `.claude/rules/anti-slop-design.md`, `.claude/docs/mobile-first-contract.md`, `.claude/docs/gameplay-screen-contract.md`, `.claude/rules/test-standards.md`, `.claude/rules/data-files.md`, `.claude/rules/design-docs.md`, `.claude/docs/technical-preferences.md`, `.claude/docs/coding-standards.md`, `.claude/docs/directory-structure.md`, and `.claude/docs/coordination-rules.md`.

Treat slash commands as manual runbooks. When a user types `/brainstorm`, `/autocreate`, `/team-dev`, `/code-review`, `/ui-audit`, `/emulator-test`, `/balance-check`, `/release-package`, `/release-checklist`, or another studio command, open the matching file in `.claude/skills/*/SKILL.md` and follow it. For specialized roles, use the persona briefs in `.claude/agents/*.md`. If needed, run helper checks with `bash tools/codex-hooks.sh <hook-name>`.

Note on `/autocreate`: it is the full Zero-to-Production pipeline, split across three sessions. It MUST run every phase without skipping:

1. Session 1 — pre-production: reference/mechanic detection, concept, classification (category G1-G6 + balance model B1-B6), Production Plan, `flutter create --platforms android,ios,web`, assets and audio, level/balance data.
2. Session 2 (`autocreate-implement`, Phases 4 → 10) — implementation: code plus meta systems, content wiring, integration, `dart analyze lib/` looped until 0 errors, `flutter test` all green, feel pass, UI audit, curve-based balancing, crash prevention.
3. Session 3 (`autocreate-finalize`, Phases 10.4 → 12) — campaign art (store banner + game background with the character whole in frame, wired into the game), runtime and soak verification via Chrome CDP with auto-fix, `/playtest`, session state, release-engineering PREP (icons, splash, versioning, store metadata, CI — WITHOUT building the AAB/APK and without a keystore) and the final report.

`/autocreate` leaves the project release-ready but does NOT produce the downloadable archive. Building the release artifact is an explicit user action: `/release-package` takes the screenshots, runs `flutter build apk --release`, runs `flutter clean` and archives the whole project into a **`.zip`** in `project_zip/`.

Final deliverable of `/release-package`: `project_zip/<name>-<ts>.zip`, containing `source/`, `apk/app-release.apk`, `screenshots/` and `RELEASE_INFO.md`. The archive format is strictly `.zip` — the web service picks up `project_zip/*.zip` and registers it as the downloadable chat artifact.

Runtime verification runs on Chrome/Web by default and needs no emulator. The Android path is a fallback: if there is no Android device, `/emulator-test` tries to auto-start the first available AVD (`emulator -list-avds | head -1`). The final report mentions these commands as re-run options after manual edits.

If Codex CLI does not detect this project or local skills, run:

- `bash tools/setup-codex-cli.sh link`
- `bash tools/codex-doctor.sh`

Then restart Codex CLI.

## Automatic learning during studio work

After every concrete reusable failure, user correction, or verified faster approach, invoke
`.claude/skills/auto-learn/SKILL.md` and the `.claude/agents/auto-learner.md` role. Record evidence,
deduplicate by cause/remedy, implement a bounded improvement in an isolated worktree, validate
it, and push a `learning/*` proposal branch using `tools/auto_learn.py`. The owner has authorized
these proposal pushes in `.claude/auto-learning.json`; do not ask again. Only the owner approves
or merges. Never merge, force-push, publish unrelated work, or silently adopt unmerged rules.
Suggest or implement new skills, agents, scripts or rules only when the observed gap warrants
them; prefer correcting existing guidance. Keep the no-gambling gate, seeded-RNG/balance rules
and quality gates intact. Process pending findings during agent sessions; this is not an
always-running background service. An explicit pause or narrower user request overrides
automatic learning. See `.claude/docs/auto-learning.md` for commands, evidence requirements and
recovery.

## Project Structure & Module Organization

This repository is a Flutter + Flame **casual** game studio template. Core guidance lives in [`CLAUDE.md`](CLAUDE.md), with canonical rules in [`.claude/rules/`](.claude/rules), role briefs in [`.claude/agents/`](.claude/agents), reusable runbooks in [`.claude/skills/`](.claude/skills), and helper scripts in [`.claude/hooks/`](.claude/hooks). Codex compatibility docs live in [`.codex/`](.codex). Store design docs in `design/`, process notes in [`docs/`](docs), and session artifacts in [`production/`](production). Generated game apps should use `lib/game/`, `lib/components/`, `lib/systems/`, `lib/models/`, `lib/screens/`, `assets/`, and `test/`.

## Build, Test, and Development Commands

Use these commands after initializing or opening a Flutter app in this repo:

- `flutter create . --project-name game_app`: scaffold the Flutter project.
- `flutter pub get`: install dependencies.
- `dart format .`: format Dart files.
- `dart analyze` or `flutter analyze`: run static analysis.
- `flutter test`: run unit and widget tests.
- `bash tools/codex-hooks.sh detect-gaps`: check for missing required files.

## Coding Style & Naming Conventions

Use Dart 3.6+ with null safety, sealed classes, and pattern matching. Indent with 2 spaces. Prefer `const` and `final`; use `var` only when reassignment is required. Name files in `snake_case.dart`, classes in `PascalCase`, and fields or methods in `camelCase`. Keep gameplay constants in `lib/game/game_config.dart`; keep balance-model numbers (levels, budgets, tempo ramps, spawn tables) in the JSON config under `design/balance/` and load them — never duplicate a number in both. Use a logger instead of `print()`.

## Testing Guidelines

Place tests under `test/` and name them `*_test.dart`, for example `test/systems/board_engine_test.dart`. Cover the pure rules engine, state transitions, and edge cases. Every game must verify that the same seed reproduces a level exactly, that a move is resolved before its animation, that scoring is exact, that no dead end exists (reshuffle, solvable deals), and the category's balance model. Verify the model with `python3 tools/simulate_balance.py --model [b1-b6|report] --config design/balance/<file>.json` — exit code 0 means PASS. Run `python3 -B tools/check_no_gambling.py` and `flutter test` before opening a pull request.

## Commit & Pull Request Guidelines

Use focused conventional commits such as `feat: add rocket special to the blast board` or `fix: move tempo ramp constants into game config`. Pull requests should state the purpose, affected areas, test status, linked issues, and include screenshots or recordings for UI changes.

## Architecture & Safety Notes

Follow [`.claude/rules/game-code.md`](.claude/rules/game-code.md), [`.claude/rules/engine-code.md`](.claude/rules/engine-code.md), [`.claude/rules/ui-code.md`](.claude/rules/ui-code.md), and [`.claude/rules/no-gambling.md`](.claude/rules/no-gambling.md). Do not `await` inside `update()` or `render()`, avoid allocations in hot paths, route all gameplay randomness through the one seeded `GameRng`, resolve every move in the pure rules engine BEFORE the animation starts, and keep gameplay values out of inline magic numbers.

The no-gambling gate is a release blocker, not a nice-to-have: no wagers, no currency, no chance-based rewards, no casino games, no gambling vocabulary in the UI or store copy, and "simulated gambling: no" on the store questionnaires.
