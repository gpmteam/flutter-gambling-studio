#!/usr/bin/env bash
# Detect Gaps Hook — Flutter Game Studio
# Warns when critical game files are missing

GAPS=()
WARNINGS=()

# Check if any game has been started
if [ ! -f "pubspec.yaml" ]; then
  GAPS+=("❌ pubspec.yaml is missing — the project is not initialised")
fi

# Check for critical game files
if [ -f "pubspec.yaml" ]; then
  if [ ! -f "lib/main.dart" ]; then
    GAPS+=("❌ lib/main.dart is missing")
  fi

  if [ ! -d "lib/game" ]; then
    WARNINGS+=("⚠️  lib/game/ has not been created — run /autocreate or /brainstorm")
  fi

  # Gameplay-screen contract — deterministic hooks for geometry tests and runtime measurement.
  GAME_SCREEN_FILES=$(find lib/screens -type f -name "*game*screen*.dart" 2>/dev/null)
  if [ -n "$GAME_SCREEN_FILES" ]; then
    if ! grep -q "gameplaySurface" $GAME_SCREEN_FILES 2>/dev/null; then
      GAPS+=("❌ GameScreen is missing Key('gameplaySurface') — portrait phone geometry cannot be verified")
    fi
    if ! grep -q "primaryAction" $GAME_SCREEN_FILES 2>/dev/null; then
      GAPS+=("❌ GameScreen is missing Key('primaryAction') — action visibility/size cannot be verified")
    fi
    if [ ! -f "test/screens/game_screen_layout_test.dart" ]; then
      GAPS+=("❌ test/screens/game_screen_layout_test.dart is missing — run the four-phone portrait layout gate")
    fi
  fi

  # No gambling and reproducible gameplay; cosmetic RNG is separate.
  if [ -f tools/check_no_gambling.py ]; then
    if ! python3 -B tools/check_no_gambling.py; then
      GAPS+=("🚨 No-gambling/seeded-RNG gate failed — see findings above")
    fi
  fi
  if [ ! -f lib/systems/game_rng.dart ]; then
    WARNINGS+=("⚠️  GameRng missing — random gameplay must use one seeded stream")
  fi

  # Check for GDD
  if [ ! -d "design/gdd" ] || [ -z "$(ls design/gdd/*.md 2>/dev/null)" ]; then
    WARNINGS+=("⚠️  No GDD documents — run /brainstorm or /design-system")
  fi

  # Check for balance config
  if [ ! -d "design/balance" ] || [ -z "$(ls design/balance/*.json 2>/dev/null)" ]; then
    WARNINGS+=("⚠️  design/balance/ is empty — /balance-check will not work")
  fi
fi

# Print gaps
if [ ${#GAPS[@]} -gt 0 ]; then
  echo ""
  echo "🚨 CRITICAL PROBLEMS FOUND:"
  for gap in "${GAPS[@]}"; do
    echo "   $gap"
  done
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  WARNINGS:"
  for warn in "${WARNINGS[@]}"; do
    echo "   $warn"
  done
fi

if [ ${#GAPS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ] && [ -f "pubspec.yaml" ]; then
  echo "✅ Project structure looks fine"
fi
