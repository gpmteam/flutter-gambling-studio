# Mobile-Only Phone Contract

Every game this studio produces is a **portrait phone game**. A phone held upright and played with
a thumb is the only design target. There is no desktop design, no desktop or tablet layout, no
landscape composition and no hover, mouse or keyboard interaction — not as the main target and not
as a secondary one. "Mobile-first" in this studio means *mobile only*.

(The file keeps its old name because the whole studio links to it.)

## Product principle

- Design every screen for a portrait phone and nothing else. 390×844 is the canonical
  composition; the rest of the phone matrix proves it holds from a short Android phone to a large
  iPhone.
- Touch only. Every action is a tap, drag, swipe or hold within thumb reach. Hover states,
  tooltips, right-click, keyboard shortcuts and scroll-wheel input are never needed to play or to
  find anything. Touch targets are at least 48×48 logical pixels; the primary action is at least
  56 high and sits in the lower thumb zone.
- Phone density. One column. Body text at least 14 sp. No data tables, multi-column dashboards,
  menu bars, sidebars, navigation rails, split panes or top bars with rows of links.
- Full-bleed phone screen. Backgrounds run edge to edge under the status bar and home indicator;
  `SafeArea` protects text and controls, not the art.
- Web is only the host the studio uses to verify and preview the phone game (Chrome/CDP at phone
  sizes). It is not a desktop product and never gets a desktop layout.

## Required viewport matrix

| Viewport | Purpose |
|---|---|
| 360×640 | short compact Android phone |
| 360×800 | tall compact Android phone |
| 390×844 | canonical phone composition and capture target |
| 430×932 | large phone |

All four are layout gates, in portrait. There is no landscape, tablet or desktop gate — a layout
built for one is a defect, not extra credit.

## Hosts larger than a phone

A tablet, a desktop browser opening the Web preview, or any window wider than a phone is not a
design target. It shows the same portrait phone game, unchanged, in a **phone column**:

- Column width = `min(available width, available height × 9/16, 480)` logical pixels, at full
  available height, centered. At every size in the phone matrix the column is the whole screen,
  so phones never see it.
- Outside the column, the game's own background art — the campaign background once finalization
  has made it — fills the host at `BoxFit.cover` under a dark veil. No device bezel, notch or
  mockup, and no controls, copy, HUD or second layout outside the column.
- Every route, dialog, sheet and overlay renders inside the column: wrap it once in
  `MaterialApp.builder`, and override the `MediaQuery` size so screens measure the column.
- Never recompose for the extra room: no breakpoints, side rails, second panels, larger type or
  scaled-up controls.

```dart
/// Presents the portrait phone game on any host. On phones the column is the whole screen; on a
/// tablet or desktop browser it is a centered phone-shaped column over the game's own background.
/// See .claude/docs/mobile-first-contract.md.
class PhoneColumn extends StatelessWidget {
  const PhoneColumn({required this.surround, required this.child, super.key});

  final ImageProvider surround;
  final Widget child;

  static const double _maxWidth = 480;
  static const double _maxAspect = 9 / 16;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = math.min(
          constraints.maxWidth,
          math.min(constraints.maxHeight * _maxAspect, _maxWidth),
        );
        if (width >= constraints.maxWidth) return child;
        return Stack(
          fit: StackFit.expand,
          children: [
            Image(image: surround, fit: BoxFit.cover, alignment: Alignment.topCenter),
            const ColoredBox(color: Color(0xA6000000)),
            Center(
              child: SizedBox(
                width: width,
                height: constraints.maxHeight,
                child: MediaQuery(
                  data: media.copyWith(size: Size(width, constraints.maxHeight)),
                  child: ClipRect(child: child),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

// MaterialApp(
//   builder: (context, child) => PhoneColumn(
//     surround: const AssetImage(GameAssets.bgCampaignMenu),
//     child: child ?? const SizedBox.shrink(),
//   ),
//   ...
// )
```

## Orientation and native targets

- Portrait only. `main()` calls
  `SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp])` before `runApp`; the
  Android main activity declares `android:screenOrientation="portrait"`; iOS lists only portrait in
  `UISupportedInterfaceOrientations` (and `~ipad`) and sets `UIRequiresFullScreen` to true.
- Create projects with `flutter create --platforms web,android,ios`. Never add Windows, macOS or
  Linux scaffolds.

Secondary informational screens (rules, odds, history, settings) may scroll. The gameplay core
may not; follow `gameplay-screen-contract.md`.

## Blocking failures

Treat these as HIGH defects and release blockers:

- a desktop, tablet or landscape layout: a width breakpoint that changes the composition, a side
  rail, `NavigationRail`, split pane, second panel or "expanded" branch;
- a wide host that stretches the phone composition across the window, shows a device bezel or
  mockup, or puts anything but the background surround outside the phone column;
- hover-only, pointer-only or keyboard-only interaction, tooltips as the only source of
  information, or a touch target below 48×48;
- overflow, clipping, unreachable actions or distorted art at any phone size;
- a missing portrait lock on a native target, or a desktop platform scaffold.
