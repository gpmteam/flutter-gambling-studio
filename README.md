# Flutter Casual Game Studio

A Flutter + Flame studio for complete portrait-phone casual games, from concept to a verified,
release-ready project. The repository retains its historical name, `flutter-gambling-studio`.

**Casino-grade or reference-matched visuals; strictly casual gameplay.** References guide
characters, symbols, frames, backgrounds, palette and rendering. A casino reference never
supplies casino gameplay: its art becomes a match board, tile puzzle, merge game, peg clearer,
reflex game or logic puzzle. An already-casual reference may supply its own gameplay: Zeus keeps
its 7×6 link grid. Scores are points, with stars, levels and deterministic unlocks. No wagers
(including on points), real or virtual money, wallets, currency shops or chance-based prizes.

The canonical contracts are [game categories](.claude/docs/game-categories.md),
[balance models](.claude/docs/balance-models.md), [no gambling](.claude/rules/no-gambling.md),
[visual references](.claude/docs/game-concept-examples.md) and
[portrait phones](.claude/docs/mobile-first-contract.md).

## Categories and balance

| Category | Mechanics | Archetypes | Balance model |
|---|---|---|---|
| G1 Match & Cascade | Swap, link, blast, rotate | A–D | B1 board simulation |
| G2 Tile & Sort | Triple tray, pairs, sort, patience | E–H | B2 solvable deals |
| G3 Merge & Place | Slide/drop merge, block place, merge grid | I–L | B3 run length |
| G4 Aim & Physics | Bubble, peg clear, bricks, knockdown, draw & guide | M–Q | B4 shot simulation |
| G5 Arcade Reflex | Runner, stacker, catcher, slicer, flyer, target throw | R–W | B5 reflex ramp |
| G6 Logic & Progression | Paths, pipes, unblock, memory, logic grids | X–AB | B6 solver curve |

The 28 archetypes are starting points, not a limit on original casual ideas. Every concept names
its category, mechanic and verifiable balance model before implementation. Budgets, targets,
spawn tables and tempo ramps live in JSON; the game reads the same data. One seeded `GameRng`
drives gameplay, and the pure rules engine resolves each move before animation plays it back.
Cosmetic randomness uses a separate stream.

```bash
python3 tools/reference_detect.py --prompt 'Make Joker Jewels' --new-game --json
python3 tools/simulate_balance.py --model b1 --config design/balance/level-config.json
python3 tools/simulate_balance.py --model report --config design/balance/bot-report.json
python3 tools/simulate_balance.py --selftest
python3 -B tools/check_no_gambling.py
```

Balance exits: 0 PASS, 1 CONCERNS, 2 FAIL. Unsupported mechanics use the game's own headless bot
in `test/balance/bot_sim_test.dart`; the report grader verifies its curve and required evidence.
No-gambling static checks exit 0 or 2 and are paired with a review of actual gameplay and copy.

## Getting started

Use Flutter 3.27+, Dart 3.6+, Python 3, and Claude Code, Codex or Gemini. Chrome/Chromium and
Node 21+ support browser runtime verification. Image generation uses GPT Image 2 through the
built-in image tool or `tools/gpt_image.py` in headless Codex; sound effects come from
`tools/synth_sfx.py`. Background music is opt-in.

```bash
git clone https://github.com/leofillium/flutter-gambling-studio.git
cd flutter-gambling-studio
```

Claude reads `CLAUDE.md` and `.claude/`. Codex reads `AGENTS.md` and the mappings in `.codex/`;
commands are runbooks in `.claude/skills/<name>/SKILL.md`. Gemini reads `GEMINI.md` and `.gemini/`.
If Codex needs project skill discovery:

```bash
bash tools/setup-codex-cli.sh link
bash tools/codex-doctor.sh
```

Restart the client after changing skill discovery. Manual hooks run through
`bash tools/codex-hooks.sh <hook-name>`.

## Creation pipeline

`/autocreate` runs three sessions and saves file-based handoffs for interrupted work:

1. Concept, reference/mechanic detection, production plan, Flutter scaffold, assets, audio and
   JSON level/progression/balance data.
2. `/autocreate-implement`: rules, Flame presentation, all UI screens, save/progression/meta
   systems, integration, analysis, tests, feel pass, UI/no-gambling audit, full-curve balance
   and crash prevention.
3. `/autocreate-finalize`: campaign art and game background, Chrome runtime and soak tests,
   actual gameplay playtest, session state, release preparation and the final report.

The result is release-ready. Native build and downloadable archive creation are explicit user
runs of `/release-package`, which writes
`project_zip/<name>-<timestamp>.zip` with `source/`, `apk/app-release.apk`, `screenshots/` and
`RELEASE_INFO.md`. `/release-engineering --prep-only` prepares icons, splash, version, CI and
store metadata without creating a keystore or building native artifacts.

Every app is a touch-only portrait phone game. Verify 360×640, 360×800, 390×844 and 430×932;
a wide preview host shows the same phone composition in a phone column. No desktop/tablet/
landscape variants or fake device frame. All generated documents, code, reports and commit
messages are English. Player-facing copy and store metadata are English unless explicitly
requested otherwise.

## Commands

| Command | Purpose |
|---|---|
| `/start` | Studio overview and routing |
| `/brainstorm [theme]` | Interactive casual concept |
| `/auto-idea [--list / --archetype A-AB / --category G1-G6]` | Autonomous complete concept |
| `/autocreate [--from-concept / --idea-only]` | Full creation pipeline |
| `/autocreate-implement`, `/autocreate-finalize` | Resume pipeline sessions 2 and 3 |
| `/map-systems` | Dependency graph and implementation plan |
| `/design-system [board-rules / tier-chain / tempo-ramp / …]` | One system's GDD and balance |
| `/prototype [mechanic]` | Isolated feedback prototype |
| `/team-dev [system]` | Coordinate design, balance, code, VFX and audio |
| `/generate-asset`, `/generate-png-asset`, `/svg-to-png` | Context-matched assets and conversions |
| `/asset-review` | Set consistency, source fidelity and in-game readability |
| `/design-review`, `/code-review`, `/ui-audit` | Design, implementation and runtime UI review |
| `/balance-check` | Difficulty/solvability verification across the whole curve |
| `/gate-check [concept / design / code / qa / release]` | PASS / CONCERNS / FAIL transition gate |
| `/emulator-test`, `/playtest` | Screen/crash checks and actual gameplay verification |
| `/continue-project`, `/add-feature [feature]` | Resume or extend a casual game |
| `/perf-profile`, `/tech-debt`, `/hotfix`, `/architecture-decision` | Maintenance and decisions |
| `/release-checklist` | Final GO / NO-GO, including the no-gambling gate |
| `/release-engineering`, `/release-package` | Native release preparation/build/package |
| `/store-screenshots` | Campaign panorama, authentic phone slides, icon and feature graphic |
| `/auto-learn` | Evidence-based framework proposals on isolated learning branches |

## Agents and rules

Directors own creative/technical decisions. `game-designer` owns the mechanic and GDD;
`balance-designer` owns B1–B6 configs and verification. `mechanics-programmer` writes the pure
rules engine; `juice-artist` and `sound-designer` make earned actions readable and tactile.
`lead-programmer`, `ui-programmer` and `meta-systems-programmer` integrate presentation,
all screens and deterministic progression. `art-director`, `performance-analyst`, `qa-tester`
and `release-manager` verify visuals, runtime, tests and readiness. `auto-learner` records
concrete reusable evidence under the repository's learning policy.

Canonical roles live in `.claude/agents/`; Gemini copies live in `.gemini/agents/`. Rules cover
engine API, gameplay, UI, design craft, JSON data, GDDs, tests and the unconditional no-gambling
gate. Session hooks display progress, detect gaps, scan casual-game requirements before commits,
validate assets and preserve checkpoints. Commit/push hooks remain advisory; quality gates
block release on violations.

## Reference art and store kits

The detector is authoritative for named English/Russian families and attached images. Record
`design/reference-contract.md`; preserve actual source character identity and visual finish,
with matching assets generated from source images. Do not copy logos, betting controls, odds or
payout numbers. Follow [visual context](.claude/docs/visual-context.md) for exact topology,
image transport and branding boundaries.

Store scenes show decisive casual play, actual game pieces and a character only where the
concept has one. The five x5/x10/x25/x50/x100 combo balls are store-only scene decoration,
never prizes or fabricated runtime values. Preserve authentic captures and use the shared
[campaign templates](.claude/skills/store-screenshots/references/campaign-prompts.md).
Metadata describes casual play and records “simulated gambling: no”; age ratings come from
actual content and art. No gambling disclaimer or age gate.

## Layout and validation

```text
.claude/agents, skills, rules, docs, hooks    canonical studio framework
.codex/, .gemini/, AGENTS.md, GEMINI.md      CLI compatibility
lib/game, systems, models                   config, seeded RNG, pure rules and state
lib/components, screens                    Flame presentation and Flutter UI
assets/images, audio, data                  generated assets and structured content
design/gdd, balance, references             concept, reports and visual source contract
production/session-state, session-logs      checkpoints and evidence
tools/, tools/tests/                        deterministic helpers and regression tests
```

```bash
python3 -B -m unittest discover -s tools/tests -p 'test_*.py'
node --test tools/tests/test_web_*.mjs
flutter pub get
dart analyze lib/
flutter test
```

Python image/compositor tests need Pillow and NumPy; skill frontmatter checks need PyYAML.
Runtime screenshots and actual play remain required: static tests do not prove visual fidelity
or that a game is playable. See [the MVP guide](docs/how-to-build-an-mvp.md).

MIT License; see [LICENSE](LICENSE).
