# Campaign handoff from autocreate-finalize

Finalization owns the initial banner and the shared runtime/phone-showcase background. Store
screenshots consumes them to create the panorama, icon/emblem, feature graphic and mobile slides.

Persist these outside timestamped store exports:

- `production/store-art/long-banner.png`: accepted device-free store banner.
- `production/store-art/shared-background.png`: clean environment used both in the game and
  behind phones on real-capture slides; no promotional multipliers or baked gameplay.
- `production/store-art/banner-prompt.txt`: exact generation prompt.
- `production/store-art/campaign.md`: game/package identity, lead kind, Design DNA/reference
  sources, ordered generation references and their SHA-256 hashes, preliminary gameplay context
  path and topology/outcome, banner/background paths and SHA-256 hashes, runtime background copy
  path/hash and selector edits, acceptance/correction results, and final runtime evidence paths.

In store preflight, read this handoff and verify files/hashes, game identity, shipped character,
ball/symbol assets and topology against the current game. A background-only change after the
preliminary capture is expected: the final captures must show the integrated background.
Copy the accepted banner and shared background unchanged into the store run's `art/` directory;
record provenance in `STORE_BRIEF.md` and `STORE_INFO.md`. Do not regenerate a valid banner.
If stale or missing, use the existing Phase 1a prompt and correction policy to generate the banner
for this store run and report why reuse was unavailable. A standalone store run preserves runtime
backgrounds; it does not silently perform finalization's background replacement.

For a valid handoff, use `art/shared-background.png` as the `showcase --bg` input with no
`--bg-panel` or `--bg-subject` panorama crop options. It is the same image as the registered
runtime background; only responsive cropping may differ. The panorama remains a separate new
composition generated with the accepted banner as world context. The icon uses the banner as
world context and original shipped assets as identity authority. Reuse a suitable existing icon
only if it matches that campaign; otherwise generate it under the existing icon budget.

With `--panels 0`, reuse the shared background for real-capture phone slides and omit the separate
multiplier showcase generation. The five marketing balls remain mandatory in the banner and,
when generated, panorama (one or more per panel); the shared clean background is exempt.
Without a valid shared-background handoff, retain the standalone panorama/showcase backdrop path.

Finalization updates the handoff with final runtime captures after integration and verification.
On interrupted runs, do not label preliminary captures or an unverified background as accepted.
