# Campaign prompts — the one source for the banner and the game background

Two runbooks generate the store banner: `/autocreate-finalize` (Phase 10.4, the normal path) and
`/store-screenshots` (only when no valid finalization banner exists). They must send **the same
prompt**. So neither runbook writes one: both render it from the templates below with
`tools/prompt_template.py`, filling only the `{{placeholders}}` with this game's facts, and both
prove the saved prompt with `check` before the image call. A reworded, shortened or "adapted"
sentence fails the check; so does an unfilled placeholder.

The banner templates are the `/store-screenshots` banner contract (Phase 1's composition rules,
lower edge, multiplier balls, first-prompt requirements and 1a) written out literally. Changing a
banner rule means changing it here, and it changes for both runbooks at once.

```bash
TPL=.claude/skills/store-screenshots/references/campaign-prompts.md
python3 tools/prompt_template.py list --template "$TPL"
python3 tools/prompt_template.py render --template "$TPL" --id banner-character \
  --set environment="..." --set character="..." --set gameplay="..." \
  --set label_color="..." --set accent="..." --set ball_fx="..." \
  --set objects="..." --set foreground_pieces="..." --set palette="..." \
  --out production/store-art/banner-prompt.txt
python3 tools/prompt_template.py check --template "$TPL" --id banner-character \
  --prompt production/store-art/banner-prompt.txt   # must print PASS before generating
```

## Choosing a template

| Game | Banner | Game background |
|---|---|---|
| Character lead (`lead_kind: character`) | `banner-character` | `background-character` |
| Object lead (crown, coin, capsule) | `banner-object` | `background-object` |
| Mechanic lead (peg clear, target throw) | `banner-object` | `background-mechanic` |

Never render a character template for a game with no living character in its concept and shipped
inventory, and never render an object/mechanic template to avoid drawing a character the game has.

## Filling placeholders

When runtime capture metadata supplies board rows, symbols, or selected cells, derive those
facts directly from the recorded state and compare them with the capture. Do not hand-copy a
long cell map from an earlier prompt. Missing state evidence requires a new authentic capture,
not invented selection indices. A passing template check verifies wording, not generated art.

A value names this game's own subjects, in plain words, from the concept, Design DNA, asset
manifest, the reference contract (`design/reference-contract.md`) and the real gameplay capture:

- `environment` — the setting as the game's background and art direction describe it; for a
  reference game, the reference's setting, read off the source image.
- `character` — who the lead is and the traits that identify them (costume colours and pattern,
  headwear, face) — the same words as the reference ledger.
- `lead` — the lead object, or for a mechanic lead the angled gameplay surface.
- `gameplay` — the real mechanic, its topology and the state in the capture (e.g. "a 7×8 match board
  of jester, crown, lute and gem tiles with a cleared three-tile match").
- `objects` — 4–7 of the game's own shipped objects in left-to-right order.
- `foreground_pieces` — the game's own tiles, gems, balls or decorative objects; never money.
- `label_color`, `accent`, `ball_fx` — the warm display colour for the ball numerals, the
  accent rim-light colour, and the halo/sparkle ring/energy flare taken from the game's FX.
- `palette` — the game's authentic palette and light sources.
- `focus` (mechanic background only) — the non-board motif that carries the upper half, taken
  from the game's own objects and light (never a board, a character or a mascot).

Values are descriptions, not instructions: no "ignore", no extra rules, no text for the image to
letter. The renderer rejects a value over 500 characters.

## Attachments and sizes

| Template | Attach, in order | Size |
|---|---|---|
| `banner-*` | the original character asset (identity authority; character lead only), the multiplier reference (ball model), the real gameplay capture (context only), visible shipped sprites, the reference sources from `design/reference-contract.md` or matching previews | `3840x1872` |
| `background-*` | the original character asset or lead object asset (identity authority; not for mechanic), the accepted banner (world context — not a character reference), the game's original (pre-campaign) background — never an earlier campaign background, the reference sources | `1328x2880` |

The accepted banner is never the character reference: the character's identity comes only from
the shipped asset. No call attaches an earlier version of the picture it makes — a banner is never
rendered from the previous banner, a background never from the previous background
([art-lineage.md](../../../docs/art-lineage.md)). Respect the transport's image limit by the rules in
`.claude/docs/visual-context.md` → "Image reference transport preflight"; never drop the
identity asset to make room.

## Banner templates

```prompt banner-character
One continuous, fully illustrated horizontal key-art banner for a mobile casual game with premium key-art visuals, set in the
game's own world: {{environment}}. Reproduce the supplied original character asset faithfully: it
is the identity authority for the face, silhouette, costume and colors, and the other images are
context. The main character, {{character}}, appears large on the left, framed as a torso-to-head
bust: the bottom edge of the image or the large foreground objects cut its body through the
torso, so no legs, knees, hips or feet are visible anywhere. The character is not standing full
length and is not flying, floating or leaping; its cut torso rises from the bottom of the image or
from behind the foreground objects. Leave visible open space above the entire head and headwear,
at least 2% of the image height. Beside the character, the game's real gameplay is part of the
scene at a three-quarter/3D angle: {{gameplay}}. Match the attached gameplay capture's mechanic,
topology, symbols and state; the capture is context only and never appears as a flat pasted
screenshot. The environment runs edge to edge, and the right third continues the scene with
background, housing and foreground running through it, but no face or decisive symbol sits in
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
One continuous, fully illustrated horizontal key-art banner for a mobile casual game with premium key-art visuals, set in the
game's own world: {{environment}}. There is no character in this game: do not add a person, hand,
animal, mascot, deity or player silhouette anywhere. The lead, {{lead}}, appears large on the
left at a three-quarter/3D angle, reproduced faithfully from the attached shipped asset. Beside
it, the game's real gameplay is part of the scene at a three-quarter/3D angle: {{gameplay}}. Match
the attached gameplay capture's mechanic, topology, symbols and state; the capture is context only
and never appears as a flat pasted screenshot. The environment runs edge to edge, and the right
third continues the scene with background, housing and foreground running through it, but no
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

The game background is the picture the player lives inside and the picture behind every phone on
the store's real-capture slides. It is a runtime asset, so it carries no multiplier balls, no
lettering, no board and no UI: the live game draws the board and controls over it, and a
promotional `x100` behind real gameplay would read as a payout claim. It keeps the campaign's
world and, for a character-led game, the character — whole, inside the phone frame.

```prompt background-character
One fully illustrated portrait background for a mobile game screen held upright, 9:19.5, set in
the world of the attached banner: the same environment, palette, lighting, materials and depth,
in a new composition made for a phone screen: {{environment}}. Reproduce the supplied original
character asset faithfully; the banner is world context, not the character reference. The main
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
saturated. Keep the environment luminous but subordinate to the character through softer focus
and lower local contrast. Preserve the source asset colors; avoid a global color wash, muddy
shadows, flat lighting and all-over haze.
```

```prompt background-object
One fully illustrated portrait background for a mobile game screen held upright, 9:19.5, set in
the world of the attached banner: the same environment, palette, lighting, materials and depth,
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
Keep shadows rich in color and midtones saturated. Keep the environment luminous but subordinate
to the lead through softer focus and lower local contrast. Preserve the source asset colors; avoid
a global color wash, muddy shadows, flat lighting and all-over haze.
```

```prompt background-mechanic
One fully illustrated portrait background for a mobile game screen held upright, 9:19.5, set in
the world of the attached banner: the same environment, palette, lighting, materials and depth,
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
