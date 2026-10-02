# Campaign art — the banner and the game background

One procedure, two callers:

- `/autocreate-finalize` Phase 10.4 runs it for every new game, before runtime verification.
- `/store-screenshots` runs it in preflight when [the campaign handoff](campaign-handoff.md) is
  missing or stale — a game built before finalization made campaign art.

It produces two pictures from one world. The **banner** is the store's key art: the lead large on
the left, the real gameplay, the five flying `x5`–`x100` balls. The **game background** is the
same world composed for a phone held upright, with the main character whole inside the frame. It
becomes the background of the game itself and the background behind every phone on the store's
real-capture slides — one picture, so the listing and the app cannot disagree.

Everything persists in `production/store-art/`, outside timestamped store exports:

| File | What it is |
|---|---|
| `long-banner.png` | accepted device-free banner, `3840x1872` source |
| `banner-prompt.txt` | the rendered banner prompt; `prompt_template.py check` PASS |
| `shared-background.png` | accepted game background, `1328x2880` source |
| `background-prompt.txt` | the rendered background prompt; `check` PASS |
| `background-crops.png` | the background at the four phone sizes, as wired |
| `context-capture.png` | the real gameplay frame used as context |
| `campaign.md` | the handoff record ([campaign-handoff.md](campaign-handoff.md)) |

The game uses `assets/images/backgrounds/bg_campaign_menu.png` and `bg_campaign_game.png`,
both exported from `shared-background.png`.

**Both pictures stay near their first generation** ([art-lineage.md](../../../docs/art-lineage.md)):
every remake is a fresh render from the original references, never from the previous banner or
background; at most one whole-frame edit of a fresh render; everything else is a region repair.
`production/store-art/lineage.json` records each picture (`tools/art_lineage.py`), and it
persists into every later run with the rest of `production/store-art/`.

## Step 1 — inputs

Select `STORE_PYTHON` exactly as `/store-screenshots` Phase 0 does, then collect:

- `lead_kind`, the lead's shipped asset (`Lead asset:` in the concept or art direction) and, for a
  character lead, the **original** character file — never a crop, preview or generated scene.
- The multiplier reference: one shipped round asset (ball, coin, token, orb) confirmed in the
  asset registry or `pubspec.yaml`. No such asset → report the missing source; do not invent one.
- The visible gameplay sprites, the game's **original** background — the one campaign art
  replaces, recorded in `campaign.md` once it has been replaced; never `bg_campaign_*` or
  `shared-background.png` — and, when `design/reference-contract.md` exists, every source it lists. A reference game's campaign art
  is that reference's world: its sources ride along on every call below.
- A real, current gameplay frame. Serve the web build and capture at the canonical phone size:

```bash
mkdir -p production/store-art .claude/runtime-logs
nohup flutter run -d web-server --web-port 8098 --web-hostname 127.0.0.1 \
  > .claude/runtime-logs/campaign-run.log 2>&1 &
echo $! > .claude/runtime-logs/campaign.pid
# wait for http://127.0.0.1:<port> in the log exactly as autocreate-finalize 10.5.2 does, then:
timeout 180 node tools/web_verify.mjs --url "$WEB_URL" --out production/store-art/context \
  --size 390x844 --budget 150 --quick
kill "$(cat .claude/runtime-logs/campaign.pid)" 2>/dev/null || true
```

Pick the active or resolving gameplay frame (not the menu) and copy it to
`production/store-art/context-capture.png`. Record its topology and outcome. It is context only:
it is attached so the model draws the real mechanic, and it never becomes a layer of the art.

## Step 2 — the banner

**Reuse first.** If `campaign.md` records the banner ACCEPTED, and the character asset,
multiplier reference and topology hashes still match, keep it. A changed template alone does not
remake it: when its prompt no longer passes `check`, review the accepted banner once against the
current template's requirements and keep it unless it breaks one, recording the template's
SHA-256 and the verdict in `campaign.md`. A remake is a **fresh** render from the original
references: never an edit of the old banner, and the old banner is not attached. A banner with
no lineage record is adopted (`tools/art_lineage.py record --made adopt`) only when its review
finds no generation artifacts; otherwise it is remade fresh.

Render and check the prompt. Use `banner-character` for a character lead and `banner-object` for
an object or mechanic lead (see [campaign-prompts.md](campaign-prompts.md)):

```bash
TPL=.claude/skills/store-screenshots/references/campaign-prompts.md
python3 tools/prompt_template.py render --template "$TPL" --id banner-character \
  --set environment="..." --set character="..." --set gameplay="..." --set label_color="..." \
  --set accent="..." --set ball_fx="..." --set objects="..." --set foreground_pieces="..." \
  --set palette="..." --out production/store-art/banner-prompt.txt
python3 tools/prompt_template.py check --template "$TPL" --id banner-character \
  --prompt production/store-art/banner-prompt.txt || exit 1
```

Generate with the built-in image tool, or headless with the same prompt file and attachments in
the order the template table lists:

```bash
python3 tools/gpt_image.py edit --prompt-file production/store-art/banner-prompt.txt \
  --image "$CHARACTER_ASSET" --image "$MULTIPLIER_REF" \
  --image production/store-art/context-capture.png --image "$SPRITE_1" ... \
  --size 3840x1872 --fidelity high --out production/store-art/long-banner.png
python3 tools/art_lineage.py record --file production/store-art/long-banner.png --role banner \
  --made fresh --ref "$CHARACTER_ASSET" --ref "$MULTIPLIER_REF" \
  --ref production/store-art/context-capture.png --ref "$SPRITE_1" ... \
  --prompt production/store-art/banner-prompt.txt
```

Review it once at full size and once at 1024×500. Each of these is an objective failure: a
misspelled, missing, duplicated or extra ball label; a missing ball or a ball resting on an object;
a ball on the character; character drift from its asset; a character shown full length, standing,
flying or floating, or with legs, knees, hips or feet visible; any title, logo, copy or blank copy
space; a pasted-screenshot boundary; a world that is not the game's (or not the reference's).

Correction follows `/store-screenshots` → "Correcting a generated scene": crop, region repairs
(`tools/region_repair.py`) or fresh compositions until the banner passes — never a whole-frame
edit of a banner that is already an edit, which only stacks generation loss. A new pose that
fits the character's area is a region repair of that area (the character and its held props); one
that needs different space is a fresh render. Record every candidate with
`tools/art_lineage.py`; it refuses a second whole-frame edit. Use the original identity
references, authentic capture and exact runtime facts for board corrections. Verify identity,
composition, balls and gameplay after changes. No local board compositing. Failed review or
attempt count alone does not make the campaign BLOCKED.

## Step 3 — the game background

Render `background-character`, `background-object` or `background-mechanic`, `check` it, and
generate at `1328x2880` with, in order: the original character asset (or the lead object asset;
none for a mechanic lead), the accepted `long-banner.png` as world context, the game's original
background, and the reference sources. The banner is never the character reference, and no earlier
campaign background is attached: a background rendered from the previous one inherits its
artifacts.

```bash
python3 tools/prompt_template.py render --template "$TPL" --id background-character \
  --set environment="..." --set character="..." --set foreground_pieces="..." --set objects="..." \
  --set palette="..." --out production/store-art/background-prompt.txt
python3 tools/prompt_template.py check --template "$TPL" --id background-character \
  --prompt production/store-art/background-prompt.txt || exit 1
python3 tools/gpt_image.py edit --prompt-file production/store-art/background-prompt.txt \
  --image "$CHARACTER_ASSET" --image production/store-art/long-banner.png \
  --image "$ORIGINAL_GAME_BACKGROUND" ... \
  --size 1328x2880 --fidelity high --out production/store-art/shared-background.png
python3 tools/art_lineage.py record --file production/store-art/shared-background.png \
  --role background --made fresh --ref "$CHARACTER_ASSET" \
  --ref production/store-art/long-banner.png --ref "$ORIGINAL_GAME_BACKGROUND" ... \
  --prompt production/store-art/background-prompt.txt
```

Build the phone-crop sheet the review uses — the picture as each phone in the matrix will show it
with the wiring below (`BoxFit.cover`, `Alignment.topCenter`):

```bash
"$STORE_PYTHON" - <<'PY'
from PIL import Image
src = Image.open("production/store-art/shared-background.png").convert("RGB")
tiles = []
for w, h in ((360, 640), (360, 800), (390, 844), (430, 932)):
    scale = max(w / src.width, h / src.height)
    img = src.resize((round(src.width * scale), round(src.height * scale)))
    left = (img.width - w) // 2
    tiles.append(img.crop((left, 0, left + w, h)))  # top-aligned, as wired
sheet = Image.new("RGB", (sum(t.width for t in tiles) + 24 * 5, 932 + 48), "#202020")
x = 24
for t in tiles:
    sheet.paste(t, (x, 24)); x += t.width + 24
sheet.save("production/store-art/background-crops.png")
PY
```

Review `shared-background.png` and `background-crops.png` once. Objective failures:

- **the character does not fit**: any part of the head, hair, headwear, face, shoulders, hands or
  a held object is cut by an edge — in the source or in any of the four phone crops;
- legs, knees, hips or feet visible, or a standing, flying or floating character;
- character drift from its asset (face, silhouette, costume, colours);
- any text, letters, numbers or logo; any multiplier ball or labelled coin;
- a painted board, reels, grid, cards, table, buttons, HUD, frame, phone or device;
- a different world from the accepted banner (environment, palette, light, materials);
- for an object/mechanic game, an invented person, hand, animal or mascot.

For a failed background, follow the same correction loop until all four phone crops pass. Use
region repairs for local defects (a hand, a held prop, a pose that fits the character's area) or a
fresh composition with the original references and accepted banner; never re-edit a background
that is already an edit, and never chain "compact", "repair" and "final" edits of one
another. Refine the template variables or append concrete crop/pose/margin correction directions
without removing the template requirements; keep the base prompt passing `check` and save the
correction prompt separately. Rebuild and review the affected crop sheet after each change.
Repeated clipping requires a more compact pose or safer placement, not the same unchanged prompt.
Do not crop, pad, repaint or composite the character locally to make it fit. Do not report
BLOCKED merely because a retry or edit count has been reached.

## Step 4 — put it in the game

This is the one sanctioned change to a game's background; it needs no further opt-in when this
procedure runs. First record the background guard's "before" state (the commands in
[runtime-branding.md](runtime-branding.md), writing into `production/store-art/` with the suffix
`-before-campaign`), then export the runtime pictures:

```bash
"$STORE_PYTHON" tools/store_compose.py backdrop \
  --src production/store-art/shared-background.png \
  --out-dir assets/images/backgrounds --prefix bg_campaign --variants menu,game \
  --size 1080x2340 --pop off --calm 0.15 --vignette 0 \
  --confirm-game-background-replacement
```

`bg_campaign_menu.png` is the picture at full strength; `bg_campaign_game.png` is the same picture
with a light calm (0.15) so the live board and HUD win the eye while the character stays
recognizable. Never calm it harder to rescue a busy screen — give the HUD and board their own
backing plates instead (`anti-slop-design.md` §7). The size warning for a heavy PNG is expected at
1080×2340; do not trade the aspect for a smaller file, that crops the character.

Wire them (targeted edits only; screens keep their hierarchy):

- Add constants to the asset registry (`lib/assets.dart` or the project's equivalent) and confirm
  `assets/images/backgrounds/` is in `pubspec.yaml`.
- The main menu, the Flutter splash route and the secondary screens that showed the game's shared
  scene use `bg_campaign_menu.png`; the game screen uses `bg_campaign_game.png`.
- Draw it full-bleed under the safe area:
  `Positioned.fill(child: Image.asset(GameAssets.bgCampaignGame, fit: BoxFit.cover,
  alignment: Alignment.topCenter))`. Top alignment is what `background-crops.png` reviewed: short
  phones lose the bottom of the mound, never the head.
- The phone column's surround on wide hosts (`mobile-first-contract.md`) uses
  `bg_campaign_menu.png`.
- On the menu, nothing covers the character's face: controls and HUD chips sit beside or below it.
  On the game screen the field keeps its size and position from the gameplay-screen contract; where
  the layout leaves the upper band open, the character's head shows above the field. Do not shrink
  or move the field to reveal more of the character.
- Keep the old background files on disk (unselected) so the change can be reverted; keep every
  character, symbol and UI asset, all math and content data, and every screen's structure.

Then `dart format` the changed files, `dart analyze lib/` (0 errors) and `flutter test` (update a
test that pinned the old background constant; never delete a test to pass). Record:

- `design/asset-manifest.md`: rows for `bg_campaign_menu` / `bg_campaign_game` — class `derive`,
  source `production/store-art/shared-background.png`, SHA-256, and the replaced files;
- `design/art-direction.md` → "Campaign background": source, template id, alignment, what the
  menu and the game screen show of the character;
- `production/store-art/campaign.md` per [campaign-handoff.md](campaign-handoff.md).

## Step 5 — verify

The caller's runtime pass (finalize Phase 10.5, or the store kit's Phase 3 captures) checks the
integrated result at the four phone sizes as **V22**: the menu shows the whole character with
nothing over its face; every screen that used the shared scene now uses the campaign picture; the
game screen uses `bg_campaign_game.png`; nothing is stretched (V18); the wide-host smoke capture
shows the campaign picture as the column's surround.

If generation, capture, integration or review fails, preserve the cause and correct it, then
repeat the affected verification until it passes. Keep the previous accepted background wired
until its replacement passes; revert failed integration before repairing it. Mark the campaign
BLOCKED only when a required input/tool/service is unavailable or an explicit user resource
limit prevents continuing. Save the cause and resume state and finish independent work in that
case. A run with unresolved campaign art is never production-ready.
