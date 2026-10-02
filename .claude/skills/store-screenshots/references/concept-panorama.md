# Concept panorama — the carousel the user approves before any code

`/autocreate` does not rush from assets into implementation. Once the concept, the asset set, the
audio and the level data exist, it renders the store panorama — the same picture
`/store-screenshots` exports, under the same rules, sliced into the same three carousel panels —
shows it to the user, and **stops**. Only the user's approval unlocks implementation, and the
approved picture then governs everything after it:

- **the game** — the field is built to look like the panorama's gameplay sample (topology,
  symbols, board housing, tile backing, the clearing moment, palette); finalization checks it
  side by side (V23);
- **the game background** — rendered in the panorama's world right after approval
  ([campaign-art.md](campaign-art.md)) and wired into every screen;
- **the store kit** — `/store-screenshots` exports this panorama unchanged (crops, grading and the
  detail pass only) and renders the banner, icon and emblem in its world.

The approval is a contract, so this procedure is strict about one thing above all: the panorama
the user sees is the panorama everything is built from. `tools/concept_gate.py` pins the approval
to its SHA-256, and the store kit's archive gate refuses a panorama that does not descend from it.

## Callers

| Caller | When | Gameplay reference |
|---|---|---|
| `/autocreate` Phase 3.9 | every new game, after Phase 3.8 | the layout draft (no game exists yet) |
| `/autocreate --revise "<feedback>"` | the user asked for changes instead of approving | the layout draft |
| `/store-screenshots` preflight | only a game made before this gate (`concept_gate.py status` → NONE, legacy) | a real gameplay capture |

The legacy store caller runs Steps 1–5 into `$ART_DIR/panorama.png` and returns to the store
runbook: there is no carousel to present and nothing to approve, because the store run itself is
the user's request.

## Files — `production/store-art/concept/`

| File | What it is |
|---|---|
| `panorama.png` | the accepted panorama source (`3456x2384` headless; ~1.6 MP from the built-in tool) |
| `panorama-prompt.txt` | the rendered `panorama-*` prompt; `prompt_template.py check` PASS |
| `layout-draft.png` | the context-only sketch of the planned field |
| `panels/` | the triptych export: `store-01..03.png` at 1320×2868, `_panorama-preview.png`, `_carousel-preview.png` |
| `export-flags.txt` | the exact `triptych` flags the carousel was exported with — the store run reuses them |
| `gameplay-sample.png` | the crop of the panorama's gameplay: the field the game is built to look like |
| `gameplay-sample.md` | the written spec of that sample |
| `preview/` | the small web previews `concept_gate.py publish` writes for the chat |
| `concept.json` | the approval record (`tools/concept_gate.py`) |
| `revisions/rN/` | earlier revisions the user asked to change |

Everything here persists in project snapshots, beside `production/store-art/lineage.json`.

## Step 1 — inputs

Select `STORE_PYTHON` exactly as `/store-screenshots` Phase 0 does. Then collect, from
`design/gdd/game-concept.md`, `design/art-direction.md` and `design/asset-manifest.md`:

- `lead_kind` and the lead's shipped asset; for a character lead, the **original** character file
  — never a crop, preview or generated scene. Object/mechanic games never gain a character.
- The multiplier reference: one shipped round asset (ball, gem, orb, bubble, token) listed in the
  asset manifest. Phase 3's asset plan includes one for exactly this reason; if it is missing,
  generate it as an ordinary game asset first — never an invented one-off orb.
- The visible gameplay assets: every symbol on the field, the board frame/housing and tile backing
  when the asset set has them, the game's background, and every source in
  `design/reference-contract.md` for a reference game (its panorama is that reference's world).
- The planned field: topology from the concept and `assets/data/` (an unspecified match game is
  7×8; reference families keep their "Build as" topology), and the **moment** the field is caught
  in — mid-clear, mid-merge, mid-shot, never a board at rest (store rule: the gameplay panel is
  caught at the instant it pays).

Build the layout draft for a grid mechanic (match, tile, sort, merge grid, block place, logic
grid) from the real symbol files:

```bash
python3 tools/store_compose.py layout-draft \
  --symbol assets/images/sprites/sprite_a.png --symbol assets/images/sprites/sprite_b.png ... \
  --grid 7x8 --frame assets/images/ui/ui_board_frame.png \
  --win 2x4,3x4,4x4 --out production/store-art/concept/layout-draft.png
# no board asset yet: --panel "#..." --tile "#..." --border "#..." from the art direction
```

A mechanic without a grid (physics, reflex, drop merge) has no draft: describe its field in the
`gameplay` value and attach the field's own sprites (pegs, bricks, targets, the player piece). The
draft is **context only** — it tells the model the topology and the moment, and it is never
pasted, warped or composited into the panorama.

## Step 2 — the prompt

Render `panorama-character` (character lead) or `panorama-object` (object or mechanic lead) from
[campaign-prompts.md](campaign-prompts.md) with `panels=three`, and prove it:

```bash
TPL=.claude/skills/store-screenshots/references/campaign-prompts.md
python3 tools/prompt_template.py render --template "$TPL" --id panorama-character \
  --set panels="three" --set environment="..." --set character="..." --set gameplay="..." \
  --set label_color="..." --set accent="..." --set ball_fx="..." --set objects="..." \
  --set foreground_pieces="..." --set palette="..." \
  --out production/store-art/concept/panorama-prompt.txt
python3 tools/prompt_template.py check --template "$TPL" --id panorama-character \
  --prompt production/store-art/concept/panorama-prompt.txt || exit 1
```

The values name this game's subjects in plain words (see the template file's placeholder rules);
`gameplay` states the topology, the symbols, the moment and where the field sits ("spanning the
middle and right panels"). Never write or paraphrase the prompt yourself.

## Step 3 — generate and record

Use the built-in image tool, or headless `tools/gpt_image.py edit` with the prompt file and the
attachments in the order the template table lists — identity asset first, then the multiplier
reference, the layout draft, the symbols/board/tile assets, the original background, the
reference sources:

```bash
python3 tools/gpt_image.py edit --prompt-file production/store-art/concept/panorama-prompt.txt \
  --image "$CHARACTER_ASSET" --image "$MULTIPLIER_REF" \
  --image production/store-art/concept/layout-draft.png --image "$SYMBOL_1" ... \
  --size 3456x2384 --fidelity high --out production/store-art/concept/panorama.png
python3 tools/art_lineage.py record --file production/store-art/concept/panorama.png \
  --role panorama --made fresh --ref "$CHARACTER_ASSET" --ref "$MULTIPLIER_REF" \
  --ref production/store-art/concept/layout-draft.png --ref "$SYMBOL_1" ... \
  --prompt production/store-art/concept/panorama-prompt.txt
```

## Step 4 — review and correct

Review the panorama and its exported panels (Step 5) against `/store-screenshots` → Phase 2 —
balls, labels, character framing, lower edge, lighting, the world — and against the concept's own
promises. Objective failures in addition to the store's list:

- the field is not the planned one: wrong topology, a symbol that is not in the asset set, a
  board redrawn as reels or as a generic neon grid, housing or tiles that come from nowhere in the
  game's assets or art direction;
- the gameplay is too small, too dark or too covered to read as a game a player would recognise —
  balls may cover part of it, the field as a whole must stay readable;
- a reference game's world, character or symbol cast drifts from its sources.

Correct with `/store-screenshots` → "Correcting a generated scene": crop first, local defects as
region repairs (`tools/region_repair.py`), composition defects as a fresh render from the original
references, at most one whole-frame edit of a fresh render. Every candidate goes into the lineage
ledger. Keep correcting until it passes — an attempt count is never a blocker.

## Step 5 — export the carousel exactly like the store kit

The store run will export this same picture with the same command, so the user approves exactly
what the App Store will show:

```bash
"$STORE_PYTHON" tools/store_compose.py triptych --src production/store-art/concept/panorama.png \
  --out production/store-art/concept/panels --panels 3 --size 1320x2868 --pop soft \
  --seam-snap off --lead-kind character --art-gate off
printf '%s\n' "--panels 3 --pop soft --seam-snap off --lead-kind character --art-gate off" \
  > production/store-art/concept/export-flags.txt
```

Use the game's `--lead-kind`. A head or label clipped by a seam is fixed in the export
(`--zoom` with `--offset`), and the flags that fixed it go into `export-flags.txt`. Review the
three panels at final crop size and `_carousel-preview.png` once. With the built-in tool's ~1.6 MP
source the compositor warns about the enlargement: that is expected here — the user judges the
composition from the previews, and the store run's detail pass gives the exports their resolution
without changing the picture.

## Step 6 — the gameplay sample

The panorama's gameplay is now the visual specification of the game's field. Crop it and write it
down so Session 2 builds to it and finalization can compare against it:

```bash
"$STORE_PYTHON" - <<'PY'
from PIL import Image
box = (X0, Y0, X1, Y1)  # the whole field with its housing, in panorama pixels
Image.open("production/store-art/concept/panorama.png").crop(box).save(
    "production/store-art/concept/gameplay-sample.png")
PY
python3 tools/art_lineage.py record --file production/store-art/concept/gameplay-sample.png \
  --role panorama --made derive --parent production/store-art/concept/panorama.png \
  --note "gameplay sample crop"
```

`gameplay-sample.md`:

```markdown
# Gameplay sample — the field the game is built to look like
- Source: production/store-art/concept/panorama.png (revision N), box X0,Y0,X1,Y1
- Mechanic and topology: [e.g. swap match-3, 7×8]
- Symbols on the field: [asset ids from design/asset-manifest.md, in the order they appear]
- Board housing / frame: [material, colour, ornament, thickness — asset id, or NEW: not in the asset set]
- Cell and tile backing: [shape, colour, spacing — asset id, code-drawn, or NEW]
- The moment shown: [what clears/merges/fires, and its look: glow colour, ring, lifted symbol]
- Field palette and light: [...]
- Marketing-only, NOT in the game: the five flying x5–x100 balls, the three-quarter camera, the
  lower-edge spill, the character/lead framing, the scenery around the field
- Alignment for Session 2: [every NEW element above and how it reaches the game: generated from
  this crop in implement Phase 4.0, or drawn in code]
```

The runtime field is the same board seen square-on, as the game requires: the camera angle and
the marketing-only items are the panorama's; everything else in this file is the game's.

## Step 7 — publish and stop

```bash
python3 tools/concept_gate.py publish \
  --panorama production/store-art/concept/panorama.png \
  --prompt production/store-art/concept/panorama-prompt.txt \
  --panels production/store-art/concept/panels \
  --sample production/store-art/concept/gameplay-sample.png \
  --sample-spec production/store-art/concept/gameplay-sample.md \
  --lead-kind character
```

Publish once, after the review passes: a different panorama replacing a PENDING one is refused
unless it went through `concept_gate.py revise`. Then present the carousel in the final report —
the three panels in order with what each shows, the gameplay sample in one sentence, the revision
number — and **end the session**. Do not write gameplay code, do not start
`/autocreate-implement`.

Approval:

- **Web service** — the chat shows the three slides and the panorama with an Approve button. The
  service records the approval (`concept_gate.py approve --by service --expect-sha …`) and starts
  `/autocreate-implement`; a typed message instead is revision feedback.
- **Standalone** — when the user approves, run `python3 tools/concept_gate.py approve --by user`,
  then `/autocreate-implement`.

## Revisions — `/autocreate --revise "<feedback>"`

1. Read `concept_gate.py status` and the feedback. If the feedback only approves ("looks good",
   "go") and asks for nothing, change nothing: say the carousel is waiting for the Approve button
   (or the approve command) and end.
2. Save the feedback to `production/session-state/concept-feedback.md` and archive the shown
   revision: `python3 tools/concept_gate.py revise --feedback-file production/session-state/concept-feedback.md`.
3. Feedback about the game itself — theme, character, symbols, palette, mechanic — goes through
   the Session 1 phase that owns it: update the concept and art direction, regenerate only the
   affected assets fresh from their original references (re-run their AR checks), and update the
   level/balance data and its simulation when topology or rules change.
4. Re-run Steps 1–7. A change that moves the composition is a fresh render with the change written
   into the template values. A purely local change ("the x100 ball in red", "a happier face") may
   be a region repair of the archived picture: cut from `revisions/rN/panorama.png`, merge into a
   new `panorama.png`, record it `--made repair --parent revisions/rN/panorama.png`. Never attach
   the archived panorama to a fresh render.
5. Report what changed against the feedback, publish the new revision and end again.

An approved concept is never revised: the game, its background and the store kit are built from
it. Changing the look after approval is a normal follow-up request against the built game.
