# Game concept examples and preview references

Inspect the matching local preview when a user requests one of these game families. For the five
named requests below, the listed preview is mandatory input to `/autocreate`, including the
`--from-concept` path and common spacing, punctuation, hyphenation, and capitalization variants of
the name. A reference entry is either one file or a folder; when it is a folder, every file in it
is mandatory input and the table states each file's job. Every family is an **exact** reference —
recreate it — except Royal Joker, a **loose** reference: a common reference for the game's world,
not a recreation (see "Loose references" below).

**A reference governs the look; `.claude/rules/no-gambling.md` governs the gameplay.** These
previews are casino art — slots and a plinko board. The studio reproduces their character, symbol
cast, frame ornament, background, palette and finish exactly — and builds a casual mechanic on top
of them, because the reference's own gameplay is a casino game. A reference whose own gameplay is
already casual would also lend its gameplay and topology; none of the mapped previews is one. The
`Reference gameplay` column records this for each family.

Suitable pixels may be reused as runtime assets when cleanly isolated and sharp at target size.
The previews are not game specifications or validated level designs. Use
`.claude/docs/visual-context.md` and record the preview path, borrowed traits, the casual
mechanic, lead kind and topology decision in the generated concept before producing assets.

| Request family | Preview | Reference gameplay | Build as (Classification) | Lead and assets | Store starting composition |
|---|---|---|---|---|---|
| Book of Ra / Book of Ra game | `examples-games/book-of-ra.png` | Casino slot — look only | **G2 / E / B2** triple tile tray: relic tiles stacked in layers inside the temple frame, a 7-slot tray | Character; reference-matched desert archaeologist, enchanted book, ankhs, scarabs, falcons, Egyptian relics as tiles | Large reference-matched explorer on the first panel; the layered relic pile and tray occupy the right; sunset temple depth and relic spill support the gameplay |
| Royal Joker / Joker / Joker game | `examples-games/royal-joker/` — all three files: `rj_key-art.jpeg` (the jester to keep), `rj_store-set-1.jpeg` (symbol family, gold frame, lightning), `rj_store-set-2.jpeg` (second jester pose, cherries and sevens) — **loose: a common reference, not a recreation** | Casino slot — look only | **G1 / C / B1** tap blast on a 7×8 grid in a gold frame | Character; the reference's grinning, mischievous jester — the same character — with fruit, sevens, crowns, stars and gems as tiles | Large jester on the first panel over a background designed for this game; the blast board spans the right two; fruit and gold light carry the motion |
| Joker Jewels / Joker's Jewels / joker-jewels | `examples-games/joker-jewels/` — all four files: `jj_reference.jpeg` (key-art staging), `jj_gameplay.jpeg` (symbol family, purple reel-strip columns and frame), `jj_character-reference.jpeg` and `jj_character-reference2.jpeg` (jester lead) | Casino slot — look only | **G1 / A / B1** swap match-3 on a 7×8 grid whose columns wear the purple reel-strip backing | Character; reference-matched belled-cap jester in a striped costume, plus faceted red and cyan gems, blue orb, lute, juggling clubs, jester shoes, crown special tile | Large reference-matched jester on the first panel; the match-3 board occupies the right; gems, bunting and confetti spill through the foreground |
| Shining Crown / Shining Crown game | `examples-games/shining-crown.jpeg` | Casino slot — look only | **G3 / I / B3** slide merge on a 4×4 grid: ruby → clover gem → star → … → the Shining Crown at the top of the tier chain | Object; crown, jewel star, clover gem, ruby, gold medallions as tiers | No invented player or mascot; slides 1–2 show the jewel board at a three-quarter/3D angle, with the crown and jewels across the foreground |
| Plinko / Plinko game | `examples-games/plinko.jpeg` | Casino plinko — look only | **G4 / N / B4** peg clear: aim glossy balls through the tilted peg field to clear target pegs; a moving catch bucket replaces prize buckets | Mechanic; glossy colored balls, pegs, the tilted board, glowing trails | Active tilted peg field can fill all three panels; trajectories carry motion; no invented person or mascot |
| Chicken game | No exact local preview required | — | **G5 / R / B5** lane runner: cross lanes of traffic and hazards, points by distance | Character; expressive chicken, road lanes, hazards, collectible grain | Chicken on the first panel; the lanes may span the remaining panels or the whole scene |

## Detecting a reference request

Detection is deterministic: `/autocreate` Phase 0 runs `tools/reference_detect.py` on the user's
exact request and writes `design/references/detection.json` and `design/reference-contract.md`.
The table above is the detector's family list; change both together (a test keeps them in step).

| Trigger | Examples it catches | Binding |
|---|---|---|
| A named family | "Joker Jewels", "Joker's Jewels", "joker-jewels", "джокер джуэлс", "Royal Joker", "роял джокер", "Joker", "джокер", "Book of Ra", "книга ра", "Shining Crown", "шайнинг краун", "Plinko", "плинко" | exact — the mapped files; loose for Royal Joker |
| Images attached to the request | anything the web service saved in `design/references/user/` | exact — on a new game always; on a follow-up when the message asks to match them |
| An explicit reproduction ask with no image | "exactly like Gates of Olympus", "копия игры …", "один в один как …" | description — match every described trait |

The detector also reports the **mechanic** that governs play:

| `topology_source` | Meaning |
|---|---|
| `family` | The family's "Build as" mechanic and topology above |
| `user mechanic` | The user named a casual mechanic ("Book of Ra match-3", "Joker bubble shooter"); it governs play and topology, the family governs identity |
| `translated` | The user named a gambling mechanic ("Book of Ra dice", "a roulette game"); the detector's translation (`.claude/docs/game-categories.md` → "Translating a gambling ask") governs play |
| `user grid` | The user named a grid; it governs the board when the mechanic can be played on it |
| `concept` | No family and no mechanic — the concept decides |

Two rules keep detection honest:

- **Only additions.** The detector can miss a reference, so an agent may add one; it may never
  drop one the detector found, reinterpret a named family as "inspiration", or treat attached
  images as mood boards.
- **Identity and mechanics are separate.** The family always governs identity — the character,
  symbols, board and frame materials, background, palette and finish (a loose family governs the
  world they belong to, not their pixels). The mechanic comes from the
  table above, the user's casual mechanic, or the translation of a gambling ask — never from a
  casino reference's own gameplay.

User attachments are held to the same standard as the mapped previews: every section of "How close
to the reference — match it" below applies to them, with the attachment as the source image. When
an attachment shows a casino game (reels, a bet panel, a paytable), reproduce its look and
translate its mechanic exactly as for a mapped casino family.

**Royal Joker and Joker Jewels are separate families.** A request that names Royal Joker, or only
a Joker, resolves to the `examples-games/royal-joker/` folder — a loose reference — and the
tap-blast board. A request that names Joker Jewels, Joker's Jewels, Jokers Jewels or
`joker-jewels` resolves to the `examples-games/joker-jewels/` folder and the swap match-3 board,
an exact reference, and is never satisfied by the Royal Joker row.

**Joker Jewels file roles.** Use `jj_reference.jpeg` for the festive purple staging, bunting,
confetti and the mask-with-gems subject pairing; `jj_gameplay.jpeg` for the symbol family (jester
face, crown, lute, juggling clubs, jester shoes, red and cyan faceted gems, blue orb), the purple
reel-strip colour that becomes the board's column backing, and the frame; and both character
references for the lead's striped costume, three-point belled cap, painted face and juggling
gesture. Do not reproduce the `Joker's Jewels` wordmark, the operator logo or branding, or the
reference's UI chrome, copy, credit/bet panel and paytable — those are another product's casino
interface.

## Loose references — a common reference, not a recreation

Royal Joker is mapped as a **loose** family (`binding: loose` in the detection). Its previews give
the game its character and its world, not its whole look:

- **The character can be the same.** Keep the jester as the previews draw him — the grinning,
  mischievous face, the purple-and-gold belled cap, the red-and-gold costume. Generate him from the
  source images.
- **The world guides, it does not dictate.** The symbol family — fruit (cherries, plums, oranges,
  lemons, grapes), sevens, crowns, stars and gems — the gold trim and the glossy 2.5D slot-art
  finish set the tone; the exact symbol set, its silhouettes, the frame and the composition of the
  menu and store art are this game's own.
- **The background is free.** Design it for the game's concept and vary it from game to game. The
  previews' red diamond-pattern backdrop is one possibility, not a template — do not copy it every
  time. Do not fall back to the old palace or ballroom staging either.
- **Gates.** AR11 and V21 hold the character to the sources and check that the symbols and finish
  fit; the background is not compared with the previews.
- Images the user attaches still bind exactly, even alongside Royal Joker.

The next section applies to exact references: every other mapped family and attached images.

## How close to the reference — match it

When a request maps to an exact reference — a named exact family or the user's attached images —
**recreate what the reference shows.** Not a reinterpretation, not an homage, not "inspired by": put the
generated game's art beside the reference and they should read as the same world. Match all of
it, as closely as the generator can get —

- the theme and setting;
- the character: costume colours and pattern, cap or headwear shape and bell count, face paint,
  build, pose and expression;
- the full cast of symbols and sprites, object for object, with their materials and colours —
  they become the game's tiles, pieces, balls or targets;
- the frame, board materials and ornament (a slot's reel frame becomes the board frame; its reel
  strips become the board's column backing);
- the palette, the light and the background treatment;
- the composition — what sits where on the menu and on the game screen;
- the UI mood: button shapes, panel materials, frame ornament.

**Do not introduce visual variation for its own sake.** No "make it your own", no fresh take, no
re-theming, no substituted symbols, no palette shift, no inverted brightness. Wherever a visual
choice is open, take the one that looks more like the reference. Art that reads as a different
game is wrong, and it is regenerated toward the reference rather than away from it.

**Inspect and supply the reference.** View every mapped file at full size before writing the
concept and before generation. Record the exact costume pattern, cap, symbol list, reel-strip
colour, frame ornament, background, linework, depth and light. Pass the relevant image files into
a reference-capable generator at high fidelity; use those observations in the prompt as specific
constraints. Text-only generation when image inputs are available causes identity drift.

### Production limits

1. **The title, wordmark, logo and operator branding.** Those are the trademarks of a published
   commercial product, and the generated game ships under its own name and its own logo.
   Everything the logo sits on top of is matched.
2. **Source image quality.** Direct reuse is appropriate only for a clean element or background
   that remains sharp at its actual displayed size. A flattened screenshot is usually unsuitable
   as a whole game background because it bakes in symbols, controls, title or payout text. Isolate
   suitable pixels with provenance, or generate a production-sized asset from the actual source
   image as a high-fidelity visual input. Do not substitute a merely similar character or symbol.
3. **The casino mechanic and interface.** Reels that spin for an outcome, paylines, the bet and
   credit panel, SPIN/AUTOPLAY buttons, paytables and multiplier payouts are never carried over
   (`.claude/rules/no-gambling.md`). The symbols are kept; what the player *does* with them is the
   casual mechanic in the table, and difficulty comes from `balance-designer`'s level curve.

Everything outside these limits is matched, not adapted.

For Book of Ra and Joker Jewels the character is the lead: rebuild that character
as the reference draws it, as the game's host. Royal Joker's jester is the lead too, designed
fresh within that reference's world. For Shining Crown and Plinko the absence
of a main character is itself part of the reference contract: do not add a host, mascot, hand,
player silhouette, deity or other living lead.

## Concept seeds

**Prism Pegs:** Aim a luminous ball into a cosmic peg field and clear every orange target peg
before the balls run out; a moving catch bucket at the bottom returns a ball. Match the Plinko
preview's diagonal action, oversized glossy balls, luminous trails and saturated separation. The
board looks like the preview's; the level layouts, target counts and ball budgets come from the
B4 level curve. G4 / N / B4.

**Sun Archive:** A triple-tile puzzle in an Egyptian temple: relic tiles — books, ankhs, scarabs,
falcons, lamps, jackals — are stacked in layers inside the preview's gold-and-lapis frame, and the
explorer cheers each cleared triple. Borrow the preview's explorer-left/field-right staging,
sunset temple depth, turquoise-and-gold relic family and dense archaeological foreground. Rebuild
the explorer and every relic as the preview draws them, object for object. Every deal is
generated solvable and ramps by layers and tile kinds. G2 / E / B2.

**Crown Merge:** A slide-merge game on a 4×4 board set in the crown preview's royal gold: rubies
merge into clover gems, clover gems into stars, up a jewel ladder to the Shining Crown itself.
Match the preview's royal tactility, jewel silhouettes, dramatic lighting, frame ornament and gold
spill. x2/x5 combo badges appear when one swipe makes several merges. G3 / I / B3.

**Royal Blast:** A tap-blast board of cherries, plums, oranges, sevens, crowns and stars in a
gold frame; Royal Joker's grinning jester in his purple-and-gold belled cap hosts from the left and
reacts to big blasts. The jester is the previews' own; the symbol designs and the background are
this game's — pick a setting for the concept rather than the previews' red backdrop. Keep the
mischievous expression rather than drifting toward an elegant host.
Groups of five or more leave a jester-cap rocket; level goals ask for cherries or sevens collected
within a move budget. G1 / C / B1.

**Harlequin Revel:** A swap match-3 of faceted red and cyan gems, blue orbs, lutes, juggling clubs
and jester shoes on a board whose columns wear the reference's purple reel-strip backing; the crown
is the special tile made by a five-in-a-row. A striped-costume jester is the visual lead and
appears in the menu, beside the board and in the level-complete celebration. Match the references'
carnival purple staging, bunting and confetti, glossy gem silhouettes, and the jester's striped
costume, belled cap and painted face as the character files draw them. G1 / A / B1.

**Chicken Dash:** A lane-crossing runner: the chicken hops across roads, rivers and farm machinery,
collecting grain for points; the tempo rises over a run. The chicken's comic defiance makes it the
visual lead. The tempo ramp, reaction windows and grace period live in the B5 config. G5 / R / B5.

Every seed's *look* comes from its preview and every seed's *difficulty* comes from its balance
model — those are the only two sources. Finish the normal concept around them: complete loop,
production plan, portrait phone layout, asset manifest, progression, required screens and a
verifiable balance config. The preview alone never proves playable UI, balance, or a completed
game.
