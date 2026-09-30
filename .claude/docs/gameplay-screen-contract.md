# Gameplay Screen Contract — Full-Screen, Integrated, Portrait Phone

This contract prevents a working mechanic from being presented as a small demo embedded inside
a generic app page. It applies to every G1–G6 `GameScreen`, regardless of Design Signature or
layout recipe.

The product canvas is defined by `.claude/docs/mobile-first-contract.md`: a portrait phone is
the only design target. Larger hosts show the same phone screen in the phone column; the game
screen is never recomposed for them.

## Required composition

1. **The gameplay screen owns the phone screen.** Use an edge-to-edge game backdrop and compose
   the play field, HUD, and controls as one screen. Safe-area insets protect interactive chrome; they
   must not shrink the whole game into a second framed window.
2. **The mechanic is the dominant surface.** At the phone verification sizes, the visible
   play field should occupy at least 55% of the usable viewport and normally at least 88% of its
   width. A narrow-mechanic or portrait thumb-rail exception is allowed only when
   `design/art-direction.md` records why it improves play; the field must still be the first focal
   point and use all remaining space. There are no expanded sizes to grow into.
2b. **The field is centered by default.** Absent a documented reason, the play field's horizontal
   center coincides with the viewport's horizontal center — an unrecorded offset is treated as an
   accident. An off-center composition is fine when the recorded per-state recipe
   (`.claude/docs/layout-archetypes.md`) genuinely calls for it — an attached side control or an
   object-led composition can shift the field's midpoint — but that reason belongs in
   `design/art-direction.md`, not in an unexplained `Padding`/`Align`/`Positioned` offset that
   nobody chose on purpose. Checked as V20 by `/emulator-test` and `/autocreate-finalize`.
3. **No nested mini-game.** Do not place the live field inside a phone-like window, browser-like
   frame, isolated card, tall decorative bezel, or large padded container floating above an
   unrelated information card. A thematic rim, cabinet, table edge, or board boundary is fine
   when it belongs to the mechanic, hugs the field, and does not create large dead margins.
4. **Integrate HUD and controls.** Attach compact controls to the field as overlays, a slim edge
   cluster within thumb reach, or one deliberate command deck. Reuse the field's alignment grid, materials, shapes, and
   depth. A generic panel stacked below an unrelated game rectangle fails.
5. **The core loop never requires page scrolling.** The live field, primary action, score, the
   level goal and moves/time left, and result feedback must be visible together on the first
   viewport.
   Rules, history, explanations, and secondary configuration may open a sheet or separate screen.
6. **Controls are proportioned and usable.** Every tap target is at least 48×48 logical pixels;
   the primary action is at least 56 logical pixels high, within thumb reach, visually dominant,
   and has idle, pressed, active, and disabled states. Labels must fit at 1.0× and 1.3× text scale.
   Secondary buttons share height, baseline, spacing, and shape logic; disabled controls remain
   legible and clearly unavailable.
7. **Use constraints, not screenshot-specific pixels.** Prefer `Stack`, `Positioned`, `Align`,
   `Expanded`, `Flexible`, `AspectRatio`, and `LayoutBuilder` so the one portrait composition
   holds from 360×640 to 430×932. Use them for phone heights and safe areas, never for a width
   breakpoint that switches to another layout. Reserve fixed dimensions for icons, tap targets,
   borders, and spacing tokens.

## Required implementation hooks

Add stable keys so widget tests and runtime audits can measure the actual hierarchy:

- `Key('gameplaySurface')` on the live field/board/tray/physics surface.
- `Key('primaryAction')` on the main Play/Shoot/Drop/Start control — or, when the field itself is
  the input (swap, link, tap), on the field's interactive layer.
- `Key('controlDeck')` on the compact group of core controls, when one exists.

Do not put `gameplaySurface` or `primaryAction` under a vertical `Scrollable`. Do not solve a
small-screen overflow by making the entire game screen scroll; recompose or collapse secondary
content instead.

## Verification matrix

Check the four portrait phones:

| Viewport | Purpose |
|---|---|
| 360×640 | short compact Android phone |
| 360×800 | tall compact Android phone |
| 390×844 | canonical capture target |
| 430×932 | large phone |

For each size, verify:

- no overflow, clipping, accidental letterboxing, or large unexplained dead zone;
- the field is visually dominant and not a thumbnail or nested app window;
- the field's horizontal center sits inside the middle 60% of the viewport width, unless the
  recorded state recipe and a documented reason justify otherwise;
- the primary action and essential counters are visible without scrolling;
- controls do not overlap the field's critical interaction zone;
- control labels fit, tap targets meet the minimum, and enabled/disabled states are clear;
- the field, HUD, and controls read as one game-specific composition.

Capture the idle and active game states at 390×844 and 360×640. A visual audit is mandatory;
clean analyzer output and widget tests alone cannot approve composition.

Opening the Web build in a wide browser shows the same phone screen inside the phone column from
`mobile-first-contract.md` — one smoke capture proves it. It is not a layout to design or tune.

## Blocking failures

Treat any of these as a HIGH layout defect and a release blocker:

- the field resembles a small window inside the app screen;
- the field is below the size thresholds without a documented mechanic-driven exception;
- the field is shoved off-center (an unexplained `Padding`/`Align`/`Positioned` offset) without a
  recipe/mechanic reason recorded in `design/art-direction.md`;
- core gameplay requires vertical scrolling;
- a large instruction/progression card competes with or is larger than the field;
- core buttons are cramped, uneven, clipped, off-screen, or visually disconnected;
- the store showcase needs cropping or concept art to hide weak gameplay composition;
- the game screen has a desktop, tablet or landscape branch, or a wide host stretches it instead
  of showing the phone column.

Implementation must recompose the screen before handoff. Finalization must fail and route the
screen back through `/ui-audit --fix` or `/autocreate-implement --resume`; it must not downgrade
these failures to cosmetic concerns.
