---
description: Flutter UI rules — crash prevention, layout safety, state management, navigation, interaction patterns
globs: ["lib/screens/**/*.dart", "lib/widgets/**/*.dart", "lib/ui/**/*.dart", "lib/theme/**/*.dart", "lib/app.dart"]
---

# UI Code Rules — Flutter Screens, Widgets & HUD

## 1. Separating UI state from game state

- **NEVER** store game state (score, moves left, the move being resolved) in Flutter widgets
- The Flutter UI only **reads** state, through a `ValueNotifier` or a `Stream`
- Game logic lives in Flame components; the UI only displays it

```dart
// ✅ CORRECT — the HUD reads through a ValueNotifier
class HudWidget extends StatelessWidget {
  final ValueNotifier<int> score;
  final ValueNotifier<int> movesLeft;
  final ValueNotifier<bool> isResolving;

  const HudWidget({
    required this.score,
    required this.movesLeft,
    required this.isResolving,
    super.key,
  });
}

// ❌ FORBIDDEN — the HUD manages the score itself
class HudWidget extends StatefulWidget {
  int _score = 0; // Not allowed!
  void _onClear(int points) => setState(() => _score += points); // Not allowed!
}
```

---

## 2. CRASH SAFETY (critical — a violation means a guaranteed crash)

### 2.1 RenderFlex overflow — THE MOST COMMON ERROR

```dart
// ❌ CRASH: "A RenderFlex overflowed by 42 pixels on the bottom"
Column(
  children: [
    Text('Header'),
    ListView.builder(itemCount: 100, itemBuilder: ...), // Unbounded height!
  ],
)

// ✅ SAFE: the ListView is bounded by Expanded
Column(
  children: [
    Text('Header'),
    Expanded(
      child: ListView.builder(itemCount: 100, itemBuilder: ...),
    ),
  ],
)
```

**Rule**: every scrolling widget (`ListView`, `GridView`, `SingleChildScrollView`) inside a
`Column` or `Row` MUST be wrapped in `Expanded` or `Flexible`.

### 2.2 setState after dispose

```dart
// ❌ CRASH: "setState() called after dispose()"
class _MyState extends State<MyWidget> {
  void _onDataLoaded(data) {
    setState(() { _data = data; }); // The widget may already be disposed!
  }
}

// ✅ SAFE: check mounted
class _MyState extends State<MyWidget> {
  void _onDataLoaded(data) {
    if (!mounted) return; // MANDATORY before every setState in a callback/Future/Timer
    setState(() { _data = data; });
  }
}
```

**Rule**: EVERY `setState` inside `Future.then()`, `Timer`, `StreamSubscription.listen()`,
`.whenComplete()` or any async callback MUST be preceded by `if (!mounted) return;`.

### 2.3 Dispose every resource

```dart
// ❌ MEMORY LEAK + CRASH:
class _MyState extends State<MyWidget> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl = AnimationController(vsync: this, duration: Duration(seconds: 1));
  late final Timer _timer = Timer.periodic(Duration(seconds: 1), (_) { ... });
  late final StreamSubscription _sub = someStream.listen((_) { ... });
  final _scrollCtrl = ScrollController();
  final _textCtrl = TextEditingController();
  // No dispose()! → memory leak → crash when touching a disposed controller
}

// ✅ SAFE: everything is released
class _MyState extends State<MyWidget> with SingleTickerProviderStateMixin {
  late final AnimationController _animCtrl;
  Timer? _timer;
  StreamSubscription? _sub;
  final _scrollCtrl = ScrollController();
  final _textCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(vsync: this, duration: Duration(seconds: 1));
    _timer = Timer.periodic(Duration(seconds: 1), (_) { ... });
    _sub = someStream.listen((_) { ... });
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    _timer?.cancel();
    _sub?.cancel();
    _scrollCtrl.dispose();
    _textCtrl.dispose();
    super.dispose();
  }
}
```

**Rule**: every `AnimationController`, `Timer`, `StreamSubscription`, `ScrollController`,
`TextEditingController` and `FocusNode` MUST be disposed or cancelled in `dispose()`.
Use nullable types (`Timer?`) for safety.

For image-loading or animation handoffs that intentionally keep a fallback visible for a
short delay, store that delay as a nullable `Timer` and cancel it in `dispose()`. Do not use
an uncancellable `Future.delayed` for a callback that can call `setState`; widget layout
tests dispose routes between viewport passes and will correctly report the pending timer.

A listener can synchronously release its owner during `notifyListeners()`. Mark the
owner inactive and cancel timers immediately, but defer disposal of its active
`ChangeNotifier`/`ValueNotifier` until the notification stack unwinds (for example, a
queued microtask). Guard subsequent notifications against the inactive owner. If a
callback can add or remove controllers/subscribers, iterate a stable snapshot and skip
released entries. Snapshot iteration alone does not make notifier disposal reentrant.
Verify this with two subscribers: the first releases itself on a score update, while
the second still receives the committed score with no Flutter errors.

### 2.4 Missing assets

```dart
// ❌ CRASH: "Unable to load asset: assets/images/sprites/missing.svg"
SvgPicture.asset('assets/images/sprites/missing.svg')

// ✅ SAFE: the path comes from constants and the file is guaranteed to exist
SvgPicture.asset(
  GameAssets.spriteCherry, // From lib/assets.dart — verified at build time
  width: 64,
  height: 64,
  placeholderBuilder: (_) => SizedBox(width: 64, height: 64), // fallback
)
```

**Rule**: all asset paths go through constants in `lib/assets.dart`.
For SVG/Image: always specify `width` and `height`.
For optional assets: use `placeholderBuilder` or `errorBuilder`.

### 2.5 Navigator safety

```dart
// ❌ CRASH: "Navigator.pop called on empty stack"
Navigator.pop(context);

// ✅ SAFE
if (Navigator.canPop(context)) {
  Navigator.pop(context);
} else {
  Navigator.pushReplacementNamed(context, '/menu');
}

// ❌ CRASH: "Could not find a generator for route /unknown"
Navigator.pushNamed(context, '/unknown');

// ✅ SAFE: every route is declared in app.dart
// And, for safety, add onUnknownRoute:
MaterialApp(
  routes: { '/menu': (_) => MainMenu(), '/game': (_) => GameScreen(), ... },
  onUnknownRoute: (settings) => MaterialPageRoute(builder: (_) => MainMenu()),
)
```

---

## 3. LAYOUT SAFETY (high — a violation means a visual bug)

All layout work follows `.claude/docs/mobile-first-contract.md`: the game is a portrait phone
game, played by touch. Every screen is written for the four portrait phones (360×640 to 430×932)
and nothing else; tablets and desktop browsers show the same screens inside the phone column.

### 3.1 SafeArea on EVERY root screen

```dart
// ❌ Content slides under the notch / status bar
@override
Widget build(BuildContext context) {
  return Scaffold(
    body: Column(children: [...]),
  );
}

// ✅ SafeArea protects against the notch / status bar / navigation bar
@override
Widget build(BuildContext context) {
  return Scaffold(
    body: SafeArea(
      child: Column(children: [...]),
    ),
  );
}
```

**Exception**: the game screen with the Flame GameWidget — SafeArea is NOT needed there
(the game is fullscreen).

### 3.2 Text ALWAYS handles overflow

```dart
// ❌ The text runs off the screen — yellow overflow stripes
Text(longPlayerName)

// ✅ The text is clipped or scaled
Text(longPlayerName, overflow: TextOverflow.ellipsis, maxLines: 1)
// or
FittedBox(fit: BoxFit.scaleDown, child: Text(longPlayerName))
// or
Flexible(child: Text(longPlayerName, overflow: TextOverflow.ellipsis))
```

**Rule**: every `Text` with dynamic content (not a hardcoded string) MUST have `overflow:`
plus `maxLines:`, or sit inside a `FittedBox`, or inside a `Flexible`/`Expanded`.

### 3.3 One portrait layout — no fixed pixels, no breakpoints

```dart
// ❌ Overflow on a 360×640 phone
Container(width: 400, height: 600, child: ...)

// ❌ A second layout for wide screens — the studio ships phone games only
LayoutBuilder(builder: (context, c) =>
    c.maxWidth > 600 ? const DesktopGameLayout() : const PhoneGameLayout())

// ✅ One portrait composition that scales with the phone
LayoutBuilder(
  builder: (context, constraints) {
    final width = constraints.maxWidth;
    return Container(
      width: width * 0.9,
      height: constraints.maxHeight * 0.7,
      child: ...
    );
  },
)

// ✅ Or MediaQuery for percentage sizes
final size = MediaQuery.of(context).size;
Container(width: size.width * 0.9, height: size.height * 0.7)
```

**Rule**: fixed pixels are acceptable ONLY for:
- Icons and buttons (32–64px)
- Padding (8–24px)
- Border/shadow (1–4px)
- Font size (12–48sp)

Everything else goes through `MediaQuery`, `LayoutBuilder`, `Expanded`, `Flexible` or
`FractionallySizedBox`.

Use `LayoutBuilder`/`MediaQuery` to fit the one portrait composition to the phone's height and
safe areas (the P axis in `layout-archetypes.md`: what grows on a tall phone, what compresses on a
short one). Never branch on width to produce another composition — no tablet, desktop or landscape
layout, no side rail or second pane for extra width. The only wide-host behaviour is the phone
column in `MaterialApp.builder` (`mobile-first-contract.md`).

### 3.4 SingleChildScrollView + Column (the correct pattern)

```dart
// ❌ CRASH: Expanded inside an unbounded scroll view
SingleChildScrollView(
  child: Column(
    children: [
      Expanded(child: Widget()), // Expanded does not work inside a scroll!
    ],
  ),
)

// ✅ SAFE: no Expanded inside the scroll
SingleChildScrollView(
  child: Column(
    children: [
      SizedBox(height: 200, child: Widget()), // Fixed or intrinsic size
      Widget(), // Intrinsic size
    ],
  ),
)
```

### 3.5 Image / SVG with dimensions

```dart
// ❌ The image stretches across the whole screen
Image.asset('assets/images/ui/button.png')
SvgPicture.asset('assets/images/sprites/cherry.svg')

// ✅ Dimensions are given
Image.asset('assets/images/ui/button.png', width: 120, height: 48, fit: BoxFit.contain)
SvgPicture.asset('assets/images/sprites/cherry.svg', width: 64, height: 64)
```

### 3.6 Full-screen gameplay composition

Read and implement `.claude/docs/gameplay-screen-contract.md` for every `GameScreen`.

- Put the live field under `Key('gameplaySurface')`, the primary action under
  `Key('primaryAction')`, and the core control group under `Key('controlDeck')` when present.
- Compose the field, HUD, and controls as one full-screen phone composition. Do not embed the
  field in a small decorative window above a separate generic information card.
- Keep the field, essential counters (score, moves/time, goal), and primary action visible without
  vertical page scrolling.
- Verify it at 360×640, 360×800, 390×844, and 430×932 in portrait — the only layout targets.

**Rule**: shrinking the field, adding a `SingleChildScrollView` around the whole game screen, or
moving core controls below the fold is not an acceptable overflow fix. Recompose the layout.

---

## 4. NAVIGATION

### 4.1 Splash → Menu: pushReplacement, not push

```dart
// ❌ The splash stays on the stack — "back" returns to the splash
Navigator.pushNamed(context, '/menu');

// ✅ The splash is replaced
Navigator.pushReplacementNamed(context, '/menu');
```

### 4.2 A back action on every screen

```dart
// ❌ "Back" closes the app
@override
Widget build(BuildContext context) {
  return Scaffold(body: ...);
}

// ✅ "Back" returns to the previous screen (or asks for confirmation)
@override
Widget build(BuildContext context) {
  return PopScope(
    canPop: false,
    onPopInvokedWithResult: (didPop, _) {
      if (didPop) return;
      // For the game screen: show "Quit the game?"
      // For the others: Navigator.pop(context)
      if (Navigator.canPop(context)) {
        Navigator.pop(context);
      }
    },
    child: Scaffold(body: ...),
  );
}
```

### 4.3 Every route is declared

In `app.dart`, EVERY route used MUST be in the `routes:` map.
Add `onUnknownRoute:` as a fallback.

### 4.4 Flame overlay lifecycle

```dart
// ❌ The overlay hangs around forever
game.overlays.add('combo');

// ✅ The overlay closes itself
game.overlays.add('combo');
Future.delayed(Duration(seconds: 3), () {
  if (game.overlays.isActive('combo')) {
    game.overlays.remove('combo');
  }
});
```

---

## 5. BUTTONS AND INTERACTION

### 5.1 The action button (Play / Shoot / Drop) — THE COMPLETE PATTERN

```dart
class ActionButton extends StatefulWidget {
  final VoidCallback onAction;
  final ValueNotifier<bool> isPlaying;

  const ActionButton({required this.onAction, required this.isPlaying, super.key});

  @override
  State<ActionButton> createState() => _ActionButtonState();
}

class _ActionButtonState extends State<ActionButton> with SingleTickerProviderStateMixin {
  DateTime? _lastTap;
  late final AnimationController _scaleCtrl;
  late final Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    _scaleCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 100));
    _scaleAnim = Tween<double>(begin: 1.0, end: 0.92).animate(
      CurvedAnimation(parent: _scaleCtrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _scaleCtrl.dispose();
    super.dispose();
  }

  void _handleTap() {
    // 1. Debounce 300ms
    final now = DateTime.now();
    if (_lastTap != null && now.difference(_lastTap!) < const Duration(milliseconds: 300)) return;
    _lastTap = now;

    // 2. Check game state
    if (widget.isPlaying.value) return;

    // 3. Animate press
    _scaleCtrl.forward().then((_) => _scaleCtrl.reverse());

    // 4. Execute action
    widget.onAction();
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: widget.isPlaying,
      builder: (_, isPlaying, child) {
        return AnimatedOpacity(
          opacity: isPlaying ? 0.5 : 1.0, // Visual disabled state
          duration: const Duration(milliseconds: 200),
          child: ScaleTransition(
            scale: _scaleAnim,
            child: GestureDetector(
              onTap: isPlaying ? null : _handleTap,
              child: child,
            ),
          ),
        );
      },
      child: /* button visual */,
    );
  }
}
```

**Rule**: the action button MUST have:
1. A 300 ms debounce
2. An isPlaying check
3. A visual disabled state (opacity / colour change)
4. A press animation (scale / glow)
5. A ValueListenableBuilder for reactivity

Use monotonic elapsed time (for example `Stopwatch`) for the debounce interval,
with an injectable elapsed-time source for tests. Device wall-clock corrections must
not disable the action until a previous timestamp catches up. Keep UTC/calendar clocks for
persisted daily eligibility and event dates. When a configured cooldown is zero, bypass
the interval gate explicitly; a negative wall-clock delta must not enable a disabled
cooldown. Test a completed action after the debounce has elapsed while the device clock
moves backward, and test zero-cooldown recovery separately from once-per-date daily challenges.

### 5.2 Secondary controls — locked while a move resolves

```dart
// ❌ A booster can be fired mid-cascade
ElevatedButton(onPressed: () => useHammer(), child: Text('Hammer'))

// ✅ Boosters, shuffle and pause are locked while the move resolves
ValueListenableBuilder<bool>(
  valueListenable: isResolving,
  builder: (_, resolving, __) {
    return IgnorePointer(
      ignoring: resolving,
      child: AnimatedOpacity(
        opacity: resolving ? 0.4 : 1.0,
        duration: const Duration(milliseconds: 200),
        child: Row(children: [
          BoosterButton(kind: BoosterKind.hammer, onTap: useHammer),
          BoosterButton(kind: BoosterKind.shuffle, onTap: shuffle),
        ]),
      ),
    );
  },
)
```

### 5.3 Tap targets at least 48x48

```dart
// ❌ Too small a button — 24x24
Icon(Icons.settings, size: 24)

// ✅ A 48x48 tap target with a 24x24 icon
SizedBox(
  width: 48, height: 48,
  child: IconButton(
    icon: Icon(Icons.settings, size: 24),
    onPressed: () => Navigator.pushNamed(context, '/settings'),
  ),
)
```

### 5.4 Every button gives feedback

```dart
// ❌ A "dead" button — no visual reaction
GestureDetector(
  onTap: doSomething,
  child: Container(child: Text('TAP')),
)

// ✅ A button with press feedback
GestureDetector(
  onTapDown: (_) => setState(() => _pressed = true),
  onTapUp: (_) => setState(() => _pressed = false),
  onTapCancel: () => setState(() => _pressed = false),
  onTap: doSomething,
  child: AnimatedScale(
    scale: _pressed ? 0.95 : 1.0,
    duration: const Duration(milliseconds: 100),
    child: Container(child: Text('TAP')),
  ),
)
```

---

## 6. RESULT AND CELEBRATION OVERLAYS

- The celebration appears AFTER the resolving animation finishes
- Scaled to significance, from the points/combos the player earned — never money:
  - Routine: a local pop and a score tick near the cleared pieces
  - Notable (a big combo, a special created): a contextual callout, burst particles, `sfx_win_big`
  - Major (level cleared with 3 stars, a new best): a result takeover with stars filling, `sfx_win_mega`
- Auto-dismiss on a timer, plus tap-to-dismiss; the level-complete screen always offers Next and Retry
- The score updates with a short count-up only when the gain matters; stable values update directly
- The overlay does NOT block the back action
- No "WIN", "BIG WIN", "JACKPOT" or "PAYOUT" banners — celebrate in the game's own words
  (CLEARED!, CHAIN x6!, NEW BEST!), see `.claude/rules/no-gambling.md` §5

## 7. PERSISTENCE (SharedPreferences)

Must be saved:
- Settings: sound on/off, sfx on/off, vibration on/off
- Profile: nickname, avatar index
- Leaderboard: top 10 scores
- Daily challenge: the date it was last cleared and the streak
- High score: the best result

**Pattern**: a try-catch around EVERY SharedPreferences call:
```dart
Future<int> getHighScore() async {
  try {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('high_score') ?? 0;
  } catch (_) {
    return 0; // Safe fallback
  }
}
```

---

## 8. ACCESSIBILITY

- The action button: `Semantics(label: 'Start the game')`
- Score: `Semantics(value: '$score points')`
- Text at least 14sp on mobile
- Text contrast against the background at least 4.5:1
- Every interactive element at least 48x48

---

## 9. PORTRAIT PHONE TARGETING

- Follow `.claude/docs/mobile-first-contract.md`: a portrait phone is the only design target.
- Lock portrait: `SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp])` in
  `main()`, `android:screenOrientation="portrait"`, portrait-only iOS orientations with
  `UIRequiresFullScreen`.
- Wrap `MaterialApp.builder` in the phone column so a tablet or desktop browser shows the same
  phone screens over the game's background; no screen checks the width to change its layout.
- Touch is the only input: no hover states, tooltips or keyboard shortcuts carry anything the
  player needs.

---

## 10. FORBIDDEN PATTERNS

1. **`setState()`** for updating game state — use `ValueNotifier` only
2. **`setState` without a `mounted` check** in an async context — a guaranteed crash
3. **`BuildContext` in Flame components** — pass a callback at initialisation
4. **UI animations longer than 500 ms** — they slow down the perception of the result
5. **Fixed sizes without `MediaQuery`** for layout — use `LayoutBuilder`
6. **`ListView` inside `Column` without `Expanded`** — an "unbounded height" crash
7. **`Expanded` inside `SingleChildScrollView`** — Expanded does not work in a scroll
8. **`Navigator.pop` without a `canPop` check** — a crash on an empty stack
9. **An AnimationController without `dispose()`** — a memory leak
10. **A Timer without `cancel()` in `dispose()`** — a callback on a disposed widget
11. **Image/SVG without width/height** — unpredictable sizing
12. **Text without overflow handling** on dynamic content
13. **A GestureDetector without visual feedback** — a "dead" button
14. **`print()` in production** — use `debugPrint` or `Logger`
15. **Player-facing strings in a language other than English**, unless the user explicitly
    asked for a different language — see CLAUDE.md → Language
16. **A desktop, tablet or landscape layout** — width breakpoints, side rails, split panes,
    `NavigationRail`, or any composition other than the portrait phone one
17. **A fake device frame, or a stretched game on a wide host** — wide hosts get the phone column
    over the game's background, never a bezel and never the phone layout stretched across the window
18. **Hover-, mouse- or keyboard-only interaction** — touch is the only input
