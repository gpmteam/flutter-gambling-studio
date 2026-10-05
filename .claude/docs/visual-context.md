# Visual context — concepts, assets, and store art

Use this contract when proposing a game, generating its assets, or composing its storefront.
The user's brief and an existing game's actual mechanics and Design DNA are authoritative.

**The studio look.** Games may look like premium casino key art — jewel-toned symbols, gold trim,
glossy gems, jokers, crowns, deities, fruit-and-seven symbol families — or reproduce a reference
exactly. That is an art direction, not a mechanic: every game plays as a casual skill game scored
in points (`.claude/docs/game-categories.md`, `.claude/rules/no-gambling.md`). A slot preview's
symbols become tiles, its reel frame becomes the board frame, and its reel strips become column
backing; nothing about it spins for an outcome.
For matching new-game requests, inspect the relevant previews in `examples-games/` by default
and read `.claude/docs/game-concept-examples.md`. They are visual references, not runtime assets
or complete game specifications. A missing reference does not block an unrelated concept.

Whether a request is a reference request is decided by `tools/reference_detect.py` (see
`game-concept-examples.md` → "Detecting a reference request") and recorded in
`design/reference-contract.md`; images the user attached are references on the same footing as the
local previews. `/autocreate` requests named **Book of Ra**, **Joker**, **Joker Jewels**, **Shining
Crown**, or **Plinko** must use the exact local reference mapping in
`game-concept-examples.md`, on the `--from-concept` path as well; do not replace it with a generic
category reference. Recreate what the preview shows: theme, character, symbol cast, palette,
frame and composition are matched, not reinterpreted. The full rule is "How close to the
reference — match it" in `game-concept-examples.md`, and it governs the whole look of the concept.
The mechanic is the family's casual "Build as" entry (or the user's casual mechanic, or the
translation of a gambling ask) — never the casino gameplay a preview shows. Follow the production
limits in `game-concept-examples.md`; suitable source pixels can be reused, while branding and the
casino interface do not carry over. Shining Crown and Plinko are object/mechanic-led and must not
gain an invented main character or mascot.
**Joker** and **Joker Jewels** are two different entries: Joker Jewels resolves to every file in
the `examples-games/joker-jewels/` folder and to the swap match-3 board, never to the plain Joker
row's tap-blast board.

## Decide the visual lead before generating

Record `lead_kind: character | object | mechanic`, the lead's identity and runtime role,
reference paths, traits borrowed, original adaptations, board topology, and supported combo
markers in `design/gdd/game-concept.md`. Carry those decisions into `design/art-direction.md`,
the asset manifest, generation prompts, and `STORE_BRIEF.md`.

Once the assets exist, record the lead's own file as `Lead asset: <path>` in the concept (or the
art direction). Separately record `menu_role: dominant | supporting | absent` from the main
menu's M recipe. `lead_kind` controls storefront composition; it does not force every runtime
menu into the same centerpiece layout. Character-led references often choose `dominant`, while a
poster, map, or progression hub may choose `supporting` or `absent` with a concrete reason. See
`quality-bar.md` §1 and V19 in `.claude/skills/emulator-test/SKILL.md`.

| Lead | When it fits | Default storefront direction |
|---|---|---|
| Character | Joker, the Book of Ra explorer, chicken, another actual character or animal mascot | Recognizable large character on the first panel; action may occupy any remaining space or span panels |
| Object | Crown, jewel, treasure chest, relic, the top tier of a merge chain is the visual star | Let that asset and the real mechanic drive the composition; when the game has no living character, slides 1–2 show angled authentic gameplay and introduce no person or mascot |
| Mechanic | Peg field and ball trails, a link-chain board, a stacking tower is the attraction | Lead with active play; a board or trajectory may extend through all panels |

A chicken is a character even though it is not a person. A crown or gem is an object even if
someone calls it the game's “hero.” Do not invent a mascot just to fill a template. Conversely,
do include a requested character in the concept, asset plan, and relevant in-game states rather
than inventing it only for the store. Existing games retain their established lead.

## Reference-led original assets

For a reference request (a mapped family or user attachments), rebuild the source's asset family
object for object: the same subjects,
costume, pose, materials, colours, light and rendering style, at runtime resolution. Inspect every
mapped image at full size and make a reference ledger for the character, each symbol, board,
background, UI materials and composition. Supply the relevant source image(s) directly to a
reference-capable image tool at high fidelity; a written description alone is insufficient when
the source is available. The local `tools/gpt_image.py edit --image <reference> --fidelity high`
path accepts JPEG and PNG. If the tool caps input count or bytes, select the relevant references
for each asset and document which ones were used; never silently drop a required identity image.
Use the resulting coherent assets in the real game, then compare runtime screenshots beside the
source at the phone sizes. Fix mismatched character traits, symbol identity, background, frame
and palette before declaring the asset set complete. See "How close to the reference —
match it" in `game-concept-examples.md`.

Directly reuse an example image or a cleanly isolated element when its pixels are suitable for
the intended runtime size and the requested reproduction; preserve provenance in the manifest.
Do not turn a flattened screenshot with UI, title, bet panel or payout text into a background or
sprite.
When isolation would be visibly poor, regenerate with the source image as a visual input and
compare again. For an unmapped concept, derive the visual style from its brief and Design DNA.

2D and 2.5D are both valid. Record the chosen depth and finish in the Design DNA. Match a mapped
reference's linework, shading, texture and light; do not convert 2D art into generic glossy 2.5D.
For an original game, choose the finish that serves the concept and use it consistently.
Build the actual runtime set first; store generation then uses those shipped assets as identity
references. A marketing reference cannot override the real game's colors, symbols, or topology.

### Joker expression

The default Joker is a mischievous, slightly vicious trickster: sharp confident grin, angled
eyebrows, lively eyes, pointed jester cap with bells, bold contrasting costume, and a theatrical
gesture. Favor impish swagger over a polite elegant courtier. Keep it playful and readable;
avoid horror, gore, creepy realistic skin, monstrous teeth, or frightening expressions.
Rich fabrics and gold trim can support the character without making elegance its personality.

### Board topology

The mechanic sets the board, not the preview's reels. An unspecified match game (G1) defaults to
a **7 columns × 8 rows** board; a named preview-mapped family takes the "Build as" topology from
`game-concept-examples.md` (Joker and Joker Jewels 7×8, Shining Crown 4×4, Book of Ra
a layered tile pile with a 7-slot tray, Plinko a tilted peg field). Save the topology in the
concept and the balance config; implementation, board assets, runtime screenshots, and marketing
must agree. A user's explicit grid keeps its dimensions when the mechanic can be played on it.
Do not change a shipped game to satisfy a marketing default.

### Combo markers

Prefer prominent `x2`, `x5` and `x10` combo badges in runtime feedback when the scoring model has
a combo multiplier on points (a long chain, a cascade, a multi-line clear). Badge material and
edging follow the game: royal jewel medallion, playful jester token, charged lightning orb, and so
on. A marker always shows a points multiplier the player just *earned by play* — never a random
multiplier, never a prize, never anything convertible. Record each marker's exact scoring source
in the manifest. If the game has no combo multiplier, use unlettered objects for runtime assets.
Never change balance just to justify a promotional badge.

For `/store-screenshots`, every generated game's store screenshot set instead includes five
theme-matched background combo balls marked `x5`, `x10`, `x25`, `x50` and `x100`, regardless of
the game's combo tiers. They are store-only scene decoration: do not insert them into real
gameplay captures, imply those tiers are reachable, present them as prizes, or alter the scoring
model to justify them. Build their shape, material, palette and light from the current Design
DNA. For every G1–G6 category and lead kind, make each ball a prominent secondary subject,
starting near 35-40% of the final portrait panel width.
The flying balls are mandatory: all five appear in the banner and the panorama (and any
`--panels 0` showcase background), and every panorama panel, including the character's, carries
at least one. Scatter them in flight at varied heights and depths around the character and across
the gameplay; none rests on an object. They may cover gameplay, symbols, outcomes, foreground
objects, and any other scene element except the main character. Keep all five ball labels
readable in the final screenshots.

These short, verified runtime game-object inscriptions and the five store-only ball markings
are exceptions to the no-baked-copy rule.
Keep ordinary UI and marketing text in code/compositor typography. For runtime assets, check
exact lettering at runtime size and derive it from the same config value; do not recolor a
symbol to invent a new tile identity. Store-only ball labels are never code/compositor
typography: the image model letters them from the exact labels written in the prompt, in the same
call that paints the scene. Check all five inscriptions at final screenshot size against the
required visual set.

## Flexible store composition

Plan every panel as a readable crop of one continuous scene. Choose positions and spans from
the mechanic, aspect ratio, and visual lead. Examples include character-left/gameplay-right-two,
full-width active peg field, an object-led jewel board across all three, or a contained field on
any panel.
The middle panel has no privileged role. Multiple play fields are allowed when they depict
real, coherent states and each remains readable; one continuous field is often stronger.
The panorama comes first, and it comes before the game: `/autocreate` renders it once the assets
exist, slices it into the carousel and stops until the user approves it
(`.claude/skills/store-screenshots/references/concept-panorama.md`). The game's field is then built
to look like its gameplay sample, the game background is rendered in its world, and the store kit
exports it unchanged and renders the banner with it attached as world context.
Each scene is one image that already contains the character, gameplay, foreground and the five
labelled multiplier balls: attach a shipped ball/coin/orb asset as the ball model and write the
exact labels into the prompt, so the image model paints and letters the balls in the scene.
Nothing is pasted or lettered onto generated art by script. Give the image generator the real
active gameplay capture — or, before the game exists, the layout draft built from its real
symbols — as context for the mechanic, symbols, topology and scoring moment; have it render
gameplay naturally at a three-quarter/3D angle within the same image as the environment and
foreground.
Do not paste the capture or a derived board plate into the panorama, or leave a placeholder
opening for a later gameplay insert. Reject generated gameplay that changes the real mechanic —
a match board redrawn as spinning reels is a failure.

When the game has a main character, show that character from torso to head in the banner and
the panorama, including enough torso to read the costume and pose. This framing is mandatory.
For humanoids, crop through the torso; for animal mascots, crop through the body in
species-appropriate terms. The bottom edge or the foreground band hides everything below the cut:
no legs, knees, hips or feet. The character is never standing full length and never flying,
floating or leaping. Keep visible open space above the complete head and hair/headwear in the
final panel crop, at least 2% of panel height. Protect the head and attached silhouette from the
first seam; a left crop is allowed and a bottom crop through the torso is expected.
Character-led concepts default to a large character on the first panel.
Object/mechanic leads have prominence and readability checks, not anatomy requirements when
the game has no main character.

For an object/mechanic-led game with no living character in its concept and shipped inventory,
the first two carousel slides are gameplay-led. Show the authentic board or mechanic at a readable
three-quarter/3D angle in each crop, or use one continuous angled gameplay surface with meaningful
play visible in both. Do not invent a human, hand, animal, mascot or player silhouette, and do not
use a decorative object-only first slide. Preserve the real topology, symbols and scoring state.
Character-led games keep their existing character-first defaults.

Boards may cross any seams. Put cuts through noncritical housing, gaps, or background; keep
faces, decisive symbols, combo inscriptions, targets, and critical interaction clear of the
actual gaps. Review both the assembled panorama and the gapped carousel. If a
critical region cannot survive a proposed span, move/scale the composition or change the cuts.

Use one visual review of the final crops; numeric composition bounds are optional diagnostics.
The background may be colorful and luminous while staying subordinate through softer focus and
lower local contrast.

Frame the lower edge like close-up slot-style key art: roughly 5–7 of the game's own objects
across a three-panel scene, each very large and near the camera, overlapping in depth and cropped
by the bottom edge, over a continuous glittering layer of the game's gold treasure (gold, gems and
sparkle as decoration — never a currency the game has) that runs the full width. Keep each
object's silhouette readable. Avoid miniature clutter and any supporting surface beneath the
objects; no floor, fabric, tabletop or drape. Keep selected multiplier balls flying in front of
the gameplay: at least two must visibly cover part of the board or mechanic in
the marketing scene. Balls may obscure anything in the scene except the main character; keep
every ball outside the player/hero character silhouette. For lighting, use the game's
authentic palette with strong warm/cool separation, clean specular highlights, local reflected
color, selective glints and controlled bloom around real light sources. Keep color-rich shadows
and vivid midtones; avoid a single-color wash, blanket saturation and clipped highlights. The
source panorama should look like bright premium mobile-game key art before compositor grading.
Never tint runtime art.

The feature graphic needs its own horizontal render and the same context decision. A left-heavy
3/5–2/5 arrangement is an option, not a universal rule. Object-led and mechanic-led banners may
use the full width. No reserved device-shaped zone; the clean source must look finished alone.
The shipped feature graphic is that scene plus one framed phone on the right holding a real
capture, and it carries no text: no title, tagline, logo, wordmark or copy on the left or
anywhere else, and no blank space kept for them.
Real gameplay showcase frames remain actual captures. Store work preserves menu/gameplay/splash
background assets and wiring; redesigning them requires an explicit user request.


## Image reference transport preflight

Check the active image transport's reference limit before submitting a large asset set.
A built-in transport observed in September 2026 accepted at most five paths even though its
visible schema showed only an array. Treat that as observed transport behavior, not a permanent
limit for every provider. A request rejected during argument validation is not a generated
source or a spent quality correction; record the rejection separately.

When the inventory exceeds the supported limit, preserve complete reference coverage through
staged integration or a labeled lossless contact sheet made from the original files. Inspect
every original at full size and game size and retain its alpha audit and source-to-sheet
mapping. Keep important identity references as separate inputs where possible; label runtime
frames as topology/state evidence and previews as composition references. Do not omit secondary
symbols to fit the limit, mistake a contact sheet for finished art, or claim packed references
guarantee faithful output. Compare every resulting identity and the full field with the original
sources after generation; all existing visual, math, seam and runtime gates still apply.

## Deterministic runtime-background guards

Before and after store branding, compare the same complete background/splash file inventory,
SHA-256 hashes and code/config selecting references. Sort file paths before hashing. Search
tools may return identical matches in a different filesystem traversal order: normalize away
line numbers where the guard already calls for that, then sort the full reference records
before comparing them. Keep paths and complete matched content; sorting must never discard
a removed/added reference or suppress a changed selector. Preserve raw inventories as evidence.
If an exact comparison fails but sorted records and asset hashes match, report unchanged
background wiring with an ordering-only diagnostic. Never recolor or replace a runtime
background to resolve an inventory-order difference.
