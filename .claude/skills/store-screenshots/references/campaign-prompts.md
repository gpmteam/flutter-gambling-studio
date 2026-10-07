# Campaign prompts — the one source for the panorama, the game background and the banner

Every campaign picture is rendered from a template in this file, never from a prompt an agent
wrote or "adapted" itself. Two runbooks can make the same picture, and they must send **the same
prompt**: both render it with `tools/prompt_template.py`, filling only the `{{placeholders}}`
with this game's facts, and both prove the saved prompt with `check` before the image call. A
reworded, shortened or "adapted" sentence fails the check; so does an unfilled placeholder.

| Picture | Made by | Made again by |
|---|---|---|
| Panorama (the concept carousel) | `/autocreate` Phase 3.9 ([concept-panorama.md](concept-panorama.md)) — before any game code, for the user to approve | `/store-screenshots`, only for a game made before the approval gate |
| Game background | `/autocreate-implement` Phase 4.0 ([campaign-art.md](campaign-art.md)) — right after approval, in the approved panorama's world | `/store-screenshots`, only when the handoff is missing or stale |
| Banner | `/store-screenshots` ([campaign-art.md](campaign-art.md)) — in the approved panorama's world | — |

The panorama templates are the `/store-screenshots` panorama contract (Phase 1's composition
rules, lower edge, multiplier balls and first-prompt requirements) written out literally; the
banner templates are the same contract for the horizontal banner. Changing a rule means changing
it here, and it changes for every runbook at once.

```bash
TPL=.claude/skills/store-screenshots/references/campaign-prompts.md
python3 tools/prompt_template.py list --template "$TPL"
python3 tools/prompt_template.py render --template "$TPL" --id panorama-character \
  --set environment="..." --set character="..." --set gameplay="..." --set panels="three" \
  --set label_color="..." --set accent="..." --set ball_fx="..." \
  --set objects="..." --set foreground_pieces="..." --set palette="..." \
  --out production/store-art/concept/panorama-prompt.txt
python3 tools/prompt_template.py check --template "$TPL" --id panorama-character \
  --prompt production/store-art/concept/panorama-prompt.txt   # must print PASS before generating
```

## Choosing a template

| Game | Panorama | Game background | Banner |
|---|---|---|---|
| Character lead (`lead_kind: character`) | `panorama-character` | `background-character` | `banner-character` |
| Object lead (crown, coin, capsule) | `panorama-object` | `background-object` | `banner-object` |
| Mechanic lead (peg clear, target throw) | `panorama-object` | `background-mechanic` | `banner-object` |

Never render a character template for a game with no living character in its concept and shipped
inventory, and never render an object/mechanic template to avoid drawing a character the game has.

## Filling placeholders

When runtime capture metadata supplies board rows, symbols, or selected cells, derive those
facts directly from the recorded state and compare them with the capture. Before the game exists
(the concept panorama), they come from the concept, the level data and the layout draft
(`store_compose.py layout-draft`) instead. Do not hand-copy a long cell map from an earlier
prompt, and never invent selection indices. A passing template check verifies wording, not
generated art.

A value names this game's own subjects, in plain words, from the concept, Design DNA, asset
manifest, the reference contract (`design/reference-contract.md`) and the real gameplay capture:

- `environment` — the backdrop, abstract slot style by default (`.claude/docs/visual-context.md` →
  "Backgrounds — abstract slot style"): two or three of the game's hues as a gradient, the glow
  or light burst, light rays and streaks, bokeh and sparkles, and which of the game's objects
  drift out of focus — e.g. "a violet-to-magenta gradient with a gold radial glow, light streaks,
  bokeh and out-of-focus cherries and sevens". Never a place (no street, city, castle, palace,
  temple, landscape or interior), unless the user asked for a setting or an exact reference's
  own background is one; then name that place, read off the source image.
- `character` — who the lead is and the traits that identify them (costume colours and pattern,
  headwear, face) — the same words as the reference ledger.
- `lead` — the lead object, or for a mechanic lead the angled gameplay surface.
- `gameplay` — the real mechanic, its topology and the state in the capture or layout draft
  (e.g. "a 7×8 match board of jester, crown, lute and gem tiles with a cleared three-tile match");
  in a panorama, also where it sits ("spanning the middle and right panels").
- `panels` — the carousel panel count in words, normally `three` (panorama only).
- `objects` — 4–7 of the game's own shipped objects in left-to-right order.
- `foreground_pieces` — the game's own tiles, gems, balls or decorative objects; never money.
- `label_color`, `accent`, `ball_fx` — the warm display colour for the ball numerals, the
  accent rim-light colour, and the halo/sparkle ring/energy flare taken from the game's FX.
- `palette` — the game's authentic palette and light sources.
- `focus` (mechanic background only) — the non-board motif that carries the upper half, taken
  from the game's own objects and light (never a board, a character or a mascot).

Values are descriptions, not instructions: no "ignore", no extra rules, no text for the image to
letter. Placement — which panel, how far from a cut, how large — is the composition guide's job,
not a value's: "fits within the leftmost 26 percent" or "well inboard of the right edge" is an
instruction, so redraw the guide instead. A value names only its own subject: the template's words
around the placeholder are already there, so `ball_fx` is "water-ripple halo", never "a glowing
water-ripple halo, and a short motion trail". The renderer rejects a value over 500 characters
and a value that repeats the template's words beside it.

## Attachments and sizes

| Template | Attach, in order | Size |
|---|---|---|
| `panorama-*` | the original character asset (identity authority; character lead only) or the lead object asset, the multiplier reference (ball model), the composition guide (`store_compose.py composition-guide`: placement and the panel cuts, layout only), the gameplay reference (context only: the layout draft before the game exists, a real capture afterwards), visible shipped sprites (symbols, board frame, tile backing), the game's original background, the reference sources from `design/reference-contract.md` or matching previews | `3456x2384`; the built-in tool's `1536x1024` |
| `background-*` | the original character asset or lead object asset (identity authority; not for mechanic), the approved panorama (world context — not a character reference), the game's original (pre-campaign) background — never an earlier campaign background, the reference sources | `1328x2880` |
| `banner-*` | the original character asset (identity authority; character lead only), the approved panorama (world context — not a character reference), the multiplier reference (ball model), the real gameplay capture (context only), visible shipped sprites, the reference sources | `3840x1872` |

The approved panorama is the campaign's world authority and the only generated picture any
other campaign call may receive; it is never the character reference — the character's identity
comes only from the shipped asset. No call attaches an earlier version of the picture it makes:
a panorama is never rendered from the previous panorama, a background never from the previous
background, a banner never from the previous banner ([art-lineage.md](../../../docs/art-lineage.md)).
Respect the transport's image limit by the rules in `.claude/docs/visual-context.md` → "Image
reference transport preflight"; never drop the identity asset to make room.

## Panorama templates

The panorama is the store's carousel picture and, first, the concept the user approves before a
line of game code exists. Its gameplay is the example the finished game is built to look like
(`gameplay-sample.md`), so it is rendered from the game's real symbol, board and tile assets in
the planned topology.

```prompt panorama-character
One continuous, fully illustrated horizontal game panorama for a mobile casual game with premium
key-art visuals, composed to be cut into {{panels}} side-by-side portrait store screenshots that
together read as one complete picture, set against the game's backdrop: {{environment}}. Compose it
on the attached composition guide, a layout diagram rather than art: its red bands mark where the
picture is cut into the {{panels}} portrait panels and its darkened edges are cropped away, so keep
every face, hand, held object, ball label and decisive symbol out of both, and place the
character, the game field, the five balls and the lower-edge objects where the guide places them;
never draw the guide's bands, outlines or flat background into the scene. Reproduce
the supplied original character asset faithfully: it is the identity authority for the face,
silhouette, costume and colors, and the other images are context. The main character,
{{character}}, appears large on the first portrait panel at the left, framed as a torso-to-head
bust: the bottom edge of the image or the large foreground objects cut its body through the
torso, so no legs, knees, hips or feet are visible anywhere. The character is not standing full
length and is not flying, floating or leaping; its cut torso rises from the bottom of the image or
from behind the foreground objects. Leave visible open space above the entire head and headwear,
at least 2% of the image height, and keep the head, hands and anything the character holds clear
of the first panel boundary. The game's real gameplay is part of the scene at a three-quarter/3D
angle: {{gameplay}}. Match the attached gameplay reference's mechanic, topology, symbols and
state, and render the board housing, tiles and symbols from the attached game assets; this is the
game's field as players will see it, so it must be readable, complete and believable as a real
game, and the reference is context only and never appears as a flat pasted picture. Keep faces,
ball labels and decisive symbols away from the panel boundaries; the board and the backdrop may continue across them. Paint five multiplier balls modeled on the attached ball asset, all
required, clearly airborne and flying around the character and across the scene at varied
heights, depths and horizontal positions, with at least one ball in each of the {{panels}}
portrait panels and none resting on an object. Letter each ball on its face with exactly one of
these inscriptions, each used once: "x5", "x10", "x25", "x50", "x100". Make every label big,
chunky 3D display numerals in {{label_color}} with a dark outline and inner highlight, filling
most of the ball face and following its curve. Light the balls with the scene: glossy specular
highlights, {{accent}} rim light, a glowing {{ball_fx}}, and a short motion trail. At least two
balls fly in front of the board and cover part of it. The balls may cover any other scene
element; keep every ball clear of the character's silhouette. No other text, title, logo,
wordmark, tagline, device, UI or empty copy space anywhere in the image; the panorama must look
finished on its own. Across the whole lower edge, place about 5–7 of the game's own objects very
large and close to the camera: {{objects}}, overlapping each other in depth and cropped by the
bottom edge, filling about the lower quarter to third of the image. Under and between them, a
continuous glittering layer of {{foreground_pieces}} runs the full width. No floor, fabric,
tabletop, podium or drape, and no miniature clutter. Give the scene vivid, high-impact
mobile-game key-art lighting from the game's authentic palette: {{palette}}. Separate warm and
cool hues, add clean specular highlights to polished materials, theme-appropriate rim light on
primary subjects, and reflected color between nearby objects. Use small star glints selectively
and localized bloom around real light sources or verified magical effects. Keep shadows rich in
color, midtones saturated, and a few highlights near white. Keep the background luminous but
subordinate through softer focus and lower local contrast. Preserve the source asset colors;
avoid a global color wash, muddy shadows, flat lighting, matte gems and all-over haze. The scene
should look exciting and premium before compositor grading.
```

```prompt panorama-object
One continuous, fully illustrated horizontal game panorama for a mobile casual game with premium
key-art visuals, composed to be cut into {{panels}} side-by-side portrait store screenshots that
together read as one complete picture, set against the game's backdrop: {{environment}}. Compose it
on the attached composition guide, a layout diagram rather than art: its red bands mark where the
picture is cut into the {{panels}} portrait panels and its darkened edges are cropped away, so keep
every ball label and decisive symbol out of both, and place the lead, the game field, the five
balls and the lower-edge objects where the guide places them; never draw the guide's bands,
outlines or flat background into the scene. There is no
character in this game: do not add a person, hand, animal, mascot, deity or player silhouette
anywhere. The lead, {{lead}}, reproduced faithfully from the attached shipped asset, frames the
action. The game's real gameplay leads the first two portrait panels at a three-quarter/3D angle,
either as a readable sample of play in each or as one continuous angled play surface with
meaningful play visible in both: {{gameplay}}. Match the attached gameplay reference's mechanic,
topology, symbols and state, and render the board housing, tiles and symbols from the attached
game assets; this is the game's field as players will see it, so it must be readable, complete
and believable as a real game, and the reference is context only and never appears as a flat
pasted picture. Keep ball labels and decisive symbols away from the panel boundaries; the board and the backdrop may continue across them. Paint five multiplier balls modeled on the attached
ball asset, all required, clearly airborne and flying around the lead and across the scene at
varied heights, depths and horizontal positions, with at least one ball in each of the
{{panels}} portrait panels and none resting on an object. Letter each ball on its face with
exactly one of these inscriptions, each used once: "x5", "x10", "x25", "x50", "x100". Make every
label big, chunky 3D display numerals in {{label_color}} with a dark outline and inner highlight,
filling most of the ball face and following its curve. Light the balls with the scene: glossy
specular highlights, {{accent}} rim light, a glowing {{ball_fx}}, and a short motion trail. At
least two balls fly in front of the board and cover part of it. The balls may cover any other
scene element. No other text, title, logo, wordmark, tagline, device, UI or empty copy space
anywhere in the image; the panorama must look finished on its own. Across the whole lower edge,
place about 5–7 of the game's own objects very large and close to the camera: {{objects}},
overlapping each other in depth and cropped by the bottom edge, filling about the lower quarter to
third of the image. Under and between them, a continuous glittering layer of {{foreground_pieces}}
runs the full width. No floor, fabric, tabletop, podium or drape, and no miniature clutter. Give
the scene vivid, high-impact mobile-game key-art lighting from the game's authentic palette:
{{palette}}. Separate warm and cool hues, add clean specular highlights to polished materials,
theme-appropriate rim light on primary subjects, and reflected color between nearby objects. Use
small star glints selectively and localized bloom around real light sources or verified magical
effects. Keep shadows rich in color, midtones saturated, and a few highlights near white. Keep the
background luminous but subordinate through softer focus and lower local contrast. Preserve the
source asset colors; avoid a global color wash, muddy shadows, flat lighting, matte gems and
all-over haze. The scene should look exciting and premium before compositor grading.
```

## Banner templates

```prompt banner-character
One continuous, fully illustrated horizontal key-art banner for a mobile casual game with
premium key-art visuals, set in the world of the attached panorama — the same backdrop, palette, lighting, board housing, lower-edge treatment and multiplier-ball look — in a new
horizontal composition: {{environment}}. Reproduce the supplied original character asset
faithfully: it is the identity authority for the face, silhouette, costume and colors; the
panorama is world context, not the character reference, and the other images are context. The
main character, {{character}}, appears large on the left, framed as a torso-to-head
bust: the bottom edge of the image or the large foreground objects cut its body through the
torso, so no legs, knees, hips or feet are visible anywhere. The character is not standing full
length and is not flying, floating or leaping; its cut torso rises from the bottom of the image or
from behind the foreground objects. Leave visible open space above the entire head and headwear,
at least 2% of the image height. Beside the character, the game's real gameplay is part of the
scene at a three-quarter/3D angle: {{gameplay}}. Match the attached gameplay capture's mechanic,
topology, symbols and state; the capture is context only and never appears as a flat pasted
screenshot. The backdrop runs edge to edge, and the right third continues the scene with backdrop, housing and foreground running through it, but no face or decisive symbol sits in
that right third. Paint five multiplier balls modeled on the attached ball asset, all required,
clearly airborne and flying around the character and across the gameplay at varied heights,
depths and horizontal positions, none resting on an object and none in the right third. Letter
each ball on its face with exactly one of these inscriptions, each used once: "x5", "x10", "x25",
"x50", "x100". Make every label big, chunky 3D display numerals in {{label_color}} with a dark
outline and inner highlight, filling most of the ball face and following its curve. Light the
balls with the scene: glossy specular highlights, {{accent}} rim light, a glowing {{ball_fx}}, and
a short motion trail. At least two balls fly in front of the board and cover part of it. The balls
may cover any other scene element; keep every ball clear of the character's silhouette. No other
text, title, logo, wordmark, tagline, device, UI or empty copy space anywhere in the image; the
banner must look finished on its own. Across the whole lower edge, place about 5–7 of the game's
own objects very large and close to the camera: {{objects}}, overlapping each other in depth and
cropped by the bottom edge, filling about the lower quarter to third of the image. Under and
between them, a continuous glittering layer of {{foreground_pieces}} runs the full width. No floor, fabric,
tabletop, podium or drape, and no miniature clutter. Give the scene vivid, high-impact mobile-game
key-art lighting from the game's authentic palette: {{palette}}. Separate warm and cool hues, add
clean specular highlights to polished materials, theme-appropriate rim light on primary subjects,
and reflected color between nearby objects. Use small star glints selectively and localized bloom
around real light sources or verified magical effects. Keep shadows rich in color, midtones
saturated, and a few highlights near white. Keep the background luminous but subordinate through
softer focus and lower local contrast. Preserve the source asset colors; avoid a global color
wash, muddy shadows, flat lighting, matte gems and all-over haze. The scene should look exciting
and premium before compositor grading.
```

```prompt banner-object
One continuous, fully illustrated horizontal key-art banner for a mobile casual game with
premium key-art visuals, set in the world of the attached panorama — the same backdrop, palette, lighting, board housing, lower-edge treatment and multiplier-ball look — in a new
horizontal composition: {{environment}}. There is no character in this game: do not add a person, hand,
animal, mascot, deity or player silhouette anywhere. The lead, {{lead}}, appears large on the
left at a three-quarter/3D angle, reproduced faithfully from the attached shipped asset. Beside
it, the game's real gameplay is part of the scene at a three-quarter/3D angle: {{gameplay}}. Match
the attached gameplay capture's mechanic, topology, symbols and state; the capture is context only
and never appears as a flat pasted screenshot. The backdrop runs edge to edge, and the right third continues the scene with backdrop, housing and foreground running through it, but no
decisive symbol sits in that right third. Paint five multiplier balls modeled on the attached ball
asset, all required, clearly airborne and flying around the lead and across the gameplay at
varied heights, depths and horizontal positions, none resting on an object and none in the right
third. Letter each ball on its face with exactly one of these inscriptions, each used once: "x5",
"x10", "x25", "x50", "x100". Make every label big, chunky 3D display numerals in {{label_color}}
with a dark outline and inner highlight, filling most of the ball face and following its curve.
Light the balls with the scene: glossy specular highlights, {{accent}} rim light, a glowing
{{ball_fx}}, and a short motion trail. At least two balls fly in front of the board and cover part
of it. The balls may cover any other scene element. No other text, title, logo, wordmark, tagline,
device, UI or empty copy space anywhere in the image; the banner must look finished on its own.
Across the whole lower edge, place about 5–7 of the game's own objects very large and close to the
camera: {{objects}}, overlapping each other in depth and cropped by the bottom edge, filling about
the lower quarter to third of the image. Under and between them, a continuous glittering layer of
{{foreground_pieces}} runs the full width. No floor, fabric, tabletop, podium or drape, and no miniature
clutter. Give the scene vivid, high-impact mobile-game key-art lighting from the game's authentic
palette: {{palette}}. Separate warm and cool hues, add clean specular highlights to polished
materials, theme-appropriate rim light on primary subjects, and reflected color between nearby
objects. Use small star glints selectively and localized bloom around real light sources or
verified magical effects. Keep shadows rich in color, midtones saturated, and a few highlights
near white. Keep the background luminous but subordinate through softer focus and lower local
contrast. Preserve the source asset colors; avoid a global color wash, muddy shadows, flat
lighting, matte gems and all-over haze. The scene should look exciting and premium before
compositor grading.
```

## Game background templates

The game background is the backdrop behind the whole game and behind every phone on the store's real-capture slides. It is rendered right after the user approves the concept
carousel, in the approved panorama's world. It is a runtime asset, so it carries no multiplier balls, no
lettering, no board and no UI: the live game draws the board and controls over it, and a
promotional `x100` behind real gameplay would read as a payout claim. It keeps the campaign's
world and, for a character-led game, the character — whole, inside the phone frame.

```prompt background-character
One fully illustrated portrait background for a mobile game screen held upright, 9:19.5, set in
the world of the attached panorama: the same backdrop, palette, lighting and materials,
in a new composition made for a phone screen: {{environment}}. Reproduce the supplied original
character asset faithfully; the panorama is world context, not the character reference. The main
character, {{character}}, is large and fits entirely inside the frame: the whole head, hair and
headwear, the face, both shoulders, both arms and hands, and anything the character holds stay
inside the left, right and top edges, with clear open space above the headwear and on both sides.
Nothing of the head, headwear, shoulders, hands or held objects is cut by an edge of the image.
Frame the character as a torso-to-head bust facing the viewer, occupying roughly the upper half of
the image with the face in the upper third. The torso is cut at about the middle of the image by a
large mound of the game's own objects and glittering {{foreground_pieces}} that rises from the bottom edge,
so no legs, knees, hips or feet are visible; the character is not standing full length and is not
flying, floating or leaping. The mound holds {{objects}}, large and close to the camera,
overlapping each other in depth and cropped by the bottom edge. No floor, fabric, tabletop,
podium or drape. Keep the lower half calmer, softer and lower in contrast than the character: in
the game, the live board and its controls are drawn over the middle and lower part of this image.
Do not paint a game board, reels, grid, cards, table, buttons, panels, HUD, frames, phones or
devices, and no text, letters, numbers, logos, labelled coins or multiplier balls anywhere. Light
it as vivid mobile-game key art from the game's authentic palette: {{palette}}. Separate warm and
cool hues, add clean specular highlights to polished materials, theme-appropriate rim light on the
character, and reflected color between nearby objects. Keep shadows rich in color and midtones
saturated. Keep the backdrop luminous but subordinate to the character through softer focus
and lower local contrast. Preserve the source asset colors; avoid a global color wash, muddy
shadows, flat lighting and all-over haze.
```

```prompt background-object
One fully illustrated portrait background for a mobile game screen held upright, 9:19.5, set in
the world of the attached panorama: the same backdrop, palette, lighting and materials,
in a new composition made for a phone screen: {{environment}}. There is no character in this
game: do not add a person, hand, animal, mascot, deity or player silhouette anywhere. The lead,
{{lead}}, reproduced faithfully from the attached shipped asset, is large and whole in the upper
half of the image, inside the left, right and top edges with clear open space around it; nothing
of it is cut by an edge of the image. A large mound of the game's own objects and glittering
{{foreground_pieces}} rises from the bottom edge: {{objects}}, large and close to the camera, overlapping
each other in depth and cropped by the bottom edge. No floor, fabric, tabletop, podium or drape.
Keep the lower half calmer, softer and lower in contrast than the lead: in the game, the live board
and its controls are drawn over the middle and lower part of this image. Do not paint a game
board, reels, grid, cards, table, buttons, panels, HUD, frames, phones or devices, and no text,
letters, numbers, logos, labelled coins or multiplier balls anywhere. Light it as vivid
mobile-game key art from the game's authentic palette: {{palette}}. Separate warm and cool hues,
add clean specular highlights to polished materials, and reflected color between nearby objects.
Keep shadows rich in color and midtones saturated. Keep the backdrop luminous but subordinate
to the lead through softer focus and lower local contrast. Preserve the source asset colors; avoid
a global color wash, muddy shadows, flat lighting and all-over haze.
```

```prompt background-mechanic
One fully illustrated portrait background for a mobile game screen held upright, 9:19.5, set in
the world of the attached panorama: the same backdrop, palette, lighting and materials,
in a new composition made for a phone screen: {{environment}}. There is no character in this
game: do not add a person, hand, animal, mascot, deity or player silhouette anywhere. The upper
half is carried by {{focus}}, whole inside the edges of the image. A soft band of the game's own
objects and glittering {{foreground_pieces}} runs along the bottom edge: {{objects}}, overlapping each
other in depth and cropped by the bottom edge. No floor, fabric, tabletop, podium or drape. Keep
the middle and lower part calm, soft and lower in contrast: in the game, the live board and its
controls are drawn over it. Do not paint a game board, pegs, buckets, reels, grid, cards, table,
buttons, panels, HUD, frames, phones or devices, and no text, letters, numbers, logos, labelled
coins or multiplier balls anywhere. Light it as vivid mobile-game key art from the game's
authentic palette: {{palette}}. Separate warm and cool hues, add clean specular highlights to
polished materials, and reflected color between nearby objects. Keep shadows rich in color and
midtones saturated. Preserve the source asset colors; avoid a global color wash, muddy shadows,
flat lighting and all-over haze.
```
