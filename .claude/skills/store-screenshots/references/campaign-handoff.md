# Campaign handoff

Three pictures carry the campaign, and `/store-screenshots` builds everything else on them:

| Picture | Made by | What the store kit does with it |
|---|---|---|
| The approved concept panorama (`concept/panorama.png`) | `/autocreate` Phase 3.9, approved by the user ([concept-panorama.md](concept-panorama.md)) | exports it **unchanged** as the carousel panels — crops, grading and the detail pass only — and renders the banner, icon and emblem in its world |
| The game background (`shared-background.png`) | `/autocreate-implement` Phase 4.0, in the panorama's world ([campaign-art.md](campaign-art.md)) | puts every real-capture phone slide on it — the same picture the captured game shows |
| The banner (`long-banner.png`) | `/store-screenshots` itself, in the panorama's world ([campaign-art.md](campaign-art.md) Step 4) | the feature graphic: the banner with one phone on the right |

## What the pipeline leaves in `production/store-art/`

- `concept/` — the panorama, its prompt, the exported panels and `export-flags.txt`, the gameplay
  sample, and `concept.json` (`tools/concept_gate.py`: status, revision, the panorama's SHA-256,
  who approved it and when);
- `shared-background.png`, `background-prompt.txt`, `background-crops.png`;
- after a store run, `long-banner.png`, `banner-prompt.txt` and `context-capture.png`;
- `lineage.json`, the ledger of every generated picture;
- `campaign.md`, which records:
  - per picture, `status: ACCEPTED | BLOCKED` and the reason for a block;
  - game/package identity, `lead_kind`, and the template ids used (`background-character`, …);
  - `world_panorama_sha256` — the approved panorama each picture was rendered in the world of;
  - the ordered references for each image call with their SHA-256 — the original character asset
    first, the approved panorama, the original background, sprites, reference sources;
  - SHA-256 of `shared-background.png`, `long-banner.png` and their prompt files;
  - the runtime pictures (`bg_campaign_menu.png`, `bg_campaign_game.png`) with SHA-256, the
    replaced background files, and every `file: selector` wiring edit;
  - the review verdicts, retries and corrections;
  - the runtime evidence paths once finalization has verified the integrated background (V22).

Preliminary captures and an unverified background are never labelled accepted.

## Validating it in `/store-screenshots` preflight

**The panorama.** `python3 tools/concept_gate.py status`:

- **APPROVED** and the panorama intact → this is the kit's panorama. Copy it unchanged into the
  run's `art/` directory; never regenerate, edit or re-letter it.
- **PENDING or DRAFTING** → the user has not approved the concept carousel yet. Stop and report
  BLOCKED: the store kit is built from the approved panorama.
- **NONE** (a game made before the approval gate) → make its panorama now with
  [concept-panorama.md](concept-panorama.md) (legacy caller, a real capture as context), then
  continue as if it had been approved. Record in `STORE_INFO.md` that it was not user-approved.

**The game background** is valid only when all of these hold:

1. `campaign.md` records it ACCEPTED and every listed file exists with its recorded SHA-256.
2. Its `world_panorama_sha256` is the current panorama's — a background made in the world of an
   older banner (before the approval gate) stays wired and valid for the game, and is recorded as
   such; it is only remade when the user asks for it.
3. Its prompt file still passes `python3 tools/prompt_template.py check` against the current
   `campaign-prompts.md` for its recorded template id — or `campaign.md` records a passing review
   of the accepted picture against the current template (its SHA-256 and the verdict). A template
   change alone triggers that one review, not a remake; only a picture that breaks a current rule
   is stale.
4. The original character asset is unchanged (its hash agrees with the record).
5. `bg_campaign_menu.png` and `bg_campaign_game.png` exist with their recorded hashes and are
   still selected from `lib/`.
6. `production/store-art/lineage.json` records it at generation 2 or less
   (`python3 tools/art_lineage.py verify --file ...`). A picture made before the ledger existed is
   adopted (`--made adopt`) when its review finds no generation artifacts (smeared texture, mushy
   detail, colour drift), and remade fresh otherwise.

**The banner** is reused only when `campaign.md` records it ACCEPTED with
`world_panorama_sha256` equal to the current panorama, its prompt and the character asset,
multiplier reference and topology hashes still agree, and the ledger records it at generation 2 or
less. Otherwise the store run makes it — campaign-art.md Step 4.

**Valid** → copy the approved panorama, `shared-background.png` and a valid `long-banner.png`
unchanged into the run's `art/` directory and record their provenance in `STORE_BRIEF.md` and
`STORE_INFO.md`. Do not regenerate any of them.

**Missing or stale** → run the matching step of [campaign-art.md](campaign-art.md) now, before the
store kit — reusing whatever still validates, and remaking the rest as fresh renders from the
original references and the approved panorama, never as edits of the stale picture — and record in
`STORE_INFO.md` why reuse was unavailable and which runtime files changed. The single exception is
an explicit `--keep-runtime-background`: the banner is still made (campaign-art.md Step 4), but the
game background is neither generated nor wired, and the phone slides use the standalone fallback
in `/store-screenshots` Phase 5.

## After the handoff

The background guard in [runtime-branding.md](runtime-branding.md) takes its baseline after this
step, so the store kit's own edits (icon, emblem) can never touch the campaign background. The five
multiplier balls stay mandatory in the panorama (at least one per panel) and the banner. The game
background carries none: it is a runtime asset, not a marketing scene.
