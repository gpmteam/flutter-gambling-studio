---
name: autocreate-implement
description: "Session 2 of the /autocreate pipeline (Phases 4.0 → 10): implementation, started only after the user approves the concept carousel. Phase 4.0 renders the campaign game background in the approved panorama's world and aligns the field's assets to its gameplay sample; then five agents in sequence write the code plus the meta systems with the field built to look like that sample, wire up content, integrate, build to 0 errors, run a feel pass, tests, a UI audit (including the no-gambling gate), curve-based balancing and crash prevention. The heavy phases are DELEGATED to fresh sub-agents without a full-history fork, so the orchestrator does not exhaust its context or TPM. At the end it spawns Session 3 (autocreate-finalize). Started by the web service's Approve button, by Session 1 after a standalone approval, or manually."
argument-hint: "[--resume]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Implement — Session 2 (implementation)

**Purpose**: turn Session 1's pre-production (concept + assets + audio + data) and the concept
carousel the user approved into fully working, clean, tested game code that looks like the
carousel's gameplay sample — and hand it to Session 3 for runtime verification. This is the
**middle** of `/autocreate`'s three context sessions.

```
Session 1 (autocreate)  →[carousel]→  user approves  →  Session 2 (THIS skill)  →[autocreate-handoff.md]→  Session 3  →  store kit
   concept/assets/data      APPROVED          4.0 background + sample alignment,           finalize          /store-screenshots
                                              4–10 code/tests/audit/balance
```

---

## 🚨 MANDATORY CONTRACT

1. ✅ Reads `production/session-state/autocreate-handoff-1.md` **as its first action**
2. ✅ Refuses to start without an approved concept carousel:
   `python3 tools/concept_gate.py check --for implement` (a project made before the gate reports
   LEGACY and continues without one)
3. ✅ Validates Session 1's artifacts (pubspec, structure, `assets/data/*.json`, `assets/audio/*`)
4. ✅ Runs **Phase 4.0** before any code: the campaign background in the approved panorama's
   world, wired as the only background from the start, and the field's assets aligned to the
   gameplay sample (`production/store-art/concept/gameplay-sample.md`)
5. ✅ Reads `design/asset-format.md` to determine the asset format (PNG vs SVG) and passes it to
   the agents (Agent B: `Image.asset()` for PNG, `SvgPicture` for SVG; Agent A: file extensions)
6. ✅ Reads `.claude/docs/mobile-first-contract.md` and
   `.claude/docs/gameplay-screen-contract.md`, then passes the portrait-phone-only target (one
   composition per screen, touch only, portrait lock, the phone column in `MaterialApp.builder`),
   stable keys, control sizing, and the four-phone matrix to Agent B, QA, integration, and UI
   audit. Agent B builds no tablet, desktop or landscape layout — there is none to build.
7. ✅ Passes the gameplay sample (`gameplay-sample.md` + `gameplay-sample.png`) to Agents B and
   C and into `lib/contracts.md`: the live field is built to look like it — the same topology,
   symbols, board housing, tile backing, clearing moment and palette, seen square-on
8. ✅ For a reference game, passes `design/reference-contract.md` to every agent that touches
   visuals (B, C) and keeps the game identical to its sources: no substituted symbols, re-themed
   screens or "improved" palette
9. ✅ Runs **Phases 4 → 10** using this skill's execution map, role briefs, and exit criteria.
   `.claude/skills/autocreate/SKILL.md` owns Session 1 and routes here; it does not contain
   the implementation phase definitions.
10. ✅ **Delegates the heavy phases to sub-agents** (see the map below) — the orchestrator does
   NOT read all of `lib/` itself, it works from command output (`dart analyze`/`flutter test`)
   and the agents' summaries
11. ✅ At the end (Phase 10.7) writes `autocreate-handoff.md` and **spawns Session 3** through
   the Agent tool

**Forbidden:**
- ❌ Starting without an approved concept carousel, or approving it yourself
- ❌ Changing, regenerating or re-exporting anything in `production/store-art/concept/` — the
  approved panorama is the contract the game, the background and the store kit are built from
- ❌ Rewriting Session 1's concept/assets/audio/data (you may only extend `GameConfig` with
  values from `assets/data/*.json`; Phase 4.0's campaign background and sample-alignment assets
  are the sanctioned additions)
- ❌ Changing balance or level data other than through balance-designer in Phase 9
- ❌ Adding any wager, currency, shop, chance-based reward, casino control, gambling copy or age
  gate (`.claude/rules/no-gambling.md`)
- ❌ Calling `flutter build apk/appbundle/web`, `adb` or `emulator` — that is Session 3 / release-eng
- ❌ Reporting "done" while `dart analyze` has errors or `flutter test` is red
- ❌ Finishing without spawning Session 3 (Phase 10.7)

---

## The context protection strategy (why this is a separate session)

A complete game means a lot of code (5 agents × dozens of files + tests + the audit). If the
orchestrator read all of that itself, the context would run out before the end. So **the
Session 2 orchestrator mostly coordinates and runs commands, while the sub-agents do the file work**:

| Phase | What the orchestrator does | Who it delegates to (Agent tool, clean context + handoff) |
|-------|----------------------------|----------------------------------------------------------|
| 4.0. Approved concept intake | checks the approval, reads the gameplay sample, records the field contract in `lib/contracts.md` | **art-director**: campaign background + sample-alignment assets |
| 4. Implementation | builds the `lib/contracts.md` contract, runs the 5 agents strictly one at a time | **A** mechanics → **E** meta-systems → **D** sound → **B** ui → **C** juice |
| 4.5. Content wiring | — | gluing data↔code: **B** (level map/mode select) + **E** (progression/achievements/album) |
| 5. Integration | — | **lead-programmer**: reads every file, fixes cross-agent mismatches, places the service/audio/VFX calls |
| 6. Build & Fix | runs `dart analyze`, collects the error list | if there are many errors, **mechanics-programmer**/**ui-programmer** fix their own; the orchestrator only re-runs analyze |
| 6.5. Feel Pass | — | **juice-artist** (living gameplay, filling in the hooks) |
| 7. Tests | runs `flutter test`, collects the failures | **qa-tester** writes/fixes the tests |
| 8. UI Audit | — | `/ui-audit` (the skill already uses agents) OR **ui-programmer** across the 10 categories |
| 9. Balance | runs `tools/simulate_balance.py` (and, for mechanics without a built-in simulator, `test/balance/bot_sim_test.dart` → `--model report`) | **balance-designer** when it falls outside the window (edits the JSON) |
| 10. Crash Prevention | a final `dart analyze` + `flutter test` | targeted fixes go to the relevant agent |

> **The orchestrator's rule:** do not open `lib/` files en masse for reading. Read only the
> output of `dart analyze`/`flutter test`, `design/structure.md`, `lib/contracts.md`, and the
> BRIEF summaries the sub-agents return. A targeted Read of 1–2 files is acceptable for
> diagnosis. That keeps Session 2's context within budget even for a large game.

> **🤖 CODEX / an environment without the Agent tool:** the delegation in the table above is
> carried out as SEQUENTIAL persona passes (see `AGENTS.md` → "Execution Model"):
> before each pass read `.claude/agents/<role>.md` + `lib/contracts.md`, do that role's zone of
> responsibility, write a 3–5 line summary of the pass into
> `production/session-state/active.md`, and do NOT keep other roles' files in context.
> The Phase 4 order is: **A → E → D → B → C** (logic and services before UI, so B sees the real
> signatures). The "do not read lib/ en masse" rule matters even more under Codex — there is one
> context for everything.

> **The TPM gate:** at most one sub-agent is active at a time. Each receives only
> `lib/contracts.md`, the design/data files it needs, its role and a short handoff. Never pass
> it the parent session's full transcript.

---

## Phase 0 — preflight & handoff read [~30 s]

```bash
test -f production/session-state/autocreate-handoff-1.md || {
  echo "❌ No handoff-1. Did Session 1 /autocreate not finish?"; exit 1; }
test -f pubspec.yaml || { echo "❌ No pubspec.yaml — the project is not initialised"; exit 1; }
test -f design/structure.md || { echo "❌ No design/structure.md"; exit 1; }
# The user approves the concept carousel before any code is written (autocreate Phase 3.10).
python3 tools/concept_gate.py check --for implement || {
  echo "❌ The concept carousel is not approved — implementation waits for the user"; exit 1; }
ls assets/data/*.json   >/dev/null 2>&1 || echo "⚠️ no assets/data/*.json — the content data is missing"
ls assets/audio/sfx/*.wav >/dev/null 2>&1 || echo "⚠️ no audio — re-run tools/synth_sfx.py"

# Determining the asset format (PNG vs SVG). You may not silently fall back to SVG:
# Session 1 must write design/asset-format.md, and on a failure the format is inferred
# from the assets that actually exist.
ASSET_FORMAT=""
if [ -f design/asset-format.md ]; then
  ASSET_FORMAT=$(grep '^format:' design/asset-format.md | awk '{print $2}' | tr -d '[:space:]')
elif ls assets/images/sprites/*.png >/dev/null 2>&1 || ls assets/images/backgrounds/*.png >/dev/null 2>&1; then
  ASSET_FORMAT="png"
  echo "⚠️ design/asset-format.md is missing; inferred format=png from existing assets"
elif ls assets/images/sprites/*.svg >/dev/null 2>&1 || ls assets/images/backgrounds/*.svg >/dev/null 2>&1; then
  ASSET_FORMAT="svg"
  echo "⚠️ design/asset-format.md is missing; inferred format=svg from existing assets"
else
  echo "❌ No design/asset-format.md and no PNG/SVG assets found — Session 1 is incomplete"
  exit 1
fi
echo "🎨 Asset format: ${ASSET_FORMAT}"

# Validating the assets against the format
if [ "$ASSET_FORMAT" = "png" ]; then
  ls assets/images/sprites/*.png >/dev/null 2>&1 || echo "⚠️ no PNG sprites — they were expected in Codex mode"
  ls assets/images/backgrounds/*.png >/dev/null 2>&1 || echo "⚠️ no PNG backgrounds"
  if find assets/images -name "*.svg" -print -quit | grep -q .; then
    echo "⚠️ PNG mode, but SVGs were found. Do not use them in the code; check they are not the result of a mistaken generation."
  fi
else
  ls assets/images/sprites/*.svg >/dev/null 2>&1 || echo "⚠️ no SVG sprites"
  ls assets/images/backgrounds/*.svg >/dev/null 2>&1 || echo "⚠️ no SVG backgrounds"
fi
echo "✅ Preflight OK — Session 1's artifacts are in place"
```

Read `autocreate-handoff-1.md`, `production/store-art/concept/gameplay-sample.md` (and view
`gameplay-sample.png` and `panorama.png`), `design/structure.md`, `design/art-direction.md`,
`design/asset-format.md` (the asset format: PNG or SVG — it affects Agent B's code),
`design/gdd/game-concept.md` (especially the Production Plan, Screen Map, asset/world Design DNA,
Game UI Read, Design Signature, state composition map, per-screen recipes, Similarity Check, and
ValueNotifier contracts). Do not read `lib/` en masse.

> **CRITICAL for the asset format:** if `design/asset-format.md` says `format: png`:
> - Agent B uses `Image.asset('assets/images/sprites/name.png')`, NOT `SvgPicture`
> - `flame_svg` is NOT used in the code (it may stay in pubspec as a fallback)
> - The constants in `assets_constants` carry the `.png` extension
> - If `format: svg`, everything is as before: `SvgPicture.asset()` + `flame_svg`

### `--resume` (after a Session 2 failure)
Work out which phase to continue from, using the artifacts:
- no accepted campaign background in `production/store-art/campaign.md`, or sample-alignment items
  still open in `gameplay-sample.md` → start at Phase 4.0
- no `lib/main.dart` / few files in `lib/` → start at Phase 4
- the code exists but `dart analyze` has errors → Phase 6
- analyze is clean, there are no tests or they are red → Phase 7
- the tests are green, the audit has not run → Phase 8
Do not redo what is already done.

---

## Phase 4.0 — approved concept intake [~10 min]

The user approved the concept carousel; it is now the visual contract of the game. Before any
code, make sure the game has everything the carousel promised. Skip this phase only for a LEGACY
project (no concept record — `concept_gate.py check` said so).

1. **Read the contract.** `production/store-art/concept/gameplay-sample.md`, the crop
   `gameplay-sample.png` and the panorama. The sample's camera angle, the five flying balls, the
   lower-edge spill and the scenery are marketing-only; the field's topology, symbols, board
   housing, tile backing, the clearing moment's look and the field palette are the game's.
2. **Align the field's assets** (art-director). For every item the spec marks NEW — a board frame
   or housing, tile backing plates, a special-tile treatment the asset set lacks — decide whether it
   is code (spacing, a rounded plate in a flat colour, a glow ring: record it for Agent B/C) or an
   asset. Generate each asset square-on as an ordinary UI asset (`ui_board_frame`, `ui_tile`, …)
   from the existing sprites plus `gameplay-sample.png` as its visual reference, cut it out with
   `tools/cutout.py`, add it to `design/asset-manifest.md`, record it with
   `tools/art_lineage.py record --role asset --made fresh --ref <sprites> --ref
   production/store-art/concept/gameplay-sample.png`, and review it beside the sample (AR checks).
   Never crop, paste or trace pixels of the panorama into the game: the sample is a reference, not
   a source of sprites. Mark each item done in the spec's "Alignment for Session 2" list.
3. **Render the campaign background** in the approved panorama's world:
   [campaign-art.md](../store-screenshots/references/campaign-art.md) Steps 1–3 — the
   `background-*` template, the character asset, the approved panorama as world context, the
   game's original background, the phone-crop review, the `bg_campaign_menu.png` /
   `bg_campaign_game.png` export. No screen exists yet, so nothing is rewired: they are simply the
   game's backgrounds from the first line of UI code. Record `production/store-art/campaign.md`
   (background ACCEPTED, `world_panorama_sha256`).
4. **Write the field contract** into `lib/contracts.md` before Agent A starts: the topology and
   cell geometry, the board housing and tile assets (or the code treatment) with their paths, the
   symbols in the sample's order, the clearing-moment treatment for Agent C (colours, ring, lift,
   spill light), `bg_campaign_menu`/`bg_campaign_game` as the only backgrounds (menu, splash route,
   secondary screens and the wide-host phone-column surround on the first; the game screen on the
   second), and the rule: *the live field, seen square-on, reads as the approved gameplay sample.*

Exit: campaign background ACCEPTED and exported; every NEW sample item resolved to an asset or a
code note; `lib/contracts.md` carries the field contract. If image generation is unavailable,
record BLOCKED with the cause in `campaign.md`, continue implementation on the original
background, and report it — the release stays blocked until the background exists.

## Phases 4 → 10 — implementation protocol

Run **Phases 4, 4.5, 5, 6, 6.5, 7, 8, 9, 10** using the delegation map above,
the relevant `.claude/agents/` role brief, and the exit criteria below. Before implementation,
record concrete integration and crash-prevention checks in the session state from the game's
contracts and repository rules; attach verification evidence as each check passes. The table
below is the Session 2 quality-gate definition:

| Phase | Exit criterion | Iterations |
|-------|----------------|------------|
| 4.0. Approved concept intake | approval verified; campaign background ACCEPTED; sample-alignment items resolved; field contract in `lib/contracts.md` | correction loop per art-lineage.md |
| 4. Implementation | the 5 agents have finished (A/B/C/D/E); the field follows the contract | 1 (Phase 6 fixes) |
| 4.5. Content wiring | Game accepts (mode,levelId); Level/Mode Select ↔ data | 2 |
| 5. Integration | 18 connections (including the meta services) | 3 |
| 6. Build | `dart analyze lib/` 0 errors | 10 |
| 6.5. Feel Pass | the field is alive (F1–F5), analyze + test clean | 2 |
| 7. Tests | `flutter test` all green (including test/services/) | 5 |
| 8. UI Audit | 100+ checks, including the blocking portrait-phone gate at the four phones (no desktop/tablet/landscape layout) and the field against `gameplay-sample.png` | 3 |
| 9. Balance | the B1–B6 model PASSES across the WHOLE curve (`design/balance/simulation-report.md`) | 3 |
| 10. Crash Prevention | 20/20 + no dead ends + the no-gambling greps clean; analyze + test clean | 3 |

**THE ABSOLUTE MINIMUM before Phase 10.7:** `dart analyze lib/` 0 errors, `flutter test` green,
15+ screens, working navigation, the core mechanic + content (N levels/modes) + the meta systems
in place, the no-gambling gate clean (no wager, currency, chance-based reward, casino control,
gambling copy or age gate), and every player-facing string in English (unless the user explicitly
asked for another language). The live field, essential HUD (score, goal, moves/time) and primary
action must be visible together without page scrolling; a thumbnail field or
nested game window blocks the handoff even when analyzer and tests are green. The live field reads
as the approved gameplay sample (topology, symbols, housing, tile backing, palette) and every
screen runs on the campaign background. Every screen is one
portrait composition that holds at 360×640, 360×800, 390×844 and 430×932; the app is
portrait-locked, touch-only, and shows the phone column on a wide host.

---

## Phase 10.7 — handoff & spawn Session 3 [~1 min]

Write `production/session-state/autocreate-handoff.md` with the game/package identity,
current architecture and entrypoints, modes/content paths, completed phase evidence, analyzer
and test results, integration/feel/UI/no-gambling/curve/crash reports, viewport measurements,
asset format and known limits, the approved concept revision and its gameplay sample, the
campaign background and where each screen selects it, and the sample-alignment assets. Include
exact runtime launch and navigation details.

**Spawn a clean-context Session 3 agent** with the following instruction:

```text
You are Session 3 of /autocreate. First read
production/session-state/autocreate-handoff.md, then
.claude/skills/autocreate-finalize/SKILL.md. Execute its campaign check (the campaign background
from the approved panorama is wired into every screen), runtime and soak verification including
V22 (campaign background) and V23 (the live field against the approved gameplay sample), playtest,
session state, release-engineering PREP, the final report and the store-kit handoff. Preserve the
approved concept, the existing concept, character/symbol assets, reference contract and verified
balance. Do not build an AAB/APK, create an upload keystore or call release-package; those require
a separate explicit request. Return the actual checks, evidence paths and any unresolved blockers.
```

Once the Session 3 sub-agent returns, pass its final report upward (to the user).
If Session 3 failed, report the reason and the manual restart command: `/autocreate-finalize`.

---

## Recovery after a failure

- **Session 2 crashed** → the user runs `/autocreate-implement --resume` in a new conversation;
  the skill works out the phase from the artifacts and continues.
- **The concept is not approved** → preflight stops. The user approves the carousel (the web
  service's Approve button, or `python3 tools/concept_gate.py approve --by user`), or asks for
  changes with `/autocreate --revise "<feedback>"`.
- **Session 1 never wrote handoff-1** → preflight fails with a clear message; run `/autocreate`
  again (or write `assets/data/*.json` and handoff-1 by hand).
