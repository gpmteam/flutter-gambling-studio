# Build a casual mini-game

The studio produces portrait-phone Flutter + Flame casual games. Premium casino artwork or
another visual reference can guide the assets; gameplay is always casual. Use points, stars and
progress unlocks, never money, wagers or random prizes. Read
[game categories](../.claude/docs/game-categories.md),
[balance models](../.claude/docs/balance-models.md) and
[the no-gambling gate](../.claude/rules/no-gambling.md).

Claude, Codex and Gemini use the same canonical `.claude/` framework. Codex starts at `AGENTS.md`
and uses `.codex/commands.md` to resolve slash-command runbooks.

## Full pipeline

Run `/autocreate` for autonomous creation or `/autocreate --from-concept` for an existing
`design/gdd/game-concept.md`. The pipeline covers concept/reference detection, assets and data,
implementation, analysis/tests, UI/balance checks, Chrome runtime, actual playtest and release
preparation. Its three sessions persist handoffs so interrupted work can resume. It does not
build an APK/AAB or archive; request `/release-package` when ready.

## Step-by-step route

1. `/brainstorm` selects G1–G6, an archetype A–AB or unique casual mechanic, theme and B1–B6
   model. `/auto-idea` does this autonomously. The Classification block records scoring, balance
   config, reference gameplay and the no-gambling check. Casino gameplay is translated;
   already-casual references may retain their mechanic, such as Zeus's 7×6 link board.
2. `/gate-check concept`, then `/map-systems`, writes the architecture and dependency plan.
3. `/design-system board-rules`, `/design-system tier-chain`, `/design-system tempo-ramp` or
   another category-appropriate system writes its GDD and JSON config with `balance-designer`.
   Built-in balance bots verify swap/link/blast, sort, slide merge and reflex ramps. Other
   mechanics require the actual game's headless rules/physics/solver bot before final signoff.
4. `/generate-png-asset --from-concept` generates the piece cast, UI and backgrounds from the
   asset manifest and reference sources. Ordinary assets have no lettering; verified combo
   markers follow the game's scoring. Match identity and visual style without casino controls.
5. `/team-dev "Build the core from our design document"` implements rules, presentation, UI and
   deterministic save/progression/achievement/collection/daily systems. One seeded `GameRng`
   resolves moves in the pure rules engine before animation.
6. `sound-designer` supplies sound effects through `flame_audio`. Background music is opt-in.
7. `/balance-check`, `/code-review`, `/ui-audit`, `/emulator-test` and `/playtest` verify the
   complete game. Play valid moves to actual complete/fail states; a generic button tour cannot
   prove that direct board manipulation works. Verify the four portrait phone sizes.
8. `/release-checklist` checks the no-gambling gate, content, seeded replay, curve evidence and
   playability. Metadata describes casual play and records “simulated gambling: no”, with an age
   rating based on actual content. Do not add gambling disclaimers, odds screens or age gates.
9. `/release-engineering --prep-only` prepares icons, splash, metadata, version and CI without
   native builds; `/release-package` explicitly builds and archives sources, APK and screenshots.

```bash
python3 tools/simulate_balance.py --model b1 --config design/balance/level-config.json
python3 tools/simulate_balance.py --model report --config design/balance/bot-report.json
python3 tools/simulate_balance.py --selftest
python3 -B tools/check_no_gambling.py
```

Balance returns 0 PASS, 1 CONCERNS or 2 FAIL and writes `design/balance/simulation-report.md`.
Adjust the JSON with `balance-designer` and rerun after a difficulty change. Extend the result
with `/add-feature "rocket special"` or `/add-feature "daily skill challenge"`.
