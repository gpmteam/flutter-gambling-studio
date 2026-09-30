# Technical standards of the Casual Game Studio

## Product platform

- Design for a portrait phone and nothing else: Android and iOS phones, portrait-locked, touch
  only. There are no tablet, desktop or landscape layouts. Follow
  `.claude/docs/mobile-first-contract.md`.
- Web is the Chrome/CDP verification and preview host. It runs the same phone screens; a wide
  browser shows them in the phone column over the game's background.

### Web font and engine resource verification

Before claiming that a served Web game starts without external resources, use a fresh browser
profile with cache disabled and external HTTP(S) requests blocked before first navigation.
Verify successful startup and real gameplay, and inspect the request/error log. Bundled theme
fonts and `--no-web-resources-cdn` alone are not proof: inspect the installed engine and its
font manifest if a fallback request remains. For example, Flutter 3.44.5 CanvasKit loads remote
Roboto when the manifest lacks the `Roboto` family, even when the app uses bundled fonts.
When that behavior is confirmed, a compatible bundled font can be registered under the engine
fallback family while preserving the app's designed typography; test the generated manifest
and repeat the blocked-network run. Do not assume the same workaround is required by every
Flutter version or renderer. This verifies a locally served build, not serverless startup or
an installed offline PWA.

## Flutter + Flame 1.18.x

### Randomness and the rules engine

- **No gambling**: randomness sets up play (a board fill, a deal, a spawn order, the next piece,
  a generated level); it never decides whether a move "wins" and never grants a reward
  (`.claude/rules/no-gambling.md`).
- **One seeded `GameRng`**: all gameplay randomness goes through one injectable generator wrapping
  `Random(seed)`. A level has a fixed seed (or a recorded random one for endless runs; the date for
  the daily challenge), so it reproduces exactly in the game, the tests and the balance bot.
  `Random.secure()` is not needed — nothing is wagered, and reproducibility matters more.
- Cosmetic randomness (particle scatter, idle animation phases) uses a separate `VfxRng`, so
  effects never shift the gameplay sequence.
- **Logic before animation**: the pure rules engine resolves each move (matches, cascades,
  merges, the physics step, score) BEFORE the animation starts. The animation simply "plays back"
  the resolved steps. Without this neither the tests nor the balance bot can drive the game.
- **Balance tuning**: all game parameters live in `game_config.dart`; the balance model's numbers
  live in its JSON config (`design/balance/*.json`), which `tools/simulate_balance.py` reads. One
  source of truth, with no duplication between JSON and code.

### Flame API (1.18.x)

- Derive the main class from `FlameGame`.
- Always declare collisions on the `World`, not on the `FlameGame`:
  `class GameWorld extends World with HasCollisionDetection {}`
- Use the updated `CameraComponent`:
  `camera = CameraComponent(world: _world);`
- No `.isPaused = true`. Use `GameState` (a sealed class: Ready, Resolving, Paused, Cleared, Failed).

### Visualisers and particles

For the juiciness of a move we use *ParticleSystemComponent* effects.
- On key events (a match, a cascade, a special created, a big combo, a level cleared, a new best)
  spawn thematic particles:
  `ParticleSystemComponent(particle: Particle.generate(count: 50, generator: ...))`
- The strength of the effect scales with the significance of the event (see quality-bar.md §3):
  a small match gets a local flash, a three-star clear gets a fullscreen celebration.
  Identical feedback for everything kills the game's grammar.
- Effect settings (glow, drop shadow) are implemented through a Flutter Overlay on top of
  Flame, because complex filters inside Flame are expensive.

### Sound
- Use the `flame_audio` package, `^2.1.0`.
- Limit concurrent playback: at most 3 overlapping sounds (for example 1 BGM loop, 1 action
  sound loop, 1 effect overlay).
- For rising effects use pitch scaling: `playbackRate` 1.0 → 1.5.
- On Web, diagnose growing native audio nodes with forced-GC before/after heap snapshots
  and strong retaining paths; an active-voice cap alone does not bound retained sources.
  If the installed backend recreates media elements when a voice changes URLs and those
  sources remain rooted after release, reuse prepared sources from the finite SFX catalog
  (for example by channel and asset). Stop the previous source on a channel, preserve at
  most three concurrently playing voices, and dispose every prepared player. Verify the
  same alternating-event workload again, including source counts, errors and playback
  cancellation. This is a measured backend-specific remedy, not a universal pool mandate.

### Graphical assets
- For `/autocreate` under Codex the default graphics path is **PNG via GPT Images 2.0**, and
  if GPT Images 2.0 fails, a retry through **GPT Images / the default Codex image generation**,
  straight from the concept and Design DNA. Do not generate SVG first and convert it to PNG
  afterwards: that loses the material, the light, the style and the tie to the game's world.
- SVG remains the fallback mode for non-Codex environments or an explicit `--svg`.
- The chosen format is recorded in `design/asset-format.md`.
- Built-in image tools may return a base64 `image_url` alongside a saved-file hint.
  Present images through `generatedImage(result)` when the tool contract provides it;
  send only concise status and saved paths to `text`, `notify`, or other text logs.
  Never stringify the complete image-bearing result: its payload can overwhelm and truncate
  the tool transcript. Preserve the original PNGs and continue the normal asset review;
  truncated text output alone is not a reason to regenerate a valid image.
- If `format: png`, the UI uses `Image.asset(...)` and real `.png` paths.
- If `format: svg`, the UI uses `SvgPicture.asset(...)` / `flame_svg`.
- `/svg-to-png` exists only for legacy SVG or an explicit user request — it is not the normal
  `/autocreate` path.
- For simple PNG assets the prompt must ask for a flat key background (chroma key: by default
  `pure magenta #FF00FF`, or `pure green #00FF00` if the palette contains magenta/pink) with no
  shadows, gradients or scene, and the background is then cut out with
  `python3 tools/cutout.py <file> --type sprite`.
  A white background is forbidden for objects with light or white areas — they merge into it.
  A manual `magick -fuzz -transparent white` is forbidden: it tears the alpha and leaves a halo.
  For background images the background is not removed.
- Naming pattern:
  `background_X` (backgrounds)
  `sprite_X` (game elements: tiles, symbols, pieces, balls, pegs, targets, blockers)
  `ui_X` (buttons, panels, board frames, trays)
  `icon_X` (badges, interface icons)
