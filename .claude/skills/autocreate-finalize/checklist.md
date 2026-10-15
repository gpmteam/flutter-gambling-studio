# /autocreate-finalize — Session 3 checklist

Read this after a compaction instead of `SKILL.md`; open a `SKILL.md` section by its heading only
when a step is unclear. One compile, one matrix: static audits and all their fixes first, then
the dev server once, then only the tour of a screen a later fix touched.

| Phase | Do | Exit |
|-------|----|------|
| 0 preflight | `production/session-state/autocreate-handoff.md` exists; `dart analyze lib/` 0 errors; `flutter test` (red is a warning); read the handoff: name, category/model, main game class, approved concept revision | fail-fast on handoff or analyze |
| 10.4 campaign | `python3 tools/concept_gate.py check --for implement`; `rg -n 'bg_campaign' lib`; `python3 tools/art_lineage.py verify --file production/store-art/shared-background.png`; `campaign.md` ACCEPTED (only a resumed project without it runs campaign-art.md Steps 1–3) | background wired on every screen |
| 10.45 branding | reuse an icon/emblem the ledger already records for this panorama; else one fresh render each with the panorama as world context + identity assets, `art_lineage.py record --role icon|emblem --made fresh …` (budget 1 fresh / 2 repairs each); `store_compose.py icon`; `flutter_launcher_icons` in pubspec, `dart run flutter_launcher_icons`; emblem → `assets/images/ui/ui_game_logo.png` + one `Image.asset` on the menu; `dart format`, `dart analyze lib/`, `flutter test`; background guard UNCHANGED; `campaign.md` "Branding: ACCEPTED" | applied, or `Branding: BLOCKED` with the cause |
| 10.5.0 static first | `python3 tools/check_asset_stretch.py --assets assets --lib lib --warn 0.05 --fail 0.10 --report … --json …` (V18); `python3 tools/check_menu_lead.py --lib lib --assets assets --min-side 120 …` (V19); `python3 tools/check_gameplay_center.py --lib lib --warn-px 16 --fail-px 48 …` (V20); fix every HIGH; `dart analyze lib/` | no HIGH before a server starts |
| 10.5.1 preflight | node + Chrome → `PLATFORM=web`; none → `SKIP_SCREENSHOTS=1` (SKIPPED is a normal verdict); `--platform android` → compile-only `flutter build apk --debug` (10.5.2c), no tour | decision logged |
| 10.5.2 one matrix | `nohup flutter run -d web-server --web-port 8099 --web-hostname 127.0.0.1` once; wait for the URL; `SHOT_DIR=production/runtime-screenshots/$TS`; `web_verify.mjs --size 390x844 --budget 180 --quick`, then `360x640 360x800 430x932` (`--budget 120 --quick`), `1440x900` wide host (`--budget 60`), `--soak 150`; vision V1–V23 on every capture (V21 beside the sources, V22 campaign, V23 against `gameplay-sample.png`); parse every `manifest.json`, `webconsole.log`, `flutter-run.log` | captures + logs under `$SHOT_DIR` |
| 10.5.3 fix loop ≤ 3 | targeted fixes only (`SKILL.md` table; never balance, data, GDD or whole screens; V13–V17 structural → FAIL and route back); restart the dev server; re-run ONLY the tour covering the changed screen at 390×844 (+ 360×640 for a layout fix) | 0 CRITICAL / 0 HIGH, V22 + V23 PASS, `STRETCH_EXIT=MENU_LEAD_EXIT=GAMEPLAY_CENTER_EXIT=0` |
| 10.5.5 artifacts | `$SHOT_DIR/REPORT.md` PASS/CONCERNS/FAIL + the three audit reports | written |
| 10.6 playtest | same server; `web_verify.mjs --soak 60` once; P1–P10 → `production/playtest/$TS/PLAYTEST-REPORT.md`; ≤ 2 fix iterations on P1/P2/P8; a suspected leak (P9) gets one look and at most one plain fix + one re-run soak — no heap snapshots, profile mode or backend rewrites (`SKILL.md` 10.5.2b) | ≠ NOT-PLAYABLE (or iterations exhausted, recorded honestly) |
| 11 state | `campaign.md` final paths/verdicts; `active.md` (Status, Runtime, Campaign, Tests, Balance); handoff `## Session 3 finished`; `production/session-state/finalize-verdict.json` from the evidence | written |
| 11.5 release prep | `/release-engineering --prep-only --no-keystore` (icon already applied in 10.45; stand-in only if BLOCKED), native splash, version, `store/`, `.github/workflows/build.yml` | icons/splash/store exist; no AAB/APK, no keystore |
| 12 report | print/return `AUTOCREATE COMPLETE — PRODUCTION READY` or `AUTOCREATE BLOCKED — …` with the blocking command first | returned |
| 13 store kit | `AUTOCREATE_STORE_KIT=service` or `--no-store-kit` → stop here; else PRODUCTION_READY → spawn the store agent (prompt in `SKILL.md`); BLOCKED → do not start it | — |

Never `flutter build web` here — the service builds the preview. Kill the dev server
(`.claude/runtime-logs/flutter.pid`) and any orphaned headless Chrome at the end.
