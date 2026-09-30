#!/usr/bin/env bash
# Validate Commit Hook — Flutter Casual Game Studio
# Advisory pre-commit checks for points-only gameplay and deterministic rules.

# Only run on git commit commands
INPUT_JSON="${CLAUDE_TOOL_INPUT:-}"
if echo "$INPUT_JSON" | grep -q '"git commit"' 2>/dev/null || echo "$INPUT_JSON" | grep -q 'git commit' 2>/dev/null; then
  :
else
  exit 0
fi

ERRORS=()
WARNINGS=()

echo "🔍 Checking the game requirements before committing..."

# 1–3. Casual mechanics, config keys and the single seeded gameplay RNG.
if [ -f tools/check_no_gambling.py ]; then
  if ! python3 -B tools/check_no_gambling.py; then
    ERRORS+=("🚨 No-gambling/seeded-RNG gate failed — see findings above")
  fi
fi

# 4. Check for valid JSON configs
for json_file in design/balance/*.json assets/data/*.json; do
  if [ -f "$json_file" ]; then
    if ! python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$json_file" 2>/dev/null; then
      ERRORS+=("❌ Invalid JSON: $json_file")
    fi
  fi
done

# 5. Check for print() statements in lib (not test)
if find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "^\s*print\(" 2>/dev/null | grep -v "_test\.dart" | grep -q .; then
  WARNINGS+=("⚠️  print() found in lib/ — use Logger from the logging package")
  find lib -name "*.dart" 2>/dev/null | xargs grep -lnE "^\s*print\(" 2>/dev/null | grep -v "_test\.dart" | while read f; do
    WARNINGS+=("   → $f")
  done
fi

# 6. Check that game_config.dart exists if there are game files
if [ -d "lib/game" ] && [ ! -f "lib/game/game_config.dart" ]; then
  WARNINGS+=("⚠️  game_config.dart is missing — every game value belongs in the config")
fi

# Report results
if [ ${#ERRORS[@]} -gt 0 ]; then
  echo ""
  echo "╔══════════════════════════════════════════╗"
  echo "║  ❌ COMMIT BLOCKED — game rules           ║"
  echo "╚══════════════════════════════════════════╝"
  for err in "${ERRORS[@]}"; do
    echo "  $err"
  done
  echo ""
  echo "Fix the errors and commit again."
  echo ""
  # Don't actually block (hooks are advisory) — just warn loudly
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  Warnings (they do not block the commit):"
  for warn in "${WARNINGS[@]}"; do
    echo "  $warn"
  done
fi

if [ ${#ERRORS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ]; then
  echo "✅ Game rules satisfied"
fi
