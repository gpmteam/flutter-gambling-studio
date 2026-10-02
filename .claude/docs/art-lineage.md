# Art lineage — keep generated art near its first generation

Every image-model edit re-renders the **whole** frame, even when the prompt says "change only X",
and every attached reference is copied at high fidelity, its artifacts included. So generated art
degrades along two paths, inside one run and across many:

- **Edit chains.** The campaign banner edited for a pose, again for a ball, again next run for a
  new rule. One store run edited its game background five times in a row — each call took the
  previous output as the edit target — and that picture is wired into the game and sits behind
  every phone slide.
- **Reference chains.** A new background rendered with the old background attached, a new banner
  rendered "in the world of" the old banner. Each render is nominally fresh, yet each inherits the
  previous one's smear and adds its own.

The result is soft, smeared texture, mushy faces and drifting colour that no export step can
remove, and whatever picture serves as world context passes it on to every picture rendered in its
world. That picture is now the **concept panorama the user approved** before implementation
(`tools/concept_gate.py`): the game background, the banner, the icon and the emblem are each
rendered from the original references plus that one panorama — never from one another.

## Rules

1. **Changes start from the original references.** A fresh render attaches the shipped assets,
   the reference sources and a real capture (or, before the game exists, the layout draft) — plus,
   for any campaign picture *other than the panorama*, the approved concept panorama as world
   context. Never attach an earlier version of the picture being made, a rejected candidate, or a
   generated background, banner, icon, emblem or showcase.
   The game background's "current background" reference is the game's **original** background, the
   one campaign art replaced — never `bg_campaign_*` or `shared-background.png`.
2. **At most one whole-frame edit per lineage, and only of a fresh render.** Anything already
   edited — or of unknown history — gets no further whole-frame edit.
3. **Local defects and local changes are region repairs** with `tools/region_repair.py`: a label,
   a ball, a hand, a held prop, a board cell, and a pose change that fits the character's area. Only
   the defect box is re-rendered and merged back; every other pixel stays byte-identical. A pose
   or layout that needs different space is a fresh render with the change written into the prompt.
4. **Crop before art.** Clipping at a seam, gutter or frame edge is fixed in the export
   (`store_compose.py` `--seam-snap`, `--offset`, `--offset-y`, `--zoom`), not in the picture.
5. **Template drift is reviewed, not regenerated.** When a prompt template changes, review the
   accepted picture against the current rules once; remake it (fresh) only for a rule it breaks.
6. **The approved panorama is a contract.** After the user approves the concept carousel it is
   only cropped, graded and detail-passed (`derive`, `detail`), and repaired as a region for an
   objective defect (`repair`) — never re-rendered or whole-frame edited.
   `tools/check_store_kit.py --concept` walks the shipped panorama's records back to the approved
   file.
7. **Record every generated picture** in `production/store-art/lineage.json` with
   `tools/art_lineage.py` — campaign art, store art, and any generated game asset a later request
   changes or aligns to the gameplay sample (role `asset`). The tool refuses the moves above.

```bash
# after a fresh render (list every attached image):
python3 tools/art_lineage.py record --file production/store-art/long-banner.png --role banner \
  --made fresh --ref "$CHARACTER_ASSET" --ref production/store-art/concept/panorama.png \
  --ref "$MULTIPLIER_REF" --ref production/store-art/context-capture.png \
  --prompt production/store-art/banner-prompt.txt
# before a whole-frame edit / before attaching a generated picture:
python3 tools/art_lineage.py check --file CANDIDATE.png --for edit
python3 tools/art_lineage.py check --file production/store-art/concept/panorama.png \
  --for reference --role banner
# after a region repair, detail merge, export or upscale:
python3 tools/art_lineage.py record --file art/panorama-r1.png --role panorama --made repair \
  --parent art/panorama.png
# a picture made before the ledger existed (counted as already edited):
python3 tools/art_lineage.py record --file production/store-art/long-banner.png --role banner \
  --made adopt
python3 tools/art_lineage.py show --file art/panorama-r1.png
```

Roles: `banner`, `background`, `panorama`, `icon`, `emblem`, `showcase`, `asset`. `--made`:
`fresh` (new render), `edit` (whole-frame edit of `--parent`), `repair` / `detail`
(`region_repair.py merge` into `--parent`), `derive` (resize, export, grade, upscale canvas — no
model), `adopt` (pre-ledger picture, generation 2).

Adopt a pre-ledger picture only when its review finds no generation artifacts (smeared texture,
mushy detail, colour drift); otherwise remake it fresh from the original references. The store
kit's archive gate (`tools/check_store_kit.py`) requires `art/lineage.json` and checks that the
shipped banner, panorama and backgrounds are recorded at generation 2 or less — and, with
`--concept`, that the shipped panorama is the approved one.
