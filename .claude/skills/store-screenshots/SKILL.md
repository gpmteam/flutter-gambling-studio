---
name: store-screenshots
description: "Create a store kit from the campaign: export the concept panorama the user approved before implementation unchanged (crops, grading and a detail pass only) as the carousel panels — torso-to-head character, the gameplay the game was built to match, mandatory flying x5/x10/x25/x50/x100 balls in every panel — then render the banner in its world from the template and a shipped ball asset. Phone slides put real captures on the game background — the same picture the game uses, character whole in frame. Add feature graphic from the banner, icon/emblem in the panorama's world, and ZIP. Started automatically after /autocreate-finalize; legacy games without an approved concept get a panorama first."
argument-hint: "[--count 8] [--panels 3] [--lead-kind character|object|mechanic] [--character-framing bust|mascot] [--banner-layout free|left-heavy] [--size 1320x2868|play] [--no-play-set] [--frame ios|android|none] [--no-apply] [--no-wire-logo] [--no-captions] [--keep-runtime-background]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Context-based store kit

Read `.claude/docs/visual-context.md`, `.claude/docs/game-concept-examples.md`,
`.claude/docs/art-lineage.md`, and the game's concept, art direction, asset manifest, math config,
the approved concept (`production/store-art/concept/`) and runtime evidence. Inspect matching
`examples-games/` previews by default, and every source in `design/reference-contract.md` when the
game is a reference game — its store art is that reference's world. References guide composition; the shipped assets and
mechanics govern identity. Never change a real game to match a preview's topology or palette.

**Generation order: the approved panorama first, then the banner.** The panorama is not made
here. `/autocreate` rendered it before any game code existed, sliced it into these same carousel
panels and stopped until the user approved it ([references/concept-panorama.md](references/concept-panorama.md));
the game's field was then built to look like its gameplay sample, and the game background was
rendered in its world ([references/campaign-art.md](references/campaign-art.md)). This run exports
that panorama **unchanged** — crops, grading and the detail pass only — so the listing shows
exactly what the user approved, and renders the banner in its world. Read
[references/campaign-handoff.md](references/campaign-handoff.md) in preflight: reuse the approved
panorama and a valid game background; make the banner (or reuse one already made in this
panorama's world). A game made before the approval gate has no approved panorama: preflight makes
one first with concept-panorama.md, then the run continues identically. Nobody writes a campaign
prompt by hand: the panorama, background and banner are rendered from
[references/campaign-prompts.md](references/campaign-prompts.md) and proved with
`tools/prompt_template.py check`, so a picture made here and one made by the pipeline come from
the same words.

The horizontal feature banner, with the character on the left, is the last campaign picture: it is
rendered with the approved panorama attached as **world context**, so the carousel, the feature
graphic and the game read as one campaign — environment, palette, lighting, board housing,
lower-edge band and multiplier-ball look all come from the panorama.

For a character-led kit, the shipped character asset is the canonical player reference in
**every** image-generation call and is always attached first. Supply the original asset file
again for a retry or a separate icon render. The approved panorama is the only generated image a
later call may receive, and only as world context: it is never the character reference, and the
banner is a new horizontal composition, not an edit, outpaint or crop of the panorama. The generated scene
may establish pose and composition, but it cannot redefine the character's face, silhouette,
costume or colors. If the character has multiple shipped layers, use the original layers or a
lossless assembly of them.

**Character framing is mandatory, not a style choice.** When the game has a main character, every
generated scene that shows it (banner, panorama and any showcase background) frames it from
torso to head. The bottom frame edge or the lower-edge foreground objects cut the body through
the torso, so no legs, knees, hips or feet are visible. The character is never standing full
length and never flying, floating, leaping or levitating. Its cut torso rises from the bottom
of the frame or from behind the foreground objects, with no background showing beneath it. Animal
mascots follow the same rule in species-appropriate terms: body to head, with no legs, paws,
talons or feet visible. A full-body, standing, flying or leg-revealing character is an
objective failure.

**The game background is not a marketing scene.** `shared-background.png` is the picture the
game itself runs on and the backdrop of every phone slide. It shows the campaign's world with the
main character torso-to-head and **whole inside the portrait frame** (head, headwear, shoulders,
hands and held props clear of every edge), and it carries no multiplier balls, lettering, board or
UI — a promotional `x100` behind real gameplay would read as a payout claim. The ball and
lower-edge requirements below govern the banner, the panorama and any showcase background; the
character framing governs the game background too.

**Flying multiplier balls are mandatory in every scene.** The banner, the panorama and any
showcase background each contain all five labelled balls (`x5`, `x10`, `x25`, `x50`, `x100`),
visibly airborne and scattered at varied heights and depths around the character and across the
gameplay. Every panorama panel carries at least one ball. That includes the character's panel,
where at least one ball flies around the character (beside or above the shoulders and head)
without touching it. Several must fly **in front of gameplay** and visibly cover parts of the
board, symbols or outcome area in the marketing scene. Balls may obscure any scene element except
the visible player/hero character silhouette, including headwear, face, hands and costume.
Character occlusion is a placement error. A missing ball, a ball resting on an object or a panel
with no ball is an objective failure. Keep the five ball labels legible. Review art at final
crop size; after a correction review affected crops again. Use format/dimension checks for exports. Do not run numeric composition gates or repeat visual
audits of unchanged art to optimize scores.

**The image model generates the multiplier balls and their labels in the same call as the rest
of the scene.** Choose one suitable shipped round asset, such as a ball, coin, token or orb,
confirm its path in the game's asset registry or `pubspec.yaml`, and attach that file to every
scene-generation call as the **multiplier reference**. The model paints the balls from that
reference: same silhouette, material, color and ornament, rendered at scene scale with the scene's
own light, reflections, glow and motion. Write the exact labels `x5`, `x10`, `x25`, `x50` and
`x100` into the prompt so the model letters them onto the balls. Never cut out, copy, paste or
alpha-composite the asset (or any sprite, label, board plate or screenshot crop) into generated
art, and never draw a label with Pillow, the compositor or any other script. The compositor only
grades, slices and frames finished images. The one blend allowed inside generated art is
`tools/region_repair.py merge`, which lays the image model's own re-render of a region back into
the same scene (see "Correcting a generated scene").

Create local artifacts; do not publish or build release binaries. Apply icon/emblem unless
`--no-apply`. Runtime backgrounds and wiring remain unchanged after campaign art: the game's
background is the campaign game background, changed only by campaign-art.md (which this run
invokes when the handoff is missing or stale, unless `--keep-runtime-background`), and never
replaced with the panorama. All copy is English unless another game language was requested.

**The approved panorama is a contract.** The user approved it before a line of game code was
written, and the game was built to match it. Never regenerate, re-render, whole-frame edit,
outpaint or re-letter it to suit a review, and never change its composition, pose, palette or
content. It may only be cropped (`--seam-snap`, `--offset`, `--offset-y`, `--zoom`), graded by the
compositor and detail-passed for export resolution; an objective defect the concept review missed
(a misspelled label, a broken hand) is a region repair of that defect alone. The archive gate
proves it: `tools/check_store_kit.py --concept production/store-art/concept/concept.json` refuses a
kit whose `art/panorama.png` does not descend from the approved file through recorded `derive`,
`detail` and `repair` steps.

## Outputs

Default N=8 screenshots: P=3 adjacent concept panels sliced from the approved panorama — the
carousel the user approved, exported with its recorded flags — followed by N−P actual
gameplay/meta captures with optional device frames and captions, set on the
game background from the campaign art — the same picture the captured game shows (see Phase 5).
With `--keep-runtime-background` they sit on the panorama's opening panel instead. Produce `store/`
at 1320×2868 and `store-play/` at 1080×1920 independently, not by resizing one set into the other.
Include a dedicated text-free 1024×500 feature graphic: the banner scene plus one phone on the
right holding a real screenshot, with no title or copy on the left or anywhere else (see Phase 5),
icon masters/platform densities (1024 launcher master, 512×512 Play listing icon, frame-free —
see Phase 3), transparent emblem, `STORE_BRIEF.md`, `STORE_INFO.md`, and ZIP under `project_zip/`.
`--no-play-set` omits Play screenshots. `--panels 0` skips panorama work and uses real captures
on the game background for all N screenshots; the banner still carries all five balls and the
feature graphic is still produced. Only `--panels 0 --keep-runtime-background` generates the
themed multiplier showcase background of Phase 1b. Store formats never change the runtime layout,
which follows `.claude/docs/mobile-first-contract.md` (portrait phone only).

## Phase 0 — context and preflight

Read the runbook and relevant references once. Reuse already-read guidance and extracted game
facts; reread only changed files or the specific section needed for a new decision. Keep learning
observations pending for a separate task, including when an art gate blocks delivery.

Select and verify an existing interpreter before installing dependencies. A missing import in
system Python does not mean the project's virtual environment is missing that package. Honor
an explicit `STORE_PYTHON` executable path; otherwise probe the active environment, project
`.venv`, and `python3` in that order. Keep the selected absolute path for subsequent tool calls
(including separate shells); do not assume a previous shell's activation persists.

```bash
if [[ -z "${STORE_PYTHON:-}" ]]; then
  for store_candidate in "${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}" "$PWD/.venv/bin/python" python3; do
    [[ -n "$store_candidate" ]] || continue
    if "$store_candidate" -c 'import PIL, numpy' >/dev/null 2>&1; then
      STORE_PYTHON=$("$store_candidate" -c 'import sys; print(sys.executable)')
      break
    fi
  done
fi
[[ -n "${STORE_PYTHON:-}" ]] || {
  echo "No probed interpreter imports Pillow and numpy. Set up a project environment and rerun preflight."
  exit 1
}
"$STORE_PYTHON" -c 'import sys, PIL, numpy; print(sys.executable); print("Pillow", PIL.__version__, "numpy", numpy.__version__)' || exit 1
```

If no existing environment passes, use the project's dependency setup and install into the
chosen environment with its own `-m pip`; avoid a bare `pip` that may target another Python.
A failed explicit `STORE_PYTHON` stops preflight so the chosen interpreter can be corrected.
Use `"$STORE_PYTHON"` for the compositor and other Python tools in this runbook.

Require a real Flutter game, Pillow/numpy, the image-generation path, compositor and capture
tools. Read `"$STORE_PYTHON" tools/store_compose.py --help` and the relevant subcommand help.
Runbook options such as count, board, hero, no-apply and keep-runtime-background govern orchestration;
do not blindly pass them to compositor subcommands. Initialize:

```bash
PROJECT_NAME=$(awk '/^name:/{print $2; exit}' pubspec.yaml)
TS=$(date +%Y%m%d-%H%M%S)
STORE_ROOT=project_zip
STORE_DIR="$STORE_ROOT/$PROJECT_NAME-store-$TS"
ART_DIR="$STORE_DIR/art"
RAW_DIR="$STORE_DIR/raw"
OUT_DIR="$STORE_DIR/store"
PLAY_DIR="$STORE_DIR/store-play"
mkdir -p "$ART_DIR" "$RAW_DIR" "$OUT_DIR" "$PLAY_DIR"
```

**Campaign art comes first — the approved panorama before everything.** Validate
`production/store-art/` by [references/campaign-handoff.md](references/campaign-handoff.md):

1. **Panorama.** `python3 tools/concept_gate.py status`. APPROVED → copy
   `production/store-art/concept/panorama.png` unchanged and read
   `production/store-art/concept/export-flags.txt` (the crop the user approved) and
   `gameplay-sample.md`. PENDING or DRAFTING → stop and report BLOCKED: the concept carousel is
   waiting for the user's approval. NONE (a game made before the approval gate) → make the
   panorama now with [references/concept-panorama.md](references/concept-panorama.md), legacy
   caller, a real gameplay capture as context, written to `$ART_DIR/panorama.png`.
2. **Game background.** Valid → copy it. Missing or stale → run
   [references/campaign-art.md](references/campaign-art.md) Steps 2–3 now (background in the
   panorama's world, export, wiring, analyzer and tests). Skipped with `--keep-runtime-background`.
3. **Banner.** Valid for this panorama → copy it. Otherwise run campaign-art.md Step 4 after the
   current captures exist (Phase 3), with the approved panorama as world context.

```bash
cp production/store-art/concept/panorama.png "$ART_DIR/panorama.png"   # approved: byte-identical
cp production/store-art/shared-background.png "$ART_DIR/shared-background.png"  # not with --keep-runtime-background
cp production/store-art/long-banner.png "$ART_DIR/long-banner.png"     # only when valid for this panorama
```

Write `STORE_BRIEF.md` before any generation call:

- Casual category/balance model, title, scoring, theme, source palette/materials/light and fonts.
- `lead_kind: character | object | mechanic`, exact subject and in-game role. A chicken is a
  character; a crown/coin/board is not. No invented mascot or character-only opening for objects.
- Inspected references, borrowed traits and original adaptations.
- Panorama provenance: the approved concept revision, its SHA-256 and approval time from
  `concept.json`, the recorded export flags, and the gameplay sample it promised — or, for a
  legacy game, that this run made the panorama and it was not user-approved.
- Panel map read from the approved panorama: what each panel shows, where the gameplay sits and
  spans. Any panel, the right two, or all three may carry gameplay. There is no required middle
  field or final reward-only panel.
- Banner plan: lead on the left, where the character's torso is cut (bottom edge or foreground
  band), gameplay placement, lower-edge band, where each of the five flying balls sits, and what
  continues under the phone on the right — the panorama's world in a horizontal composition. Note
  where the character's pose, crop or placement differs from the panorama.
- Lower-edge plan (see Phase 1): the game's own objects chosen for the close-up foreground band,
  their left-to-right order, which ones cross seams, and the real game objects used for the foreground layer.
  Record the game's warm/cool light sources and polished materials.
- For an object/mechanic-led game with no living character in its concept and shipped inventory,
  mark slides 1 and 2 as gameplay-led. Each opening crop, reviewed separately, must show
  recognizable authentic play at a three-quarter/3D angle, either through two readable samples
  or one continuous angled gameplay surface with meaningful play visible in both. Do not
  introduce a person, hand, animal,
  mascot or player silhouette; slide 1 cannot be a decorative object-only scene.
- Actual topology and resolving state. New unspecified classic slots default to 3×3; store
  work preserves the shipped game's dimensions, symbols, ordering and outcome. Record the
  gameplay capture as a visual reference for generation, never as a layer for the panorama.
- The canonical character asset path (if present), the shipped asset attached as the
  multiplier reference, plus source assets used for other visible gameplay objects. Record
  their scene roles. The multiplier reference must be an actual asset file.
- Required store-art multiplier-ball set for every game: `x5`, `x10`, `x25`, `x50`, and `x100`,
  whether or not those values exist in the game's scoring config. These are themed marketing-scene
  objects, not a gameplay state, a payout claim or a reason to change game math. Record which
  values, if any, are actual in-game rewards and keep unsupported values out of real gameplay
  captures, captions, scoring claims and feature-phone UI. Never present the five balls as a
  guaranteed result. Showcase captions on real-capture slides use compositor typography; the
  ball inscriptions are generated by the image model from the prompt, and nothing letters the
  generated art afterward.
- Multiplier-ball art direction: the multiplier reference path, its original material, palette
  and ornament, the label style (display face, color, outline), glow/sparkle treatment, lighting,
  target size and placement in the banner, panorama and any showcase background. Size is judged
  in the final panel crop, not the wide source image. Aim for prominent balls around 35-40% of a
  portrait panel's width, adjusting for the artwork.
  Record the exact labels separately from the visual treatment so a styled ball never changes
  a game's scoring meaning.
  Map each value to a position and flight direction across the full panorama, judging space in
  the final portrait crops. Scatter the five balls so every panel carries at least one, with no
  fixed label assignment per panel. On the character's panel, at least one ball flies around the
  character, clear of its silhouette. Place at least two ball bodies
  across the board/mechanic or its symbols so they visibly hide a portion of gameplay in the
  exported marketing panels. Keep every ball outside the player/hero silhouette. Map the same
  behavior in the banner and, for `--panels 0`, the themed showcase background wherever the
  marketing scene depicts gameplay. Do not alter authentic captured gameplay in a phone.
- Independent feature layout: `free` by default or justified `left-heavy`; no reserved device zone.
  The feature graphic is text-free: record the chosen capture for its right-side phone, not a
  title or tagline.
- One initial attempt per scene this run makes (the banner, a legacy game's panorama, any
  `--panels 0` showcase background and any icon), followed by correction until the required
  exports pass. Fresh renders restart from the original assets, plus the approved panorama for
  later scenes; local defects are repaired region by region on the current candidate, never by
  re-editing an edited frame. The approved panorama itself is never one of these scenes. Follow
  the correction policy below. Reuse accepted art and preserve evidence of failed attempts.

Collect the original character asset and the gameplay sprites that will be visible in the art.
Exclude UI chrome, fonts, backgrounds and store outputs. Preserve originals; convert non-PNG
sources to lossless PNG references only when the image tool needs PNG. If reference slots are
limited, prioritize the original character asset, then the approved panorama (for later scenes),
the multiplier reference, the gameplay capture and visible sprites.
Written descriptions and generated previews never replace the character asset.
For the multiplier reference, choose a shipped round asset such as a ball, coin, orb or token.
If it sits on an opaque background, a local cutout may give the model a cleaner reference; that
cutout is only an input to generation and never enters the art. If no shipped asset can serve
as a recognizable ball reference, report the missing source instead of inventing an orb.

Capture or locate a real active/resolving gameplay frame as reference-only context. Record its
field rectangle and actual state. A symbol-built board is provisional until a real frame exists.
Games without a grid use the actual curve, machine, card or other mechanic surface. After campaign
art and before any other edit, record all runtime-background files, hashes and selecting
code/config references, including registered splash/shared backgrounds outside conventional
directories. See [references/runtime-branding.md](references/runtime-branding.md).

## Phase 1 — the approved panorama, then the banner

### Composition rules shared by every scene

Choose the panorama aspect from panel count and target geometry. When the game has a main
character, frame that character from torso to head in the banner and the panorama, showing
enough torso to read the costume and pose. Humanoids crop through the torso; animals crop through
the body in species-appropriate terms. In both cases the bottom frame edge or the lower-edge
foreground objects hide everything below the cut: no legs, knees, hips or feet. Never pose the
character standing full length, flying, floating or leaping. Leave visible open space above the
complete head/headwear in the final panel crop, at least 2% of panel height, and protect
attached forms from the first seam.
Character-led Joker/chicken games default to a large real character on panel 1. Use
`--character-framing bust` for humanoids and `mascot` for a compact chicken/animal. Both are
torso-to-head framings with no legs or feet; mascot mode only measures prominence by area rather
than humanoid height, and still protects the head, first-panel placement and attached
silhouette. A left crop is allowed and a bottom crop through the torso is expected; preserve the
mascot's recognizable head and body. Joker is a mischievous, slightly vicious
playful trickster, not an elegant courtier or horror figure. Object/mechanic scenes have no empty
character berth and no anatomy constraints. Keep a strong game anchor in every panel; a continuous
board can anchor several. Flying multiplier balls must cover part of the board or mechanic in
marketing art.
When the shipped game has no living character, its first two carousel slides must instead be
gameplay-led: present the real board or mechanic at a readable three-quarter/3D angle in each crop,
or span one continuous angled surface across both with meaningful gameplay visible in both. Never
add a human, hand, animal, mascot or player silhouette to supply drama. The object lead may frame
the action, but it cannot replace gameplay in slide 1.

Give the image generator the canonical character asset, actual gameplay capture, relevant shipped
sprites, the multiplier reference and matching previews. Label the original character asset as
**identity authority**, the multiplier reference as the **ball model**, and the capture as
**context only**: it establishes the real mechanic, field dimensions, symbol identities, ordering
and resolving state. Request a complete, coherent image in one generation: the game surface
itself appears as a scene-native three-quarter/3D view, with its housing, depth, lighting,
foreground band, labelled multiplier balls and surrounding environment generated together.
Noncritical board structure may cross seams. A rough layout sketch may indicate panel cuts and
subject positions, but it must not contain a screenshot-shaped opening intended for later fill.
Do not generate a background, empty board recess or blank ball placeholder to fill later.

**Lower edge.** Frame the bottom of the scene like close-up casino key art: the game's own
symbols and objects rendered very large, near the camera, across the full width. For a
three-panel scene use roughly 5–7 hero objects, each around a third to half of a panel wide,
overlapping one another in depth, cropped by the bottom edge and at some seams, and occupying
about the lower quarter to third of the image. Beneath and between them, a continuous glittering
layer of the game's actual tiles, gems, balls or other pieces runs the whole width, so the band reads as
a treasure spill rather than a row of cutouts. The pieces are game objects, not a surface: no
floor, fabric, tabletop, podium, platform or velvet drape. Vary scale and angle for rhythm; keep
the game objects recognizable where visible; do not shrink them into miniature clutter. Light the band
with the scene's warm and cool sources: specular highlights, rim light and reflected color. A few
other game objects may fly higher. Where the character's cut torso meets the band, the objects
hide everything below the cut, so no legs or feet appear. The multiplier balls stay visibly in
flight, including when they cross the foreground; none rests on a lower object.

**Multiplier balls.** Every scene shows all five labelled balls in flight: the banner, the
panorama (with at least one ball in every panel, the character's panel included) and, when
`--panels 0`, the themed showcase background. This is required for every game and lead kind.
Each ball is the multiplier reference re-rendered by the model: keep its silhouette, material,
color and ornament recognizable while the scene's lighting shapes it, with a specular highlight,
rim light in the scene's accent color, reflected color from neighbors, a halo, sparkle ring or
energy glow drawn from the game's own FX vocabulary, and a short motion trail. The label is the
dominant feature on the ball face: short chunky display numerals filling roughly 60–70% of the
ball's width, in the game's warm display color (gold/yellow in most casino themes) with a dark
outline, an inner highlight and a slight 3D bevel, following the ball's curvature. A flat
sticker look, a thin or small label, an unlit disc and a ball that looks pasted over the scene
are the failures this rule prevents. Scatter the balls at irregular heights, depths and flight
directions. At least two must cross in front of the board or mechanic and visibly obscure part of
it; do not move them all above the action to preserve gameplay visibility. They may overlap lower
props but must remain clear of the player/hero silhouette. Avoid a row, regular grid or tight
cluster. Match any user-supplied size reference.

### 1a — Panorama (the approved concept)

`art/panorama.png` is the concept panorama the user approved, copied byte-identical from
`production/store-art/concept/panorama.png`. It already satisfies every rule in this phase: it was
rendered from the `panorama-character` or `panorama-object` template in
[references/campaign-prompts.md](references/campaign-prompts.md) — this phase's composition rules,
lower edge, multiplier balls and first-prompt requirements written out literally — reviewed
against Phase 2, and exported with the same `triptych` command this run uses. Do not render,
edit, outpaint or re-letter it. Phase 4 crops and detail-passes it; nothing else touches it.

For a game made before the approval gate, preflight made it with
[references/concept-panorama.md](references/concept-panorama.md) as one complete, coherent image:
the torso-to-head character, scene-native gameplay at a three-quarter/3D view with the real
capture as context only, the lower-edge band, all five labelled balls in flight with at least one
in every panel, and the environment. Attach, in order: the original character asset (identity
authority), the multiplier reference (ball model), the composition guide
(`store_compose.py composition-guide --field <capture>`: placement and the panel cuts), the
gameplay capture (context only), visible shipped sprites, matching previews. When the tool takes custom sizes, `3456x2384` (about 1.45:1)
covers three 1320×2868 panels plus the default hidden seam allowance. No banner is attached: the
banner is made from the panorama, never the other way round.

### 1b — Banner (panorama as world context)

`art/long-banner.png` is the campaign banner, made by campaign-art.md Step 4 unless a banner
already exists in this panorama's world: the prompt is `banner-character` or `banner-object` from
[references/campaign-prompts.md](references/campaign-prompts.md), rendered with this game's values
and passing `tools/prompt_template.py check`. The template is this section and "First-prompt
requirements" below written out once for the banner; do not re-adapt them yourself. The approved
panorama is attached as **world context**, not as a source to extend: the banner inherits its
environment, palette, lighting, board housing, lower-edge treatment and ball look in a new
horizontal composition, not an edit, outpaint or crop of the panorama. The character may take a
different pose, expression, crop or panel than in the panorama, but it stays framed from torso to
head with no legs visible; identity still comes only from the original asset. For a character-led
game the character appears large on the left, framed from torso to head: the bottom edge or the
foreground band cuts the body through the torso, with no legs or feet visible, and the character
is neither standing full length nor flying. Object/mechanic leads put the lead object or the
angled gameplay surface there instead, with no invented character. The mechanic sits at a
three-quarter/3D angle beside the lead, the environment runs edge to edge, and the lower-edge band
crosses the full width. The right third continues the scene without a face or decisive symbol,
because `banner` seats the phone there (centered at 82% of the width, about a third of it wide).
That area is not an empty reserved zone: background, housing and foreground run through it.
Include all five labelled multiplier balls flying around the character and across the gameplay,
clear of the character's silhouette. Keep their labels out of the right-third phone seat so the
shipped graphic shows all five, and never keep balls off the gameplay to preserve it. No title,
logo, wordmark, tagline, device, UI or copy space; a left side left blank for text is a failed
banner. The banner must look finished alone.

Attach, in order: the original character asset (identity authority), the approved panorama (world
context — not a character reference), the multiplier reference (ball model), the gameplay capture
(context only), visible shipped sprites, matching previews. When the tool takes custom sizes,
`3840x1872` matches the 1024×500 delivery aspect. The banner is made after Phase 3's captures, so
its gameplay context is the current game — which was built to match the panorama's gameplay
sample. Copy the accepted `production/store-art/long-banner.png` to `$ART_DIR/long-banner.png`.

Only for `--panels 0 --keep-runtime-background`, generate the portrait
`art/multiplier-showcase-bg.png` the same way, with the approved panorama as world context, all
five labelled balls in the scene and the existing game background as inspiration. Keep runtime
background files unchanged.

### First-prompt requirements

This is the composition requirement every scene's **first** prompt carries. The panorama's and
the banner's versions exist, written out once and literally, as the `panorama-*` and `banner-*`
templates in [references/campaign-prompts.md](references/campaign-prompts.md) — render those,
never a paraphrase. Adapt it the same way to any showcase background:

> One continuous, fully illustrated game panorama set in the game's own world. Reproduce the
> supplied original character asset faithfully; it is the identity authority, and every other
> image is context. If the game has a main character, frame it as a torso-to-head bust (or the
> species-appropriate equivalent): the bottom edge of the image or the large foreground objects
> cut its body through the torso, so no legs, knees, hips or feet are visible anywhere. The
> character is not standing full length and is not flying, floating or leaping; its cut torso
> rises from the bottom of the image or from behind the foreground objects. Leave visible open
> space above the entire head/headwear in the final panel crop, at least 2% of panel height.
> Paint five multiplier balls modeled on the attached ball asset, all required, clearly
> airborne and flying around the character and across the scene at varied heights, depths and
> horizontal positions, with at least one ball in each of the [N] portrait panels and none
> resting on an object. Letter each ball on its face with exactly one of
> these inscriptions, each used once: "x5", "x10", "x25", "x50", "x100". Make every label big,
> chunky 3D display numerals in [warm display color] with a dark outline and inner highlight,
> filling most of the ball face and following its curve. Light the balls with the scene: glossy
> specular highlights, [accent] rim light, a glowing [halo/sparkle ring/energy flare from the
> game's FX], and a short motion trail. At least two balls fly in front of the board and cover
> part of it. The balls may cover any other scene element; keep every ball clear of the
> character's silhouette. No other text, title, logo or UI anywhere in the image.

Include this lower-edge and lighting direction in the first prompt of every scene, adapting it to
the game's real palette and objects:

> Across the whole lower edge, place about 5–7 of the game's own objects very large and close to
> the camera: [ordered list], overlapping each other in depth and cropped by the bottom edge, filling
> about the lower quarter to third of the image. Under and between them, a continuous glittering
> layer of actual game objects runs the full width. No floor, fabric, tabletop, podium or drape, and no
> miniature clutter. Give the scene vivid, high-impact mobile-game key-art lighting from the game's
> authentic palette. Separate warm and cool hues, add clean specular highlights to polished
> materials, theme-appropriate rim light on primary subjects, and reflected color between nearby
> objects. Use small star glints selectively and localized bloom around real light sources or
> verified magical effects. Keep shadows rich in color, midtones saturated, and a few highlights
> near white. Keep the background luminous but subordinate through softer focus and lower local
> contrast. Preserve the source asset colors; avoid a global color wash, muddy shadows, flat
> lighting, matte gems and all-over haze. The scene should look exciting and premium before
> compositor grading.

Use the available built-in image tool; headless generation follows `generate-png-asset/SKILL.md`
and `tools/gpt_image.py edit` with a prompt file and repeated `--image` inputs in the order above.
Record every candidate as it lands, with each attached image — the ledger refuses a reference
that is an earlier banner or any generated store picture other than the panorama
([art-lineage.md](../../docs/art-lineage.md)):

```bash
python3 tools/art_lineage.py record --file production/store-art/long-banner.png --role banner \
  --made fresh --ref "$CHARACTER_ASSET" --ref "$ART_DIR/panorama.png" --ref "$MULTIPLIER_REF" \
  --ref "$RAW_DIR/<capture>.png" ... --prompt production/store-art/banner-prompt.txt
```
The compositor may grade and slice the finished panorama; it must not assemble its gameplay
field or add anything to it. `boardplate` is retired for this workflow, and `triptych` refuses
`--sprite` and `--sprite-dir`.

Use the runtime capture to keep the game surface recognizable. The generated marketing scene
may be partly covered by flying balls; authentic gameplay remains visible in the separate real
captures. Check for a pasted screenshot boundary in the single final visual pass.

### Correcting a generated scene

Review inscriptions and gameplay at final export size. Objective failures include incorrect
labels or missing balls, forbidden character framing, character drift, balls overlapping the
character, incorrect board dimensions or symbol ordering, and links that change the captured
move or scoring state. Preserve the real mechanic, topology, symbols, and state.

A failed visual review starts a correction loop; it does not end the pipeline. Continue until
all requested exports pass, without a fixed number of fresh retries, targeted edits, or crop
adjustments. Reuse accepted artwork and correct only failed scenes. Never declare PASS or
package rejected art to end the loop.

The one exception is the **concept panorama before approval** (`/autocreate` Phase 3.9 and
`--revise`): the user reviews it the moment it is published, so its loop is bounded — three fresh
renders and five region repairs per revision (`tools/concept_gate.py budget`, enforced by the
lineage ledger), after which the best candidate is published with its remaining defects named as
known issues ([references/concept-panorama.md](references/concept-panorama.md) → Step 4). It never
declares those defects fixed; it hands them to the user.

The approved panorama is corrected only by crop, and by a region repair for an objective defect
the concept review missed. A composition or taste note against it is not a defect: the user
approved that composition, and the game was built to match it. Record the note in
`STORE_INFO.md` for a later concept change; do not act on it here.

**Repairs must not compound.** An image-model edit re-renders the whole frame even when the
prompt says "change only X": every pixel is painted again, so an edit of an edit stacks
generation loss — detail softens, texture smears, colour drifts and the character's face slowly
changes. A panorama that went through a fresh render and three corrective edits (move the hero,
lower the board, re-letter one ball) shipped visibly mushier than the banner beside it. Choose
the correction from the defect, in this order:

- **Crop first.** A seam, gutter or frame edge clipping a label, the head or a board row is an
  export problem, not an art problem: move the cut (`--seam-snap`, `--offset` with `--zoom`,
  `--offset-y` for the Play set's vertical crop) and re-export. No new image.
- **A local defect is repaired as a region.** A wrong or misspelled label, a ball to add, lift or
  nudge, a hand, a wrong cell or connector: cut a window around it, let the image model re-render
  that window, and merge back only the defect box. Every pixel outside the box and its feathered
  edge stays byte-identical, and the box is drawn at more resolution than the candidate had there, so any
  number of repairs costs no more picture quality than one.
- **A composition defect gets a fresh render** — of a scene this run makes, never of the approved
  panorama. The character too large or in the wrong panel,
  the board in the wrong place, a ball that has to move across the scene: write the correction
  into the prompt and render a new composition from the original references (plus the approved
  panorama as world context), keeping what the review already accepted as explicit direction.
- **At most one whole-frame edit per lineage.** A whole-frame edit may take only a
  first-generation render as its input; never send a frame that is itself an edit, or contains a
  merged repair, to another whole-frame edit. Headless whole-frame edits keep the candidate's
  size: `tools/gpt_image.py edit ... --size like:<candidate.png>`, never the 1536x1024 default.
  Run `tools/art_lineage.py check --file <candidate> --for edit` first; it answers from the
  ledger, which remembers edits made in earlier runs too.

```bash
"$STORE_PYTHON" tools/region_repair.py cut --src "$ART_DIR/panorama.png" \
  --box X0,Y0,X1,Y1 --out-dir "$ART_DIR/repairs/01-x25-label"
# Image model: the original character asset first, the shipped multiplier reference when the
# defect is a ball, then repairs/01-x25-label/window.png named as the EDIT TARGET, with the
# defect's position in that image (printed by `cut`) and everything else in it as invariants.
# Headless: tools/gpt_image.py edit ... --size <printed by cut>. Built-in tool: view_image the
# window first, then copy its output to repairs/01-x25-label/render.png.
"$STORE_PYTHON" tools/region_repair.py merge \
  --plan "$ART_DIR/repairs/01-x25-label/plan.json" \
  --render "$ART_DIR/repairs/01-x25-label/render.png" --out "$ART_DIR/panorama-r1.png"
```

Keep the box tight but whole: the complete ball with its label, the hand with its prop, the
cell. `window-marked.png` outlines the box for your review; never attach it to the model. The
merge aligns the render (models reframe by a few pixels), matches its tone on the untouched ring
and refuses a render that is not a re-render of that window. Review `proof.png` (before | after |
difference) and the affected export crops. A seam-difference warning means the model also
changed the surroundings: widen the box or re-render with them named as invariants. Several boxes
cut from one candidate merge in turn, each with `--base` set to the newest candidate. The merged
pixels are the image model's own render of that region of the same scene, which is why this is
the one blend allowed inside generated art.

Fresh renders may use the approved panorama as world context, never rejected art as an identity
reference. For a wrong symbol or chain connector, attach the window, original identity assets,
authentic capture, and exact runtime facts; identify the cells and requested change. Never
paste, warp, repaint, or composite a board or chain locally.
Never letter it with a script. Attach the original character asset first when present and the shipped multiplier reference
when correcting a ball. Keep unrelated scene content unchanged.

Record prompts, input/output paths, the observed defect, and the correction result. Record each
candidate's lineage with `tools/art_lineage.py record` (`--made edit|repair --parent <candidate>`),
and never attach a rejected candidate or an earlier panorama to a fresh render.
Review the changed region and affected App Store, Play, or phone crops; verify previously
accepted identity, labels, and gameplay remain valid. Reject repairs that introduce unrelated
drift and retain the closest valid candidate. If a defect recurs, change the composition, pose,
margins, prompt, box or crop strategy using that evidence instead of repeating the same failed
approach. Recheck the complete export contact sheet after composition changes; avoid repeated
audits of unchanged art.

Preserve failure evidence under `production/store-art/failed-delivery/` while continuing repairs.
BLOCKED is reserved for an unavailable required input/tool/service or an explicit user resource
limit that prevents further work; an attempt count or failed visual review alone is not a blocker.
Stop at the user's request. If an external blocker prevents continuing, save the exact cause and
resume state, finish independent work, and report the incomplete delivery accurately.

## Phase 2 — visual review criteria (apply after exports)

After the first full export, inspect one contact sheet showing the final App Store and Play crops,
plus the feature graphic. The approved panorama's art was reviewed before the user approved it:
here its crops are reviewed (a label or head cut by a seam, a board row lost by the Play crop),
and its art only for an objective defect. The banner and anything else this run made get the
whole review. Compare the character to its original asset, verify that `x5`, `x10`,
`x25`, `x50` and `x100` each appear once, spelled exactly, on distinct airborne balls in the
panorama and in the banner, and that every panorama panel carries at least one ball. Check that
any main character reads from torso to head in the banner and the panorama. Its body should be
cut through the torso by the bottom edge or the foreground band, with no legs, knees, hips or feet
visible. It should be neither standing full length nor flying or floating, with visible space
above the complete head in the final panel crop. Check for clipped labels, missing panels or an
obvious pasted screenshot
boundary. Check that the balls
read as the multiplier reference (silhouette, material, color, ornament) painted into the scene:
lit by it, with glow and motion, labels bold and dominant. A flat, pasted-looking or small-label
ball is an error. Confirm at least two ball bodies visibly cover gameplay and none overlaps the
player/hero silhouette. Do not move balls off the board to clear the action. Check that the
banner visibly shares the approved panorama's world, and that the lower edge is a close-up band of large,
readable game objects over a continuous layer of the game's own pieces, without a floor, drape or heap of tiny props.
For a game without a character, check that no player/mascot was invented. Apply the correction
policy from Phase 1 and recheck affected crops after repairs; avoid repeated audits of unchanged
art, per-sprite audits, numeric scoring or subjective regeneration cycles.

Judge lighting in the generated source, before compositor grading. It should feel vivid and
celebratory while retaining the game's authentic colors. Look for clean highlights, selected
glints, local bloom and color-rich shadows; reject a flat global cast or uniformly dull scene.
Avoid clipped highlights, crushed shadows, blanket saturation and bloom that washes out faces,
symbols or text. The compositor should preserve the source look; make at most one visible
exposure adjustment and do not tune numeric palette or foreground metrics. Keep runtime assets
untouched.

## Phase 3 — branding and current captures

Follow [references/runtime-branding.md](references/runtime-branding.md) for icon/emblem application,
platform-density checks and background guards. Honor no-apply/no-wire-logo. The icon and emblem
are generated with the approved panorama as world context. The game background is the campaign's
and stays as campaign art wired it; `--apply-backdrop` is retired, and
`--confirm-game-background-replacement` belongs to campaign-art.md alone.

Capture menu, active play, peak tension, win/reward and a useful meta state after branding using
`/emulator-test` or `tools/web_verify.mjs` against the actual running URL. A typical capture uses
`--size 390x844 --dpr 3 --budget 180 --quick`. Every capture must show the integrated campaign
background (V22 in `/emulator-test`); a frame from before campaign art is stale. Reuse frames only
if current and authentic. Reject
blank, duplicate, loading, error, overflow and fabricated states; parse runtime exception logs.
Apply `.claude/docs/gameplay-screen-contract.md`: never use cropping or device chrome to conceal
weak gameplay. If the actual state changed, correct integration/feature art and re-export;
an unchanged matching capture does not justify another generation call.

## Phase 4 — final exports

Export both sets directly from the approved panorama with the flags recorded in
`production/store-art/concept/export-flags.txt` — the same command the concept carousel was
exported with. The concept carousel is the Google Play set, so the `store-play/` panels are the
slides the user approved. (A concept approved before the carousel moved to the Play size was
exported at 1320×2868; the size of `production/store-art/concept/panels/store-01.png` says which
set the user saw.) Turn the numeric art gates off; do not measure hero, lead, gameplay or
protected-region boxes. Inspect actual final crops in Phase 2. If a label or character is cut by
a seam, adjust the crop and re-export until all requested formats pass; review the affected crops
after each change. A flying ball covering gameplay is never a reason to adjust the crop.

```bash
FLAGS=$(cat production/store-art/concept/export-flags.txt)
# a legacy game (no approved concept): --panels 3 --pop soft --seam-snap off --lead-kind mechanic --art-gate off
"$STORE_PYTHON" tools/store_compose.py triptych --src "$ART_DIR/panorama.png" \
  --out "$PLAY_DIR" --size play $FLAGS
"$STORE_PYTHON" tools/store_compose.py triptych --src "$ART_DIR/panorama.png" \
  --out "$OUT_DIR" --size 1320x2868 $FLAGS
```

Use `--lead-kind character` or `object` as applicable for a legacy game. Export each set from the
same complete source; never resize one set into the other. The approved set keeps the recorded
flags unchanged: they are the crop the user approved. The Play set's 9:16 panels crop about 18%
of a 1.45:1 panorama's height, centred by default, and `--offset-y` (-1 keeps the top, +1 the
bottom) brings a clipped board row or the headroom back without new art. The App Store panels
take back the height the Play crop trimmed. On a 3:2 source their cuts land within a percent of
the width of the Play cuts, so the recorded flags normally fit them too. A 16:9 source moves them
about 3% of the width: a label or character cut in an App Store panel is fixed with that set's own
`--zoom`/`--offset`, never by changing the approved set. The compositor's default gutter remains
suitable for a carousel. A label cut by the gutter needs a crop correction; every panel must still
carry a ball, at least two balls must still cover gameplay, and no ball may cover the player.

**Resolution.** The App Store panels need about 4160×2868 of picture. `tools/gpt_image.py`
renders the panorama natively at `3456x2384`, a 1.2× export. The built-in image tool returns about
1.6 MP (around 1508×1043): a 2.75× enlargement that no sharpening hides, and `triptych` warns
above 1.6×. With such a source, run the **detail pass** on the accepted panorama before
exporting: make a canvas at panel height, then re-render the regions the eye goes to at the
model's full resolution and merge them back in detail mode.

```bash
"$STORE_PYTHON" tools/region_repair.py upscale --src "$ART_DIR/panorama.png" \
  --height 2868 --out "$ART_DIR/panorama-canvas.png"
"$STORE_PYTHON" tools/region_repair.py cut --src "$ART_DIR/panorama-canvas.png" \
  --box X0,Y0,X1,Y1 --context 0.3 --out-dir "$ART_DIR/detail/01-lead"
# Same references as a repair, window.png as the edit target: "re-render this at full detail —
# identical pose, expression, labels, objects, positions, sizes and colours; refine only edges,
# texture and lighting detail".
"$STORE_PYTHON" tools/region_repair.py merge --mode detail \
  --plan "$ART_DIR/detail/01-lead/plan.json" --render "$ART_DIR/detail/01-lead/render.png" \
  --out "$ART_DIR/panorama-canvas-d1.png"
```

Use at most four windows — the lead's head and shoulders first, then the ball labels — and chain
them with `--base`. Detail mode refuses a render whose content drifted from the region it
replaces; still compare identity and every label in `proof.png`. Leave the board out unless you
then verify every cell. The detail pass adds resolution, never content: the approved panorama
must look the same after it, so a window whose render changes a face, a pose or a label is
rejected, not accepted as an improvement. Export both sets from the final canvas, and ship that
canvas as `art/panorama.png`. Never feed a canvas or a detailed canvas to a whole-frame edit.
Record the canvas as `--made derive` and each merge as `--made detail`, each with its `--parent`
— the archive gate walks those records back to the approved file.

## Phase 5 — showcases and feature graphic

Use `showcase` on real captures with the game's fonts/type mood and secondary device framing.
Typical Joker typography is bold/playful, not automatic elegance. Captions describe actual play.
Resolve filenames and words from this game's inventory; honor frame/no-captions/language/count.

**Phone slides sit on the game background.** Pass `--bg "$ART_DIR/shared-background.png"` to
every real-capture showcase, with no `--bg-panel`, `--bg-gutter` or `--bg-subject`. It is the
picture the captured game already shows, composed for a portrait phone with the character whole
inside the frame, so the backdrop needs no panel window to keep the character. Do not add
promotional balls to it; the banner and panorama carry those.

```bash
"$STORE_PYTHON" tools/store_compose.py showcase --shot "$RAW_DIR/03-game-action.png" \
  --bg "$ART_DIR/shared-background.png" --out "$OUT_DIR/store-04.png" \
  --size 1320x2868 --caption "Every Spin Counts" --type-mood playful --pop soft
```

**Fallback with `--keep-runtime-background` only.** Real-capture backdrops show the opening panel
with the whole character. Every phone slide
sits on the panorama's first panel, not the cover-cropped middle: pass `--bg-panel 1` (and the
triptych's `--gutter` as `--bg-gutter` if Phase 4 changed it). Panel 1's cut ignores content, so
a hand, held prop, hair or headwear that crosses into panel 2 would be lost. Read the character's
full horizontal extent once from `art/panorama.png` and pass it as `--bg-subject LEFT,RIGHT`
(fractions of the panorama width). The backdrop then slides right only as far as the whole
character needs. It is a crop parameter, not a gate. A character wider than one panel keeps the
side that crosses the seam and loses some of the side the image edge already crops; the
compositor warns, and a narrower extent (head and the reaching hand) chooses otherwise. Reuse
the same values for the Play set; the compositor recomputes the Play geometry. For an
object/mechanic lead, `--bg-subject` spans the lead object instead.

```bash
"$STORE_PYTHON" tools/store_compose.py showcase --shot "$RAW_DIR/03-game-action.png" \
  --bg "$ART_DIR/panorama.png" --bg-panel 1 --bg-subject 0.00,0.38 \
  --out "$OUT_DIR/store-04.png" \
  --size 1320x2868 --caption "Every Spin Counts" --type-mood playful --pop soft
```

With `--panels 0 --keep-runtime-background`, use `art/multiplier-showcase-bg.png` (Phase 1b)
behind at least one real-capture showcase; keep the capture and runtime background files
unchanged. Compose Play separately in every case.

Feature example:

```bash
"$STORE_PYTHON" tools/store_compose.py banner --keyart "$ART_DIR/long-banner.png" \
  --out "$STORE_DIR/feature-graphic-1024x500.png" \
  --base-out "$ART_DIR/long-banner-source-1024x500.png" --size 1024x500 --pop soft \
  --lead-kind character --banner-layout free --banner-gate off \
  --shot "$RAW_DIR/03-game-action.png" --frame "${DEVICE_FRAME:-ios}"
```

Use the appropriate `--lead-kind` for the game. Review the final banner with the phone once; do
not run focal bounds, gameplay bounds or numeric banner gates.

**The feature graphic is a banner with one phone on the right and no text.** It carries no
title, tagline, logo, wordmark, caption, badge or call to action — not on the left, not over the
scene, not beside the device. The scene fills the frame and the phone sits on the right; the left
is pure illustration with no scrim or copy space. The compositor enforces this: `banner` refuses
`--title`, `--tagline` and `--logo`. The only lettering that may appear is a multiplier-ball
inscription generated by the image model or the game's own UI inside the captured screenshot.
The banner always carries all five multiplier balls flying around the character, and any
character is framed from torso to head with no legs visible. The balls cover some of the
scene's gameplay and may overlap any scene element except the player. Keep all five labels
legible in the shipped graphic, clear of the phone. The phone may cover other parts of the
illustration.

**The feature graphic always carries one device.** `--shot` is required: pick the single
strongest current capture (active play or a win moment, not the menu) and pass it so the compositor
inlays a real phone mockup with that authentic screenshot on the right side of the 1024×500 canvas
inside Play's safe area — a full scene occupies most of the frame and one device sits to the right,
never a bare screenshot rectangle (`--frame none` is refused) or a pasted capture with no scene
around it. `--base-out` keeps the clean device-free scene; `--out` is
the one shipped with the phone composited in. Do not ship a feature graphic with no device.

## Phase 6 — verify, report and package

Run `store_compose.py check --dir "$OUT_DIR" --store appstore` and, when enabled, the equivalent
Play check. Verify RGB PNGs, dimensions, no store-screenshot transparency, file sizes, aspect,
numbering/counts and feature dimensions. In the final passing visual review from Phase 2, confirm the
feature graphic has no title, tagline, logo or other copy and exactly one framed phone on the
right; do not repeat the image review here.
Read `.claude/rules/no-gambling.md`; check captions, metadata and art for gambling controls,
currency, chance-based prizes and misleading scoring claims. Metadata describes the casual
mechanic and records “simulated gambling: no”; rate the content and art. No virtual-currency
disclaimer, age gate or odds disclosure. Interpret decorative objects in context.
The Phase 2 review checks the five ball inscriptions in the final crops. A missing or altered label follows the
Phase 1 correction policy; an unsupported gameplay value does not need one. Balls in the
generated marketing scene must fly in every panel and cover some gameplay while leaving the
player clear, and any character stays framed from torso to head. Keep separate real gameplay
captures authentic.

Recheck runtime-background inventory/hashes/wiring against the baseline taken after campaign art:
normal result UNCHANGED, including a run that made the campaign art itself. If branding changed
Dart, run format/analysis and relevant existing tests, and verify the menu still fits. Compositor
success is not runtime or visual verification.

Write STORE_INFO.md with the original character asset path, the multiplier reference asset path,
the panorama's provenance (the approved concept revision, its SHA-256, approval time and export
flags — or, for a legacy game, that this run made it unapproved), every step it took after
approval (crops, detail windows, any objective-defect repair), the references attached to each
image call this run made (the approved panorama as world context for the banner, icon and emblem),
panel and lower-edge plan, upload order/dimensions/counts, five store-only ball
labels and whether each exists in gameplay, the single visual verdict for balls flying in every
panel and covering gameplay while clearing the player, the character framing verdict (torso to
head, no legs, not standing, not flying), any retry or correction with each accepted scene's
lineage (fresh render, whole-frame edit, region repairs and detail windows), its native size and
export enlargement, whether the game background was
reused from implementation or made in this run (and why, with the runtime files it changed),
whether the banner was made in this run or reused from one in this panorama's world, the
phone-slide backdrop (`shared-background.png` and its SHA-256, or the fallback panel and
`--bg-subject` extent), feature phone capture and no-text result, background guard and compliance notes. Do not require per-sprite audit tables, measured
bounds, numeric gate results or repeated visual verdicts.

Before packaging, copy the finished icon master, listing icon, and transparent emblem into
`$STORE_DIR/branding/` as `app_icon.png`, `store_icon_512.png`, and `emblem.png`. Copy the
lineage ledger in and prove the shipped art against it — the archive gate repeats this check:

```bash
cp production/store-art/lineage.json "$ART_DIR/lineage.json"
python3 tools/art_lineage.py --ledger "$ART_DIR/lineage.json" verify \
  --file "$ART_DIR/long-banner.png" --file "$ART_DIR/panorama.png" \
  --file "$ART_DIR/shared-background.png"   # each file the kit ships
```
 After actual
visual review confirms identity, framing, balls, and accurate gameplay, write
`$STORE_DIR/STORE_DELIVERY.json` with the resolved request count and Play-set choice:

```json
{
  "schema_version": 1,
  "status": "COMPLETE",
  "screenshot_count": 8,
  "play_set": true,
  "visual_review": "PASS",
  "gameplay_review": "PASS",
  "icon_master": "branding/app_icon.png",
  "listing_icon": "branding/store_icon_512.png",
  "emblem": "branding/emblem.png"
}
```

Set STORE_COUNT to the resolved screenshot count. `8` and `true` are defaults, not overrides
of `--count` or `--no-play-set`. Set review PASS
only from the real image review; a blocked or pending scene cannot be declared COMPLETE.

```bash
ARCHIVE_NAME="$PROJECT_NAME-store-$TS.zip"
ARCHIVE_PATH="$STORE_ROOT/$ARCHIVE_NAME"
(cd "$STORE_ROOT" && zip -r "$ARCHIVE_NAME" "$(basename "$STORE_DIR")" -x '*.DS_Store')
unzip -t "$ARCHIVE_PATH"
shasum -a 256 "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
```

Verify ZIP contents: ordered screenshots, feature graphic and branding. Final answer links
ZIP/report, gives composition/counts and actual limitations. Record reusable failures or faster
methods for a separate `/auto-learn` run; do not add that workflow to store-kit delivery.

Create the ZIP after this file exists, then validate the archive itself:

```bash
"$STORE_PYTHON" tools/check_store_kit.py --archive "$ARCHIVE_PATH" --count "$STORE_COUNT" \
  --concept production/store-art/concept/concept.json
# Add --no-play-set when requested. STORE_COUNT is the resolved screenshot count. Drop --concept
# only for a legacy game with no concept record; with it, the gate proves art/panorama.png is
# the approved panorama or descends from it by recorded crops, detail passes and repairs alone.
```

The worker requires a new or changed ZIP whose contents pass this gate. A successful image call,
source-rule check, or CLI exit does not complete store delivery. On failure, preserve the report,
exact runtime facts, attempt prompts and evidence under `production/store-art/failed-delivery/`
as well as the export directory; worker snapshots exclude `project_zip/`. Do not package rejected
art merely to satisfy the archive gate.
