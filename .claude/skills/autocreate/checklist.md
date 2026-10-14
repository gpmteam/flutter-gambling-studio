# /autocreate — Session 1 checklist

Read this after a compaction instead of `SKILL.md`; open a `SKILL.md` section by its heading only
when a step is unclear. Phases, commands and exit criteria only — the rules themselves stay in
the runbook and in the documents each phase names. **Session 1 is one thread**: every phase
below runs here; no sub-agents, no delegated phase.

| Phase | Do | Exit |
|-------|----|------|
| 0 reference | `production/session-state/user-request.txt` (verbatim); `python3 tools/reference_detect.py --prompt-file … --attachments-dir design/references/user --new-game --json > design/references/detection.json` and `--markdown > design/reference-contract.md`; view every mapped source at full size | contract written; nothing the detector found is dropped |
| 1 concept | `auto-idea` logic (unless `--from-concept`) → `design/gdd/game-concept.md`: Classification block, reference bar, production plan (≥ 12 levels or endless, 2–3 modes, stars, achievements, album, daily), Game UI Read, Design Signature, per-screen recipes, Similarity Check, `lead_kind` + `menu_role`, ≥ 12 screens, portrait-phone declaration, reference record | complete; `--idea-only` stops here |
| 2 bootstrap | `flutter create . --project-name game_app --platforms web,android,ios --org com.gamestudio`; portrait lock in the manifest and plist; pubspec deps and asset dirs; `design/structure.md` (one of V1–V5); `design/art-direction.md` (UI Read, Signature, state map, recipes at 390×844 with P strategies, Similarity Check) | `web/index.html` exists; both design files written |
| 3 assets | `design/asset-format.md`, `asset-prompts.md`, `asset-manifest.md` before generating; PNG with the built-in image tool (headless: `python3 tools/gpt_image.py`), chroma key + `python3 tools/cutout.py`; one original abstract slot-style background; a round multiplier reference named in the manifest; board frame / tile assets when the art direction has them; `tools/cutout.py --dir assets/images/sprites --check` and `--dir assets/images/ui --check`; `flutter pub get` | every manifest row has a file, SHA-256 and verdict |
| 3.5 audio | `python3 tools/synth_sfx.py --from-concept --sfx-dir assets/audio/sfx` | 8 WAVs; no BGM; no `assets/audio/bgm/` in pubspec |
| 3.6 cohesion | `/asset-review` as art-director: contact sheets incl. the 64 px sheet, AR1–AR11 → `design/asset-review.md` | PASS, or every REGENERATE fixed and re-reviewed |
| 3.7 data | balance config in `design/balance/` from `.claude/docs/templates/balance-configs/`; `python3 tools/simulate_balance.py` where the mechanic is built in; `assets/data/levels.json` or `ramp.json`/`stages.json`; `assets/data/progression.json`; 2–3 modes recorded; parse every JSON | all JSON parses; no currency, price, odds or payout field |
| 3.8 handoff | `production/session-state/autocreate-handoff-1.md` with `Concept gate: required`, identity, links, counts, lead / multiplier / background / board assets, Session 2 exit criteria, portrait checklist, reference binding | written |
| 3.9 carousel | concept-panorama.md Steps 1–7: layout draft; `store_compose.py composition-guide --size play --canvas … --offset-y 1 --lead … --field … --ball …`; `panorama-character|object` rendered from campaign-prompts.md and `prompt_template.py check`; ONE render with the identity asset, multiplier reference, guide, draft and field assets; `art_lineage.py record --role panorama --made fresh …`; bounded review (`concept_gate.py budget`: 3 fresh / 5 repairs — check a crop with `composition-guide --over` before exporting); `triptych` with the store flags → `export-flags.txt`; gameplay sample + spec; `concept_gate.py publish [--known-issue …]` | status PENDING |
| 3.10 gate | print the `CONCEPT READY FOR APPROVAL` report; **stop** | no code, no Session 2, no self-approval |

`--revise "<feedback>"`: concept-panorama.md → "Revisions" — `concept_gate.py revise`, regenerate
only what the feedback touches (fresh from the originals), publish the next revision, stop at the
gate again. NONE/DRAFTING → treat the message as more direction and resume at the first phase
whose artifacts are missing; never repeat completed asset generation.

Economy: read each reference document once; review candidates on one contact sheet; one export
per accepted crop; after a compaction come back here, not to `SKILL.md`.
