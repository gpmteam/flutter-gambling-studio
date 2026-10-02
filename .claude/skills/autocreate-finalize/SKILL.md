---
name: autocreate-finalize
description: "Session 3 of the /autocreate pipeline (Phases 10.4 → 10.5 → 10.6 → 11 → 11.5 → 12 → 13): the campaign check (the game background rendered in the approved concept panorama's world is wired into every screen), runtime + soak verification (Chrome CDP, auto-fix) including V22 (campaign background) and V23 (the live field against the approved gameplay sample), playtest (a real gameplay session, P1–P10), session state, release-engineering PREP (icons/splash/version/store-metadata/CI — WITHOUT building the AAB/APK and without a keystore), the final report and a machine-readable verdict, then the handoff to /store-screenshots, which exports the approved panorama and makes the banner from it. It does NOT build artifacts and does NOT call /release-package — that is an explicit user action. Started automatically through the Agent tool at the end of Session 2 (autocreate-implement), or manually in a new conversation."
argument-hint: "[--skip-emulator | --no-fix | --no-store-kit]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Finalize — Session 3 of the pipeline

**Purpose**: finish `/autocreate` after Session 2 (`autocreate-implement`) has brought the
project to `dart analyze` 0 errors + `flutter test` green. In this session:
- **campaign check** (Phase 10.4): the game background Session 2 rendered in the approved concept
  panorama's world (character whole in the portrait frame) is wired into every screen; it is
  rendered here only when a resumed project lacks it. No banner is made here — the store kit makes
  it from the approved panorama;
- runtime verification: Chrome/CDP (screenshots + console + auto-fix) plus a soak probe for leaks;
  Android (`--platform android`) is a Gradle compile-only check, with no emulator and no APK
- **playtest** (Phase 10.6): a real gameplay session — the P1–P10 checks from
  `.claude/skills/playtest/SKILL.md` (the score changes, clear/fail paths, a responsive board, progression)
- **V23**: the live field, side by side with the approved concept's gameplay sample, is the same
  field — the user approved the game by that picture
- updating the session state + the final report + `production/session-state/finalize-verdict.json`
- **the store kit handoff** (Phase 13): a production-ready game goes straight on to
  `/store-screenshots`
- **release-engineering PREP** (`/release-engineering --prep-only --no-keystore`): icons, native
  splash, versioning, store metadata, CI — **WITHOUT building the AAB/APK and without a keystore**

**Building the artifacts is NOT part of this skill.** The AAB/APK and the archive are built by
`/release-package` (an explicit run). For a signed AAB for Google Play, use
`/release-engineering` with no flags (it mints the upload keystore — an explicit user action).

**When it is called:**
- Automatically: Session 2 (`autocreate-implement`) calls the Agent tool at the end of Phase 10.7
  with a prepared prompt (a full-history fork, no subagent_type)
- Manually: the user runs `/autocreate-finalize` in a **new** conversation, if the sub-agent
  crashed, or to repeat the runtime check after edits

**What it does NOT do:**
- It does NOT rewrite game logic or change balance; Phase 10.4's background export/wiring (only
  for a project that lacks it) is the one sanctioned art change, recorded in the manifest and art
  direction
- It does NOT generate a banner or a panorama, and never touches `production/store-art/concept/`
- It does NOT create new screens
- It does NOT run Phases 1–10 — Session 2 already did those

---

## 🚨 MANDATORY CONTRACT

1. ✅ Reads `production/session-state/autocreate-handoff.md` **as its first action**
2. ✅ Validates that Session 2's artifacts exist (`pubspec.yaml`, `lib/main.dart`,
   `dart analyze` still 0 errors)
3. ✅ Reads `.claude/docs/mobile-first-contract.md` (portrait phone only — no desktop, tablet
   or landscape design) and `.claude/docs/gameplay-screen-contract.md` before runtime capture and
   treats every V13–V23 defect as a HIGH release blocker
4. ✅ Runs Phases 10.4 → 10.5 → 10.6 → 11 → 11.5 → 12 → 13 in that order
5. ✅ Returns the final report to the parent session (or prints it for the user) and writes
   `production/session-state/finalize-verdict.json`

**Forbidden:**
- ❌ Changing `lib/game/game_config.dart`, `design/balance/*.json` or `assets/data/*.json` —
  the balance and content are frozen
- ❌ Rewriting whole screens — only targeted runtime auto-fixes are allowed
  (overflow, setState after dispose, a missing asset path, a null ValueNotifier), plus the
  targeted background integration explicitly required by Phase 10.4
- ❌ Generating a release upload keystore — Phase 11.5 runs ONLY with `--no-keystore`;
  a signed AAB is the user's explicit `/release-engineering`
- ❌ Calling `/release-package` — packaging is a separate, explicit run
- ❌ Changing, regenerating or re-exporting the approved concept panorama or its carousel

---

## Phase 0 — preflight & handoff read [~30 s]

```bash
# 1. The handoff must exist
test -f production/session-state/autocreate-handoff.md || {
  echo "❌ No handoff file. Did Session 2 (autocreate-implement) not finish?"
  exit 1
}

# 2. The project must compile
dart analyze lib/ > /tmp/finalize_preflight_analyze.log 2>&1
if grep -q " error " /tmp/finalize_preflight_analyze.log; then
  echo "❌ dart analyze lib/ reports errors — Session 2 did not finish its work correctly"
  exit 1
fi

# 3. The tests must be green
flutter test > /tmp/finalize_preflight_test.log 2>&1 || {
  echo "⚠️ flutter test is red. We continue, but this is worth fixing."
}
```

Read the handoff file and extract:
- The game's name → for the archive's name
- The category (G1–G6), the balance model (B1–B6) and the reference-gameplay/translation decision → for the final report
- The path to the main game class → for emulator-test navigation
- The approved concept revision and `production/store-art/concept/gameplay-sample.md` → for V23
  (`python3 tools/concept_gate.py status`; LEGACY projects have none)

---

## Phase 10.4 — campaign check: the game runs on the approved world

Session 2 Phase 4.0 rendered the game background in the approved concept panorama's world
([campaign-art.md](../store-screenshots/references/campaign-art.md) Steps 1–3) and built every
screen on `bg_campaign_menu.png` / `bg_campaign_game.png`. Confirm it before runtime capture:

```bash
python3 tools/concept_gate.py check --for implement   # the approved concept (or LEGACY)
rg -n 'bg_campaign' lib                              # menu, splash route, secondary screens, game screen
python3 tools/art_lineage.py verify --file production/store-art/shared-background.png
```

`production/store-art/campaign.md` records the background ACCEPTED with the approved panorama's
SHA-256 as its `world_panorama_sha256`. When a resumed project lacks it — campaign.md missing, the
background BLOCKED, or a screen still selecting the original background — run campaign-art.md
Steps 1–3 now (render in the approved panorama's world, review the phone crops, export, retarget
the selectors with targeted edits, `dart format`, `dart analyze lib/`, `flutter test`). A LEGACY
project (no concept record) keeps the background it has.

This phase never makes a banner or a panorama: the store kit renders the banner from the approved
panorama and exports the panorama itself unchanged. Every picture stays near its first
generation ([art-lineage.md](../../docs/art-lineage.md)): a remade background is a fresh render
from the original references plus the approved panorama, never an edit of the previous one, and
`tools/art_lineage.py` refuses a second whole-frame edit.

Phase 10.5 verifies the integrated background at the phone matrix as **V22** and the live field
against the approved gameplay sample as **V23**; Phase 10.6 plays against both. If image
generation, the integration or a review fails, record BLOCKED in `campaign.md`, keep the previous
background wired, and continue only the independent checks. Runtime opt-outs do not waive the
campaign background: without a current real frame it is BLOCKED. A BLOCKED campaign is never
production-ready.

---

## Phase 10.5 — runtime emulator verification [~8 min]

Call the `/emulator-test --quick` skill (see `.claude/skills/emulator-test/SKILL.md`).

### 10.5.1 — preflight (web-first, headless, no display)

> **The default is headless web** through `flutter run -d web-server` + headless Chrome over CDP
> (`tools/web_verify.mjs`). That needs no emulator, no KVM, no graphical display and no
> `xdotool`/`osascript`. Android (`--platform android`) is an explicit request, and it **does not
> start an emulator/AVD**: it is a pure **Gradle compile-only verification**
> (`flutter build apk --debug`; the APK is neither kept nor packaged), with no runtime tour, no
> screenshots and no `adb logcat`. That removes the two main causes of Phase 10.5 hanging:
> "I cannot open/click Chrome" and "I cannot start an AVD/KVM in a headless environment".

```bash
# What the web path needs: node (for the CDP driver) + a Chrome binary (for headless shots).
HAVE_NODE=0; command -v node >/dev/null 2>&1 && HAVE_NODE=1
CHROME_BIN="${CHROME_EXECUTABLE:-}"
for c in google-chrome google-chrome-stable chromium chromium-browser; do
  [ -z "$CHROME_BIN" ] && command -v "$c" >/dev/null 2>&1 && CHROME_BIN="$(command -v "$c")"
done
export CHROME_EXECUTABLE="$CHROME_BIN"

if [[ "${AUTOCREATE_SKIP_EMULATOR:-0}" == "1" ]]; then
  echo "⏭️ AUTOCREATE_SKIP_EMULATOR=1 — Phase 10.5 SKIPPED on request."
  export SKIP_SCREENSHOTS=1
elif [[ "${PLATFORM:-web}" == "android" ]]; then
  # An explicit Android request (--platform android). We do NOT start an emulator/AVD/KVM —
  # this is only a compile verification of the Gradle build; see 10.5.2c.
  echo "🤖 PLATFORM=android → Gradle compile-only verification (no emulator, no screenshots)."
fi

# The web path (the default): needs node + Chrome. Without them, the only honest answer is SKIP.
if [[ "${SKIP_SCREENSHOTS:-0}" != "1" && "${PLATFORM:-web}" == "web" ]]; then
  if [[ $HAVE_NODE -eq 1 && -n "$CHROME_BIN" ]]; then
    echo "🌐 Web path: node=$(node -v) chrome=$CHROME_BIN"; export PLATFORM=web
  else
    echo "⚠️ No node ($HAVE_NODE) or Chrome ('$CHROME_BIN') — web verification is impossible. SKIPPED."
    export SKIP_SCREENSHOTS=1
  fi
fi

# NDK pre-flight — ONLY for the Android compile-only verification (web does not build Gradle).
if [[ "${PLATFORM:-web}" == "android" ]]; then
  command -v sdkmanager &>/dev/null && { sdkmanager --list_installed 2>/dev/null | grep -q "ndk;27" || \
    sdkmanager "ndk;27.0.12077973" 2>/dev/null || echo "⚠️ NDK install failed"; }
  if [[ -f android/app/build.gradle ]] && ! grep -q "ndkVersion" android/app/build.gradle; then
    python3 - <<'PY'
import re, pathlib
bg = pathlib.Path("android/app/build.gradle"); src = bg.read_text()
src = src.replace("android {", 'android {\n    ndkVersion "27.0.12077973"', 1)
src = re.sub(r'minSdkVersion\s+\d+', 'minSdkVersion 21', src); bg.write_text(src)
print("✅ Patched build.gradle: ndkVersion + minSdkVersion 21")
PY
  fi
fi
```

**The transition criterion:**
- If `SKIP_SCREENSHOTS=1` (an explicit opt-out, or no node/Chrome for web) —
  **do NOT run** 10.5.2; go straight to Phase 11 with the verdict **SKIPPED**. That is a normal
  path, NOT an error: the pipeline counts as successful (the game was already built and tested in
  Session 2).
- Otherwise (`PLATFORM=web` with node+Chrome, or `PLATFORM=android` — no device or emulator is
  needed for the latter, it is compile-only) — continue with 10.5.2.

### 10.5.2 — runtime tour / compile verification (only when NOT SKIP_SCREENSHOTS)

**The web path (the default)** — self-contained commands (details in `emulator-test/SKILL.md`):

```bash
mkdir -p .claude/runtime-logs
WEB_PORT=8099

# 1) A headless dev server (it does not open a browser)
nohup flutter run -d web-server --web-port "$WEB_PORT" --web-hostname 127.0.0.1 \
  > .claude/runtime-logs/flutter-run.log 2>&1 &
echo $! > .claude/runtime-logs/flutter.pid

# 2) Wait for the URL, with an early exit on a build error (so it cannot hang)
WEB_URL=""
for i in $(seq 1 120); do
  WEB_URL=$(grep -oE "http://127\.0\.0\.1:[0-9]+" .claude/runtime-logs/flutter-run.log 2>/dev/null | head -1)
  [ -n "$WEB_URL" ] && break
  grep -qE "Failed to compile|Target dart2js failed|Compilation failed|^Error: " .claude/runtime-logs/flutter-run.log 2>/dev/null && break
  sleep 2
done

TS=$(date +%Y%m%d-%H%M%S); SHOT_DIR="production/runtime-screenshots/$TS"; mkdir -p "$SHOT_DIR"

if [ -n "$WEB_URL" ]; then
  # 3) Canonical phone tour plus the rest of the portrait phone matrix.
  timeout 220 node tools/web_verify.mjs --url "$WEB_URL" --out "$SHOT_DIR" \
    --size 390x844 --budget 180 --quick \
    2>&1 | tee "$SHOT_DIR/web_verify.log"
  for VIEWPORT_SIZE in 360x640 360x800 430x932; do
    VIEWPORT_DIR="$SHOT_DIR/$VIEWPORT_SIZE"; mkdir -p "$VIEWPORT_DIR"
    timeout 140 node tools/web_verify.mjs --url "$WEB_URL" --out "$VIEWPORT_DIR" \
      --size "$VIEWPORT_SIZE" --budget 120 --quick \
      2>&1 | tee "$VIEWPORT_DIR/web_verify.log"
  done
  # 4) Wide-host smoke capture: NOT a design target. It only proves a desktop browser shows the
  #    phone column over the campaign surround instead of a stretched game.
  mkdir -p "$SHOT_DIR/wide-host"
  timeout 90 node tools/web_verify.mjs --url "$WEB_URL" --out "$SHOT_DIR/wide-host" \
    --size 1440x900 --budget 60 --quick \
    2>&1 | tee "$SHOT_DIR/wide-host/web_verify.log"
else
  echo "❌ the web server did not come up — the build is broken. Log: .claude/runtime-logs/flutter-run.log" \
    | tee "$SHOT_DIR/web_verify.log"
fi

# 5) Server cleanup (the script kills its own headless Chrome)
kill "$(cat .claude/runtime-logs/flutter.pid 2>/dev/null)" 2>/dev/null || true
```

Then:
- **Visual analysis** of each `$SHOT_DIR/*.png` through Read (vision) against the V1–V23 checklist,
  `.claude/docs/mobile-first-contract.md`, and `.claude/docs/gameplay-screen-contract.md`.
  For a named `examples-games/` game, compare the mapped source files beside the menu and
  idle/active gameplay captures. Record wrong character, symbol, background, palette, topology,
  finish or composition as HIGH V21 and route the fix to art or UI before a PASS verdict.
  Inspect the portrait phone matrix at 360×640, 360×800, 390×844 and 430×932, with idle and
  active gameplay at 390×844 and 360×640. These are the only design gates: there is no
  landscape, tablet or desktop layout to verify, and one found in the code is V17. The wide-host
  capture must show the unchanged phone composition in a centered column over the campaign
  surround — never a stretched or recomposed game, and never a device bezel.
- **Error parsing**: inspect every `manifest.json` and `webconsole.log` under `$SHOT_DIR`,
  and `.claude/runtime-logs/flutter-run.log` (EXCEPTION CAUGHT, RenderFlex overflowed, Unable to load asset).
- **Asset distortion (V18)**, **menu composition/role (V19)**, **gameplay-field centering (V20)**
  the **campaign background (V22)** and the **approved gameplay sample (V23)**: run steps
  10.5.2d–10.5.2h below. A screenshot that "has
  the sprite in it" is not proof the sprite kept its shape, a menu that renders is not proof it
  shows the game, a field that is on-screen is not proof it is centered, and a background that
  loads is not proof it is the campaign's.

### 10.5.2c — Android compile verification (only when `PLATFORM=android`)

Android here is **NOT** a runtime tour. No emulator/AVD, no screenshots, no `adb logcat`. The
only goal is to confirm that the Gradle project really compiles (including that the NDK/minSdk
patches from 10.5.1 worked). Full runtime verification of the game already happens through web
(Chrome/CDP) above; the Android path answers only "does it compile", not "does it work on a
device" — and for that you need no emulator, KVM or hardware.

```bash
mkdir -p .claude/runtime-logs
timeout 600 flutter build apk --debug 2>&1 | tee .claude/runtime-logs/android-build.log
ANDROID_BUILD_EXIT=${PIPESTATUS[0]}

if [[ "$ANDROID_BUILD_EXIT" == "0" ]]; then
  echo "✅ Android Gradle compile OK — the app builds."
else
  echo "❌ Android Gradle compile FAILED — see .claude/runtime-logs/android-build.log"
fi

# This is a verification, not a release artifact — the APK is not kept or packaged.
rm -f build/app/outputs/flutter-apk/app-debug.apk 2>/dev/null || true
```

Compile errors (Gradle/Kotlin/NDK/platform Dart code) are handled the same way as the
`dart analyze` errors in Phase 6 of `autocreate-implement`: routed to
mechanics-programmer/ui-programmer, with up to 2 iterations of editing and re-running
`flutter build apk --debug`. Packaging (`flutter build apk --release`, the AAB, signing,
archiving) is not part of this — that is a separate, explicit `/release-package` on request.

### 10.5.2b — soak / leak probe (web, optional but recommended)

A complete game must survive a long session without memory growth or exceptions. If the web path
is active, run a short soak: ~150–200 automated actions (repeating the main game action plus
screen transitions) and compare the heap at the start and the end, plus the accumulation of
console errors.

```bash
# web_verify.mjs --soak N runs N action→wait cycles and records heapUsedStart/End
# (if the flag is not supported in the current version, skip it — this is not a blocker).
timeout 180 node tools/web_verify.mjs --url "$WEB_URL" --out "$SHOT_DIR" --soak 150 \
  2>&1 | tee -a "$SHOT_DIR/web_verify.log" || echo "soak skipped"
```

The sign of a leak: monotonic growth in `JSHeapUsedSize` with no plateau after GC, or a growing
number of repeated console exceptions. Whatever is found goes into REPORT.md as HIGH (not
CRITICAL, if the game is playable); a targeted fix (an un-disposed controller/timer/particle
leak) is permitted.

### 10.5.2d — asset distortion audit (V18) [~20 s]

An asset drawn at a different aspect ratio than its source file is one of the most visible
"AI made this" tells, and it passes every other gate: the analyzer is clean, the widget test is
green, the sprite is present in the screenshot — and the jester is 40% wider than the artwork
the art director approved.

```bash
python3 tools/check_asset_stretch.py \
  --assets assets --lib lib --warn 0.05 --fail 0.10 \
  --report "$SHOT_DIR/asset-stretch.md" --json "$SHOT_DIR/asset-stretch.json"
STRETCH_EXIT=$?   # 0 = no HIGH finding, 1 = at least one HIGH, 2 = bad invocation
```

The script reads each asset's real pixel dimensions from its file header and compares them with
the box the Dart code draws it in, reporting only the operators that actually deform artwork:
`BoxFit.fill` on a box whose ratio differs from the source, a Flame `size: Vector2(w, h)` off the
sprite's ratio (Flame stretches to `size:` — it does not letterbox), and a non-uniform
`Transform.scale`. MEDIUM at 5% aspect deviation, HIGH at 10%. A plain `Image.asset(width:,
height:)` is not reported: Flutter letterboxes it under the default fit.

Then the vision confirmation, which is the part the script cannot do (it cannot see a box computed
from runtime constraints):

- Read the source file and the runtime screenshot **together** for every character/hero asset, the
  app icon, the primary action button and every site the report lists, and compare the silhouette
  proportions — a circle still circular, a face still the right width, baked-in lettering not
  slanted or condensed.
- Judge the ratio, not the size. Drawing a 512×512 sprite at 64×64 is correct; drawing it at
  96×64 is V18.
- Check the tallest and shortest phones specifically (430×932, 360×640): a background or panel
  that is honest at 390×844 is often the one squeezed on a short phone, and check the wide-host
  surround is `BoxFit.cover`, not stretched.

Every confirmed finding is **V18, HIGH** and enters the 10.5.3 auto-fix loop. Fix the draw site,
never the source artwork: switch to `BoxFit.contain`/`BoxFit.cover`, make the box match the source
ratio, or derive one side from the other. Re-exporting a sprite to fit a wrong box, or regenerating
the asset, is not a fix. A genuinely deliberate non-uniform scale (a 9-slice panel, a full-bleed
gradient backdrop) is recorded with a `stretch-ok` comment on the draw site, which also suppresses
the static finding.

### 10.5.2e — main-menu lead audit (V19) [~20 s]

`quality-bar.md` §1: the menu must implement the memorable idea and M/O/P recipe recorded in
`design/art-direction.md`. The storefront lead does not automatically become a runtime-menu
centrepiece: the design docs record `menu_role: dominant | supporting | absent` separately from
`lead_kind`.

```bash
python3 tools/check_menu_lead.py \
  --lib lib --assets assets --min-side 120 \
  --report "$SHOT_DIR/menu-lead.md" --json "$SHOT_DIR/menu-lead.json"
MENU_LEAD_EXIT=$?   # 0 = no HIGH finding, 1 = at least one HIGH, 2 = bad invocation
```

The script reads `lead_kind`, `menu_role`, and the lead asset out of
`design/gdd/game-concept.md` / `design/art-direction.md` / `design/asset-manifest.md`. For a
dominant or supporting character role, it checks that the main-menu source actually draws the
asset. If the concept never recorded the role, it says so as a MEDIUM instead of guessing — read
the concept and re-run with `--lead-kind`, `--menu-role`, and `--lead-asset` as needed.

Then judge `02-menu.png` at 390×844 and 360×640, which is the half the script cannot do:

- the documented M/O/P recipe is recognizable and its attention order is intentional;
- a dominant or supporting lead is visible on the first viewport and important features are not
  accidentally clipped or buried by controls;
- a dominant lead actually leads; a supporting lead supports; an absent lead is not reintroduced
  just to satisfy a generic menu pattern;
- its alignment and crop follow the recorded recipe instead of an undocumented centering default;
- the short phone preserves that relationship rather than pushing the lead under the controls.

A confirmed failure is **V19, HIGH** and enters the 10.5.3 loop: restore the documented menu role
or attention order with a targeted edit on the menu screen.

> **Never satisfy V19 by inventing a character or forcing the storefront lead into the menu.**
> Object- and mechanic-led games may use their object or field as dominant, supporting, or absent
> according to the documented recipe. Adding a mascot, host, hand, or player silhouette is its own
> defect (`.claude/docs/visual-context.md`).

### 10.5.2f — gameplay-field centering audit (V20) [~20 s]

`gameplay-screen-contract.md` §2b: absent a documented reason, the live play field sits centered
on the viewport's horizontal axis. A field shoved against one edge passes every other gate (the analyzer is clean,
the widget test only checks the field is on-screen and above the size floor, the screenshot "has
the field in it") while still reading as unintentional.

```bash
python3 tools/check_gameplay_center.py \
  --lib lib --warn-px 16 --fail-px 48 \
  --report "$SHOT_DIR/gameplay-center.md" --json "$SHOT_DIR/gameplay-center.json"
GAMEPLAY_CENTER_EXIT=$?   # 0 = no HIGH finding, 1 = at least one HIGH, 2 = bad invocation
```

The script finds every `Key('gameplaySurface')` site (the mandatory hook from
`gameplay-screen-contract.md`) and walks its ancestor widgets for an explicit horizontal offset:
an `Align`/`Alignment` pinned toward an edge, asymmetric `Padding`, or a `Positioned` pinned to
one side or given unequal `left`/`right` insets. It cannot resolve the box that runtime
constraints (parent size, safe-area insets, `Expanded` siblings) actually produce, so the vision
pass is not optional:

- Read `03-game-idle.png` and `04-game-action.png` at 390×844 and 360×640 together with the
  state recipe recorded in `design/art-direction.md`.
- The field's horizontal center should sit inside the middle 60% of the viewport width.
- An off-center placement is fine when the recorded state recipe genuinely calls for it (for
  example, an edge rail or split relationship), but that reason has to be written down in
  `design/art-direction.md`, not just visible in the screenshot; an unexplained offset is V20.
- A width-based layout branch that moves the field is itself a defect (V17): there is no
  desktop reflow to drift into.

Every confirmed finding is **V20, HIGH** and enters the 10.5.3 auto-fix loop. Fix the offending
`Padding`/`Align`/`Positioned` so the field's center returns to the viewport's center, or — only
when the composition genuinely calls for an offset — record the reason in
`design/art-direction.md` rather than leaving it silent.

### 10.5.2g — campaign background audit (V22) [~1 min]

Session 2 built the game on the campaign background (Phase 10.4 confirmed it); this proves it
arrived. Read
`production/store-art/campaign.md`, `shared-background.png` and `background-crops.png`, then the
menu and game captures at all four phone sizes:

- `rg -n 'bg_campaign' lib` finds the menu, the splash route, the secondary screens that showed
  the shared scene, and the game screen; no screen still selects the replaced background;
- the menu shows the whole character (or the lead object) — nothing cut by the screen edge,
  nothing covering the face;
- the game screen uses `bg_campaign_game.png`; the field keeps its contract size and position,
  and where the recipe leaves the upper band open the character's head shows above it;
- the picture is `BoxFit.cover` with top alignment — never stretched (V18), never letterboxed;
- the wide-host capture uses the campaign picture as the column's surround.

A confirmed failure is **V22, HIGH** and enters the 10.5.3 loop as a targeted wiring edit. A
background that cannot fit its character is not a wiring defect: it goes back to campaign-art.md's
review, and the campaign stays BLOCKED until it passes.

### 10.5.2h — approved gameplay sample audit (V23) [~1 min]

The user approved the game by its concept carousel, and the carousel's gameplay is the field the
game promised (`production/store-art/concept/gameplay-sample.md`). Read `gameplay-sample.png` and
the spec together with `04-game-action.png` (and `03-game-idle.png`) at 390×844 and 360×640, and
compare — the runtime field is the same board seen square-on; the camera angle, the flying balls,
the lower-edge spill and the scenery are marketing-only:

- **topology** — the same columns × rows (or the same field layout for a non-grid mechanic);
- **symbols** — the same cast, the same art, recognisably the same pieces;
- **board housing and tile backing** — the same material, colour, ornament and plate shape;
- **the clearing moment** — the active capture's match/merge/shot treatment reads like the sample's
  (its glow colour, ring, lift or spill light);
- **palette and light** on the field — the same family, no re-themed field.

A field that would make the user say "that is not the game I approved" is **V23, HIGH**: a
generic grid where the sample had an ornate housing, different tile plates, missing symbols, a
different board size, a flat clear where the sample promised a lit one. It enters the 10.5.3 loop.
Skip V23 only for a LEGACY project (no concept record); say so in REPORT.md.

### 10.5.3 — the auto-fix loop (up to 3 iterations)

Consolidate the problems, mark their severity (CRITICAL/HIGH/MEDIUM) and assign agents:
- V2/V3/V5/V7/V8/V9/V10/V11/V13/V14/V15/V16/V17/V18/V19/V20/V22 → **ui-programmer**
- V23 → **ui-programmer** for housing, plates, spacing and layout; **juice-artist** for the
  clearing moment; **art-director** when the asset itself does not match the sample (generate the
  missing piece from `gameplay-sample.png` as in implement Phase 4.0 — never a crop of the panorama)
- V4/V12 → **mechanics-programmer**
- V18 on a Flame component `size:` → **juice-artist** or **mechanics-programmer**, whoever owns
  the component
- V21 → **art-director** for asset identity/finish or **ui-programmer** for screen composition
- VFX not visible → **juice-artist**
- Logcat asset errors → check `lib/assets.dart` against the real files

**Permitted auto-fixes:**

| Symptom | Cause | Auto-fix |
|---------|-------|----------|
| An empty black rectangle instead of the play field | The components were not added in World.onLoad() | `await world.addAll([...])` |
| The HUD shows null/NaN | The ValueNotifier was never initialised | Initialise it in the Game constructor |
| The splash is black and never advances | There is no Timer for navigation | `Future.delayed → pushReplacementNamed` |
| A white screen after PLAY | The route is not registered | Add it to the `routes:` map in app.dart |
| Yellow overflow stripes | A ListView with no Expanded | Wrap it in Expanded |
| A red screen exception | A null check/type error from the stack trace | Fix it at the file:line from the log |
| "Unable to load asset" | A path mismatch in `lib/assets.dart` | Fix the path, or create the file |
| Slight field/control constraint miss | An avoidable wrapper, padding, or incorrect flex | Make a targeted constraint edit and re-capture both idle and active states |
| An asset is stretched or squashed (V18) | `BoxFit.fill`, a Flame `size:` off the source ratio, or a non-uniform `Transform.scale` | Fix the draw site: `BoxFit.contain`/`cover`, a box matching the source ratio, or derive one side from the other — never re-export or regenerate the asset |
| The documented menu role or composition is not realized (V19) | The runtime menu contradicts its M/O/P recipe, attention order, or `menu_role` | A targeted menu-screen edit that restores the documented relationship — never invent a character or force a storefront lead into an `absent` role |
| The play field sits off-center (V20) | An unexplained `Padding`/`Align`/`Positioned` offset on an ancestor of `Key('gameplaySurface')` | Remove the offset so the field's horizontal center returns to the viewport's, or record and verify the state recipe/mechanic reason in `design/art-direction.md` |
| A screen still shows the old background, or the campaign picture is stretched/letterboxed (V22) | A missed selector, or a fit/alignment other than `BoxFit.cover` + top | Point the selector at `bg_campaign_menu`/`bg_campaign_game`, set `BoxFit.cover` + `Alignment.topCenter` |
| The live field does not read as the approved gameplay sample (V23) | A board drawn in code where the sample shows a housing asset, wrong tile plates or spacing, a missing clear treatment | Targeted edits to the field's frame/tile widgets and the clear effect so they follow `gameplay-sample.md`; a missing asset is generated from the sample crop (art-director) — topology and rules stay as the frozen data define them |
| A desktop/tablet/landscape layout branch, or a wide host that stretches the game (V17) | A width breakpoint or a missing phone column | Delete the branch so every width renders the phone composition; wrap `MaterialApp.builder` in the phone column from `mobile-first-contract.md` |

**Forbidden "auto-fixes":**
- Changing `game_config.dart` (the balance is frozen)
- Changing `level-config.json` / `endless-config.json` / `assets/data/levels.json`
- Adding any wager, currency, chance-based reward, casino control, gambling copy or age gate
- Rewriting whole screens — targeted edits only
- Changing the GDD

If V13–V17 require structural recomposition rather than a targeted constraint edit, do not hide
or downgrade the defect. Mark finalization FAIL and route it back to `/ui-audit --fix` or
`/autocreate-implement --resume`; Session 2 owns whole-screen composition.

### 10.5.4 — Phase 10.5's exit criterion

**The web path (the default):**
- **Success**: 0 CRITICAL + 0 HIGH visual problems, 0 FATAL exceptions, the asset-distortion,
  menu-lead and gameplay-centering audits report no HIGH finding (`STRETCH_EXIT=0`,
  `MENU_LEAD_EXIT=0`, `GAMEPLAY_CENTER_EXIT=0`, and the vision confirmations agree), V22 and V23 pass,
  and the gameplay-screen contract passes in idle and active states at every phone size
- **Partial success**: CRITICAL/HIGH are cleared but MEDIUMs remain — go on to Phase 11 with CONCERNS
- **Failure**: after 3 iterations any CRITICAL/HIGH remains — save
  `production/runtime-screenshots/<ts>/REPORT.md`, report with the verdict FAIL;
  Phase 11 runs anyway (active.md is updated with the FAIL verdict)

**The Android path (`PLATFORM=android`, compile-only):**
- **Success**: `flutter build apk --debug` finishes with exit code 0 (`ANDROID_BUILD_EXIT=0`)
- **Failure**: after 2 auto-fix iterations the compile errors remain — the verdict is FAIL, with
  the reason from `.claude/runtime-logs/android-build.log`; Phase 11 runs anyway
- There is no notion of CRITICAL/MEDIUM visual problems here — this is not a runtime tour

### 10.5.5 — artifacts

**The web path:**
- `production/runtime-screenshots/<ts>/*.png` — the shots
- `production/runtime-screenshots/<ts>/REPORT.md` — the verdict PASS/CONCERNS/FAIL
- `production/runtime-screenshots/<ts>/asset-stretch.md` + `.json` — the V18 audit
- `production/runtime-screenshots/<ts>/menu-lead.md` + `.json` — the V19 audit
- `production/runtime-screenshots/<ts>/gameplay-center.md` + `.json` — the V20 audit
- `.claude/runtime-logs/flutter-run.log`

**The Android path (compile-only):**
- `.claude/runtime-logs/android-build.log` — the `flutter build apk --debug` log
- No screenshots/logcat/APK files — this verification saves nothing as an artifact

Cleanup: stop `flutter run` using the PID in `.claude/runtime-logs/*.pid` (the web path).

---

## Phase 10.6 — playtest (a real gameplay session) [~6 min]

> Phase 10.5 checked that "the screens open and do not crash". This phase checks that "it is
> actually PLAYABLE": moves produce results, the score changes, clears are celebrated, the board
> responds. The benchmark is `.claude/docs/quality-bar.md` (§2–§4, §6, §7).

Run the `.claude/skills/playtest/SKILL.md` runbook (if the web path was SKIPPED in 10.5, or if
10.5 went down the Android compile-only path, this phase is honestly SKIPPED too — that is not an
error: playtest needs a genuinely running instance over CDP, and compile-only launches nothing):

- The tour + gameplay load (`web_verify.mjs --soak 60`) → the **P1–P10** checks
  (vision comparison of frames: the move changes the field, the HUD numbers change, clear/combo
  feedback is visible, and active-state motion communicates the result; a deliberately still idle
  state is valid; manifest: 0 consoleErrors, suspectLeak=false).
- Verdict: **PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED** →
  `production/playtest/<ts>/PLAYTEST-REPORT.md`.
- On a CRITICAL (P1/P2/P8), run an auto-fix loop of up to 2 iterations against the same table of
  permitted fixes as in 10.5.3 (targeted wiring edits only; NOT balance, NOT rewriting screens).

**Exit criterion:** PLAYTEST-REPORT.md exists; the verdict is ≠ NOT-PLAYABLE (or the 2 iterations
are exhausted — then the verdict is recorded honestly and reaches the final report as the FAIL
reason).

---

## Phase 11 — session state update [~1 min]

Update `production/store-art/campaign.md` with the final capture/report paths and the actual
background integration verdict. Keep an incomplete art phase marked BLOCKED in session state.

Update `production/session-state/active.md`:

```markdown
<!-- STATUS -->
Epic: [Game Name]
Feature: Complete Game
Task: Production-ready
<!-- /STATUS -->

## Status
[If the campaign background, the approved gameplay sample (V23) and runtime/playtest/layout pass: The game is fully
implemented and verified. The store kit (/store-screenshots) follows. To get the APK and the archive, run /release-package.]
[If the campaign background is incomplete or any CRITICAL/HIGH or NOT-PLAYABLE remains: RELEASE BLOCKED. Return to /ui-audit --fix or
/autocreate-implement --resume; do not run /release-package or /store-screenshots yet.]

## Runtime verification
- Verdict: [PASS / CONCERNS / FAIL / SKIPPED]
- Screenshots: production/runtime-screenshots/<ts>/
- Report: production/runtime-screenshots/<ts>/REPORT.md

## Campaign
- Approved concept: production/store-art/concept/concept.json (revision [N], approved [date])
- Gameplay sample (V23): [PASS / FAIL / LEGACY, evidence paths]
- Handoff: production/store-art/campaign.md
- Shared background: production/store-art/shared-background.png (in the approved panorama's world)
- Integration and visual verdict (V22): [PASS / BLOCKED, evidence paths]
- Banner: made by the store kit from the approved panorama

## Session 2's tests
- Unit: [N] green
- Integration: [N] green
- Edge cases: [N] green

## Balance
[The balance run's verdict from Session 2: the model B1–B6, the key metrics, PASS/CONCERNS/FAIL]
```

Also mark the handoff file as finished: append a final
`## Session 3 finished` section to `production/session-state/autocreate-handoff.md`, with an
ISO timestamp and the verdict.

Write the verdict the web service reads to decide whether the store kit follows:

```bash
cat > production/session-state/finalize-verdict.json <<'JSON'
{
  "schema_version": 1,
  "verdict": "PRODUCTION_READY",
  "runtime": "PASS",
  "playtest": "PLAYABLE",
  "campaign_background": "PASS",
  "gameplay_sample": "PASS",
  "blockers": [],
  "finished_at": "<ISO timestamp>"
}
JSON
```

`verdict` is `PRODUCTION_READY` exactly when Phase 12's report says
`AUTOCREATE COMPLETE — PRODUCTION READY`, and `BLOCKED` otherwise, with every blocker listed in
one line each. Write it from the evidence, never optimistically.

---

## Phase 11.5 — release engineering prep (NO build) [~3 min]

Run `/release-engineering --prep-only --no-keystore`
(see `.claude/skills/release-engineering/SKILL.md`). **The AAB/APK build does NOT happen here** —
the goal is to leave the project READY for `/release-package` without spending time on a heavy
Gradle build:
- App icons (Android adaptive + iOS + web) and a native splash from the Design DNA.
- The version/build number and the launcher label.
- `store/` — the listing stubs (casual category, "simulated gambling: no"), privacy policy, data
  safety, and the age rating from the content alone (normally Everyone / PEGI 3; no age gate).
- `.github/workflows/build.yml` (CI).
- It does **NOT** generate an upload keystore and does **NOT** build the AAB/APK.

```bash
# A safe prep: it creates no keystore, publishes nothing externally and builds no artifacts.
flutter pub get >/dev/null 2>&1 || true
# If release-engineering is unavailable as a skill, do only the prep steps by hand:
#   dart run flutter_launcher_icons ; dart run flutter_native_splash:create
#   (do NOT run flutter build appbundle/apk here — that is /release-package's job)
```

> If the source icon `assets/branding/app_icon.png` is missing, generate it from the branded
> logo/sprite (rasterise the SVG at 1024×1024) before running launcher_icons.

**Exit criterion:** the icons and splash are generated and `store/` exists. The artifacts
(AAB/APK) are NOT built — `/release-package` builds those. For a signed Play AAB, the user runs
`/release-engineering` (with no flags), which mints the keystore and builds the signed AAB.

---

## Phase 12 — the final report

Print to the user (or, when invoked as a sub-agent, return it to the parent session). Use
`AUTOCREATE COMPLETE — PRODUCTION READY` only when runtime has 0 CRITICAL/HIGH issues, the
gameplay-screen contract passes, playtest is not NOT-PLAYABLE, the campaign background is
integrated and verified (V22), and the live field matches the approved gameplay sample (V23).
Otherwise use `AUTOCREATE BLOCKED — UI/GAMEPLAY REWORK REQUIRED` and put the blocking rerun
command first.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 AUTOCREATE COMPLETE — PRODUCTION READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Screens (12+):
   ✅ Splash, Main Menu, Level Map / Mode Select, Game Screen + HUD, Pause
   ✅ Level Complete (stars), Level Failed / Run Over, How to Play, Settings
   ✅ Achievements, Collection Album, Stats / Profile, Daily Challenge

🎮 Gameplay:
   ✅ Core game loop works end-to-end
   ✅ [Category]: [board engine / deal solver / merge engine / physics / tempo ramp / level solver] fully functional
   ✅ Logic before animation, one seeded GameRng, GameState sealed class
   ✅ All constants in GameConfig, double-tap protection, no dead ends
   ✅ No gambling: no wagers, currency, chance-based rewards or age gate
   [If the request named a gambling mechanic: "Built as <casual mechanic> — the studio does not make gambling games"]

🗂 Content and modes (Phase 4.5):
   ✅ [N] levels/stages (assets/data/*.json) | Modes: [Classic + Endless/Time-Attack/Daily]
   ✅ Level/Mode Select is wired to the real data

🧩 Meta systems (Agent E):
   ✅ SaveService (versioned), Progression (stars + unlocks), Achievements, Collection album, Daily challenge
   ✅ Analytics/Ads/IAP/RemoteConfig — abstractions (no-op, no external SDKs)

🔊 Audio (Phase 3.5):
   ✅ 8 real .wav sound effects synthesised (mood: [mood]) — not placeholders
   ℹ️ No background music by design (SFX-only); not a gap, do not list it as one

🧪 Tests (Session 2):
   ✅ Unit: [N] passed | Integration: [N] passed | Edge: [N] passed

🌐 Runtime verification (Chrome, Phase 10.5):
   [PASS / CONCERNS / FAIL / SKIPPED] — [N] CRITICAL, [N] HIGH issues
   Gameplay composition: [PASS / FAIL / UNVERIFIED] — portrait phone screen, dominant field + integrated controls, centered by default (V20)
   Campaign background in game (V22): [PASS / FAIL / BLOCKED]
   Field vs. the approved gameplay sample (V23): [PASS / FAIL / LEGACY]
   Screenshots: production/runtime-screenshots/<ts>/
   Report: production/runtime-screenshots/<ts>/REPORT.md

🕹 Playtest (Phase 10.6 — a real gameplay session):
   [PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED]
   P1–P10: [briefly — e.g. "P1–P8 PASS, P9 leak-suspect, P10 PASS"]
   Report: production/playtest/<ts>/PLAYTEST-REPORT.md

⚖️ Balance (Session 2):
   [Model B1–B6: e.g. "L1–3 ≥ 92%, hardest 31%, ramp +58 pp" — PASS/CONCERNS/FAIL]
   [The report is in design/balance/simulation-report.md]

🎨 Campaign (approved concept → game → store):
   Approved concept: revision [N] — production/store-art/concept/ (the carousel the user approved)
   Game background: production/store-art/shared-background.png → assets/images/backgrounds/bg_campaign_*.png
   (rendered in the approved panorama's world) — [PASS / BLOCKED]
   Next: /store-screenshots exports the approved panorama unchanged as the carousel, renders the
   banner in its world, and puts the phone slides on this same game background

🚀 Release-ready (Phase 11.5, PREP — no build):
   ✅ Icons (Android adaptive + iOS + web) + a native splash (colour from the DNA)
   ✅ Version [name]+[build], store/ (listing + privacy + data-safety + age-rating)
   ⚙️ .github/workflows/build.yml (CI)
   ℹ️ The AAB/APK were NOT built — the project is ready to be packaged

📦 Building artifacts / publishing (an explicit user action):
   /release-package                 — build the AAB+APK + screenshots + sources → one .zip
   /release-engineering             — mint the upload keystore → a SIGNED .aab for Google Play

🔧 Commands to run it:
   flutter run -d chrome        — run in Chrome
   flutter run                  — run on an available device
   flutter test                 — run the tests
   adb install project_zip/[name]-[ts]/apk/*.apk — install the APK (if there is one)

📋 Recommended re-runs:
   /emulator-test               — REPEAT the runtime verification
   /release-package             — REPEAT the release packaging
   /autocreate-finalize         — re-run the whole of Session 3

📋 Optional next steps:
   /add-feature [feature]       — add a mechanic
   /code-review                 — a full code review
   /balance-check               — a detailed balance check (full curve)
   /perf-profile                — performance profiling
   /release-checklist           — the final GO/NO-GO checklist before a store release
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Phase 13 — the store kit

A production-ready game goes straight on to its store listing, built from the same approved
panorama: `/store-screenshots` exports it unchanged as the carousel slides (crops, grading and the
detail pass only), renders the banner in its world, puts real captures of this game on its
background, and packages the kit.

```bash
echo "store kit: ${AUTOCREATE_STORE_KIT:-agent}"
```

- `AUTOCREATE_STORE_KIT=service` (the web service sets it) or `--no-store-kit` → do not start it:
  the service runs `/store-screenshots` as its own run after reading `finalize-verdict.json`. End
  here.
- Otherwise, when the verdict is `PRODUCTION_READY`, spawn a clean-context agent:

```text
You are the store-kit session of /autocreate. Read .claude/skills/store-screenshots/SKILL.md and
run it with its defaults. The concept panorama the user approved is production/store-art/concept/
— export it unchanged (its recorded export flags; crops, grading and the detail pass only) and
render the banner in its world. Return the ZIP path, the check_store_kit.py result and any blocker.
```

- When the verdict is `BLOCKED`, do not start the store kit: the listing would show a game that
  fails its own gates. The report names the blockers and says the store kit follows their fix
  (`/store-screenshots`).

---

## Quality gates

| Phase | Exit criterion | Max iterations |
|-------|----------------|----------------|
| 0. Preflight | The handoff exists + `dart analyze` 0 errors | 1 (fail-fast) |
| 10.4. Campaign check | The approved concept passes `concept_gate.py check`; the background (rendered in the approved panorama's world, character whole in frame) is ACCEPTED and selected by every screen; campaign.md complete; analyzer/tests pass | Only when missing: fresh renders from original references + the approved panorama; at most one whole-frame edit; region repairs for local defects (art-lineage.md) |
| 10.5. Runtime Chrome / Android compile | Web: 0 CRITICAL/HIGH visual at every phone size, gameplay-screen contract PASS, no HIGH in the V18 asset-distortion, V19 menu-composition/role, V20 gameplay-centering, V22 campaign-background or V23 approved-gameplay-sample audits, wide host shows the phone column, 0 FATAL in flutter-run.log (+ soak: no leak). Android (`--platform android`): `flutter build apk --debug` exit 0 | 3 (Chrome is always available) / 2 (Android compile) |
| 10.6. Playtest | PLAYTEST-REPORT.md, verdict ≠ NOT-PLAYABLE (P1–P10) | 2 |
| 11. Session state | `active.md` updated | 1 |
| 11.5. Release-eng prep | Icons/splash generated, `store/` created (AAB best-effort) | 1 |
| 12. Final report | The report was printed / returned; `finalize-verdict.json` written | 1 |
| 13. Store kit | PRODUCTION_READY → `/store-screenshots` started (or left to the web service); BLOCKED → not started, and the report says why | 1 |

**THE ABSOLUTE MINIMUM to finish Session 3:**
- `production/session-state/active.md` is updated
- The final report is printed, with the runtime verification verdict

This minimum permits an honest blocked report; it does not permit a production-ready claim. Any
remaining V13–V23/HIGH defect, a BLOCKED campaign background, or a failed mobile-phone/gameplay-screen contract keeps the project blocked.

---

## Recovery after a failure

**If the sub-agent crashed mid-Session 3**, the user runs `/autocreate-finalize` in a new
conversation. The skill:
1. Reads `autocreate-handoff.md` and `active.md`
2. Works out which phase to continue from (by which artifacts exist):
   - `production/store-art/campaign.md` missing, the background not ACCEPTED, or `bg_campaign_*`
     not wired → start at 10.4 (reusing every campaign file that still validates)
   - No `production/runtime-screenshots/<ts>/` and no `.claude/runtime-logs/android-build.log` → start at 10.5
   - There are shots (or, on the Android path, an `android-build.log` with exit 0) but no
     `production/playtest/<ts>/PLAYTEST-REPORT.md` → start at 10.6 (on the Android path this step
     is honestly SKIPPED — go straight to 11)
   - There is a playtest report (or the Android path reached the SKIPPED playtest) but `active.md`
     has not been updated → start at 11
3. Continues from that phase without redoing what is done

**If web verification is impossible** (no `node` or no Chrome binary): `web_verify.mjs` cannot
run — Phase 10.5 is SKIPPED as normal and we go to Phase 11 with the verdict SKIPPED (the game
was already built and tested in Session 2). To enable web verification: install `node` (≥21, for
the built-in WebSocket) and Chrome/Chromium (`google-chrome`/`chromium`), or point
`$CHROME_EXECUTABLE` at the binary. This does NOT block Session 3 from finishing.

**If it hangs on Phase 10.5** — it should not: `web_verify.mjs` terminates itself on `--budget`,
there is a `timeout` on top of it, and `flutter run -d web-server` exits early on a build error.
If it does hang anyway, kill `$(cat .claude/runtime-logs/flutter.pid)` and any orphaned
`google-chrome --headless` processes, mark the verdict SKIPPED and move to Phase 11.
Note `CHROME_SKIPPED: true` in `RELEASE_INFO.md`.
