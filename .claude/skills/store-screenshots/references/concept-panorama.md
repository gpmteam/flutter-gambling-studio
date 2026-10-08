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

Its own review, on the other hand, is **bounded**, because the user reviews the picture the moment
it is published. Each revision has three fresh renders and five region repairs
(`concept_gate.py budget`); crops and re-exports are free. Unbounded, one panorama took ten fresh
renders and 42 minutes: the grid count and the cut placement were re-rolled together every time,
because nothing told the image model where the cuts fall. The composition guide (Step 1) tells it.

## Callers

| Caller | When | Gameplay reference |
|---|---|---|
| `/autocreate` Phase 3.9 | every new game, after Phase 3.8 | the layout draft (no game exists yet) |
| `/autocreate --revise "<feedback>"` | the user asked for changes instead of approving | the layout draft |
| `/store-screenshots` preflight | only a game made before this gate (`concept_gate.py status` → NONE, legacy) | a real gameplay capture |

The legacy store caller runs Steps 1–5 into `$ART_DIR/panorama.png` and returns to the store
runbook: there is no carousel to present and nothing to approve, because the store run itself is
the user's request. It draws the composition guide from its capture (`--field`) like any caller,
but the render budget is the concept callers' — with no user review to come, its panorama follows
the store's correction policy.

## Files — `production/store-art/concept/`

| File | What it is |
|---|---|
| `panorama.png` | the accepted panorama source (`3456x2384` headless; ~1.6 MP from the built-in tool) |
| `panorama-prompt.txt` | the rendered `panorama-*` prompt; `prompt_template.py check` PASS |
| `layout-draft.png` | the context-only sketch of the planned field |
| `composition-guide.png` | the context-only placement sketch: the panel cuts, the lead, the field, the five balls, the lower band |
| `panels/` | the triptych export: `store-01..03.png` at the Google Play size 1080×1920, `_panorama-preview.png`, `_carousel-preview.png` |
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

Choose the clearing cells (`--win`) in the left half of the board: the field spans the cut
between its two panels, and the composition guide seats it so that cut crosses its right-hand
columns. A mechanic without a grid (physics, reflex, drop merge) has no draft: describe its field
in the `gameplay` value and attach the field's own sprites (pegs, bricks, targets, the player
piece). The draft is **context only** — it tells the model the topology and the moment, and it is
never pasted, warped or composited into the panorama.

Then draw the **composition guide** — where the export will cut the picture, and where everything
goes — for the size the image tool returns (`--canvas 1536x1024` for the built-in tool, which is
asked for that landscape size; the default `3456x2384` headless) and for the carousel's panels,
the Google Play size (`--size play`, 1080×1920):

```bash
"$STORE_PYTHON" tools/store_compose.py composition-guide --size play --canvas 1536x1024 \
  --offset-y 1 \
  --lead-kind character --lead "$CHARACTER_ASSET" --ball "$MULTIPLIER_REF" \
  --field production/store-art/concept/layout-draft.png \
  --object "$SYMBOL_1" --object "$SYMBOL_2" ... \
  --out production/store-art/concept/composition-guide.png
```

Red bands are the cuts (the hidden allowance plus a safety margin), darkened edges are what the
cover crop trims — on a 3:2 render, a band along the top, because Play's 9:16
panels take the picture's whole width and the crop is anchored to the bottom. The real assets sit where
the panorama needs them: the torso-to-head bust on
panel 1 (or the lead object on the last panel; a mechanic lead is the field itself), the field
across the remaining panels, one ball per panel, two over the board, the lower-edge objects. Look
at it once: a clearing cell under a red band means moving `--win` left, or the field with
`--field-x`. It is context only, like the draft — attached, never composited into any art.

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
middle and right panels"). Placement — which panel, how far from a cut, how large — is in the
guide, not in a value: a value carrying it hits the 500-character limit, as four renders of one
run did. Never write or paraphrase the prompt yourself.

## Step 3 — generate and record

Use the built-in image tool — asking for the landscape `1536x1024` size the guide was drawn for —
or headless `tools/gpt_image.py edit` with the prompt file and the attachments in the order the
template table lists: identity asset first, then the multiplier reference, the composition guide,
the layout draft, the symbols/board/tile assets, the original background, the reference sources:

```bash
python3 tools/gpt_image.py edit --prompt-file production/store-art/concept/panorama-prompt.txt \
  --image "$CHARACTER_ASSET" --image "$MULTIPLIER_REF" \
  --image production/store-art/concept/composition-guide.png \
  --image production/store-art/concept/layout-draft.png --image "$SYMBOL_1" ... \
  --size 3456x2384 --fidelity high --out production/store-art/concept/panorama-candidate-1.png
python3 tools/art_lineage.py record --file production/store-art/concept/panorama-candidate-1.png \
  --role panorama --made fresh --ref "$CHARACTER_ASSET" --ref "$MULTIPLIER_REF" \
  --ref production/store-art/concept/composition-guide.png \
  --ref production/store-art/concept/layout-draft.png --ref "$SYMBOL_1" ... \
  --prompt production/store-art/concept/panorama-prompt.txt
```

The record is also the budget: a fresh render beyond the revision's three is refused, and an
unrecorded picture cannot be published.

## Step 4 — review and correct, within the budget

First see where the cuts fall on the candidate itself — the tool may return another aspect than
the guide's (16:9 instead of 3:2 fills the Play panels' height, so the cuts move outward and
nothing is trimmed top or bottom), and the overlay is drawn for the candidate's real size:

```bash
"$STORE_PYTHON" tools/store_compose.py composition-guide --size play --offset-y 1 \
  --over production/store-art/concept/panorama-candidate-1.png \
  --out production/store-art/concept/panorama-candidate-1-cuts.png
```

Then review the panorama and its exported panels (Step 5) against `/store-screenshots` → Phase 2 —
balls, labels, character framing, lower edge, lighting, the world — and against the concept's own
promises:

- the field reads as a different game: reels or a generic neon grid instead of the planned board,
  a different mechanic or topology, housing or tiles from nowhere in the game's assets or art
  direction, no clearing moment;
- the gameplay is too small, too dark or too covered to read as a game a player would recognise —
  balls may cover part of it, the field as a whole must stay readable;
- a reference game's world, character or symbol cast drifts from its sources;
- the backdrop is a literal place — a street, city, castle, palace, temple, landscape or
  interior — instead of abstract slot style, unless the user asked for a setting or an exact
  reference's own background is one (`.claude/docs/visual-context.md` → "Backgrounds — abstract slot style").

**A field off by one row or one column is a note, not a defect.** The game takes its topology from
the level data, not from the picture: write the painted count into `gameplay-sample.md`
(`Painted:` line) and publish it as a known issue. It never justifies a fresh render. A symbol
that is not in the asset set is a cell repair, not a re-render. Symbol order is not compared with
the draft — there is no captured state to preserve before the game exists.

Correct each defect with the cheapest fix that can work, in this order, and check
`python3 tools/concept_gate.py budget` before spending a render:

1. **Crop** — something in a red band or a trimmed edge: `--zoom` with `--offset` on the export,
   or adjust `--offset-y` if a head enters the top trim (-1 keeps the top, +1 the bottom).
   Keep the lower-edge objects visible when choosing the bias, and record it in
   `export-flags.txt`. The same flags on `composition-guide --over` show where the cuts and the
   grey move. Free, and no new picture.
2. **Region repair** — a misspelled or missing label, a hand or prop on a cut, a wrong cell, a ball
   to add or move (`/store-screenshots` → "Correcting a generated scene"). Five per revision.
3. **Fresh render** — a composition defect only: the field reads as a different game, the
   character's identity drifted, the bust is in the wrong panel. Write what the review accepted and
   what must change into the template values (and redraw the guide if placement is the problem).
   Three per revision, the first render included.

At most one whole-frame edit of a fresh render, as everywhere. Every candidate goes into the
lineage ledger. When the budget is spent, stop correcting: choose the best candidate — identity
and a readable field first, then the labels, then the framing — and publish it in Step 7 with a
`--known-issue` sentence for each thing still off. The user sees the picture next and can ask for
a revision; another render here only delays that.

The accepted candidate is copied byte for byte to `production/store-art/concept/panorama.png`; the
ledger knows a picture by its content, so the copy keeps its record.

## Step 5 — export the carousel exactly like the store kit

The carousel is the Google Play set. The store run exports this same picture with the same command
for its `store-play/` panels, so the user approves exactly what Google Play will show:

```bash
"$STORE_PYTHON" tools/store_compose.py triptych --src production/store-art/concept/panorama.png \
  --out production/store-art/concept/panels --panels 3 --size play --pop soft \
  --seam-snap off --offset-y 1 --lead-kind character --art-gate off
printf '%s\n' "--panels 3 --pop soft --seam-snap off --offset-y 1 --lead-kind character --art-gate off" \
  > production/store-art/concept/export-flags.txt
```

Use the game's `--lead-kind`. The bottom anchored Play crop keeps the panorama's foreground
objects in all three panels; the guide and export must use the same `--offset-y`. Review the top
edge as well, especially the highest ball and the character's head. If either is clipped, adjust
the bias and save the chosen value in `export-flags.txt` only after all three panels pass review.
A head or label clipped by a seam is fixed in the export
(`--zoom` with `--offset`, `--offset-y` for the top or bottom edge), and the flags that fixed it
go into `export-flags.txt`. The size never goes into that file: the store run passes it, once for
each set. On a 3:2 render its App Store panels (1320×2868) cut the picture within a percent of its
width of the Play cuts and add back the strip above that the Play crop trims — which is
why the panorama is still rendered 3:2: one picture serves both sets. Review the three panels at final crop size and `_carousel-preview.png` once. With the
built-in tool's ~1.6 MP source the compositor warns about the enlargement: that is expected here —
the user judges the composition from the previews, and the store run's detail pass gives the
exports their resolution without changing the picture.

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
- Mechanic and topology: [e.g. swap match-3, 7×8 — from assets/data, the game's own]
- Painted: [the count the panorama shows, when it differs by a row or column — e.g. 6×8; the game
  keeps the data's 7×8]
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
  --lead-kind character \
  --known-issue "The painted board is 6×8; the game keeps the level data's 7×8."  # one per issue
```

Publish once, after the review passes: a different panorama replacing a PENDING one is refused
unless it went through `concept_gate.py revise`. A known issue is one plain sentence for the user
(at most eight), shown on the chat card beside the Approve button. Then present the carousel in the
final report — the three panels in order with what each shows, the gameplay sample in one
sentence, the revision number, the known issues — and **end the session**. Do not write gameplay code, do not start
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
4. Re-run Steps 1–7 with a fresh budget (`revise` starts the revision's count). A change that
   moves the composition is a fresh render with the change written into the template values. A purely local change ("the x100 ball in red", "a happier face") may
   be a region repair of the archived picture: cut from `revisions/rN/panorama.png`, merge into a
   new `panorama.png`, record it `--made repair --parent revisions/rN/panorama.png`. Never attach
   the archived panorama to a fresh render.
5. Report what changed against the feedback, publish the new revision and end again.

An approved concept is never revised: the game, its background and the store kit are built from
it. Changing the look after approval is a normal follow-up request against the built game.
