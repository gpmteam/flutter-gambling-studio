# /autocreate-implement — Session 2 checklist

Read this after a compaction instead of `SKILL.md`; open a `SKILL.md` section by its heading only
when a step is unclear. The orchestrator works from command output and the sub-agents'
summaries — it does not read `lib/` en masse and does not implement inline.

| Phase | Do | Exit |
|-------|----|------|
| 0 preflight | `autocreate-handoff-1.md`, `pubspec.yaml`, `design/structure.md` exist; `python3 tools/concept_gate.py check --for implement`; asset format from `design/asset-format.md`; read handoff-1, `production/store-art/concept/gameplay-sample.md` (view the png and the panorama), `design/structure.md`, `design/art-direction.md`, `design/gdd/game-concept.md` | OK, or stop with the reason |
| 4.0 intake | art-director sub-agent: sample-alignment assets (`tools/cutout.py`, `art_lineage.py record --role asset …`), the campaign background by campaign-art.md Steps 1–3 → `production/store-art/campaign.md` ACCEPTED with `world_panorama_sha256`; then write `lib/contracts.md` (topology, housing/tile assets, symbol order, clearing moment, `bg_campaign_*` as the only backgrounds) | background ACCEPTED; contract written |
| 4 code | persona passes **one at a time**, each a fresh sub-agent: A mechanics → E meta-systems → D sound → B ui → C juice; each gets its brief, `lib/contracts.md`, its data files and the rule files of "Per-pass reading" (`SKILL.md`) | five passes done; `active.md` has each summary |
| 4.5 wiring | B: level map / mode select ↔ data; E: progression, achievements, album ↔ data | Game accepts (mode, levelId) |
| 5 integration | lead-programmer: cross-agent mismatches; service, audio and VFX calls placed | 18 connections |
| 6 build | `dart analyze lib/` → owners fix their own errors | 0 errors |
| 6.5 feel | juice-artist: F1–F5 | analyze + test clean |
| 7 tests | `flutter test` → qa-tester writes/fixes | all green |
| 8 UI audit | `/ui-audit` (or ui-programmer over the 10 categories): portrait gate at 360×640, 360×800, 390×844, 430×932; the field against `gameplay-sample.png`; no-gambling | pass |
| 9 balance | `python3 tools/simulate_balance.py --model … --config design/balance/…` (or `test/balance/bot_sim_test.dart` → `--model report`); balance-designer edits the JSON only | PASS across the whole curve |
| 10 crash | 20/20 checks, no dead ends, `python3 -B tools/check_no_gambling.py` + the greps; final `dart analyze lib/` + `flutter test` | clean |
| 10.7 handoff | write `production/session-state/autocreate-handoff.md`; **close every Session 2 sub-agent**; spawn Session 3 as a fresh sub-agent with the prompt in `SKILL.md`; ONE `wait_agent` at the longest timeout; pass its report up | Session 3 report returned, or the failure + `/autocreate-finalize` named |

Sub-agent protocol (every pass): spawn → one blocking `wait_agent` at the longest timeout (again
only on a timeout) → read the 3–5 line summary → run the phase's exit command → `close` the agent
→ next pass. If the pool is full, close finished agents; never take their work into this thread.

`--resume`: pick the phase from the artifacts (`SKILL.md` → `--resume`) and do not redo what is
done.
