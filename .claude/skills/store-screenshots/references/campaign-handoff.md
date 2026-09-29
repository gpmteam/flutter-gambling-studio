# Campaign handoff

[Campaign art](campaign-art.md) — run by `/autocreate-finalize` Phase 10.4 — owns the banner and
the game background. `/store-screenshots` builds everything else on top of them:

- the **panorama** is a new composition generated with the accepted banner as world context;
- the **icon and emblem** use the banner as world context and the shipped assets as identity;
- the **feature graphic** is the banner with one phone on the right;
- the **mobile screenshots** put real captures on the game background — the same picture the
  captured game already shows, with its character whole in the frame.

## What finalization leaves in `production/store-art/`

`long-banner.png`, `banner-prompt.txt`, `shared-background.png`, `background-prompt.txt`,
`background-crops.png`, `context-capture.png`, and `campaign.md`, which records:

- `status: ACCEPTED | BLOCKED` and the reason for a block;
- game/package identity, `lead_kind`, and the template ids used (`banner-character`, …);
- the ordered references for each image call with their SHA-256 — the original character asset
  first, the multiplier reference, the context capture, sprites, reference sources;
- SHA-256 of `long-banner.png`, `shared-background.png` and both prompt files;
- the context capture's topology and outcome;
- the runtime pictures (`bg_campaign_menu.png`, `bg_campaign_game.png`) with SHA-256, the
  replaced background files, and every `file: selector` wiring edit;
- the review verdicts, retries and corrections;
- the final runtime evidence paths once Phase 10.5 has verified the integrated background (V22).

Preliminary captures and an unverified background are never labelled accepted.

## Validating it in `/store-screenshots` preflight

The handoff is **valid** only when all of these hold:

1. `campaign.md` says ACCEPTED and every listed file exists with its recorded SHA-256.
2. Both prompt files still pass `python3 tools/prompt_template.py check` against the current
   `campaign-prompts.md` for their recorded template ids. A banner made from an older prompt is
   stale: the banner rules changed, so the banner is remade under the new ones.
3. The original character asset, the multiplier reference and the game's topology/symbols are
   unchanged (hashes and the math config agree with the record).
4. `bg_campaign_menu.png` and `bg_campaign_game.png` exist with their recorded hashes and are
   still selected from `lib/`.

**Valid** → copy `long-banner.png` and `shared-background.png` unchanged into the run's `art/`
directory and record their provenance in `STORE_BRIEF.md` and `STORE_INFO.md`. Do not regenerate
either.

**Missing or stale** → run [campaign-art.md](campaign-art.md) now, before the store kit —
reusing whatever part still validates — and record in `STORE_INFO.md` why reuse was unavailable
and which runtime files changed. The store run then continues exactly as if finalization had
made the art. The single exception is an explicit `--keep-runtime-background`: the banner is
still generated through the banner step of campaign-art.md (same template, same check), but the
game background is neither generated nor wired, and the phone slides use the standalone fallback
in `/store-screenshots` Phase 5.

## After the handoff

The background guard in [runtime-branding.md](runtime-branding.md) takes its baseline after this
step, so the store kit's own edits (icon, emblem) can never touch the campaign background. The five
multiplier balls stay mandatory in the banner and the panorama (at least one per panel). The game
background carries none: it is a runtime asset, not a marketing scene.
