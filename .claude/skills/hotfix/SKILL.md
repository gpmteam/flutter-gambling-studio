---
name: hotfix
description: "An emergency fix for a critical problem, with a minimal diff and mandatory verification."
argument-hint: "[a short description of the critical problem]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# /hotfix [problem description]

Invocation: the user runs `/hotfix [a short description of the critical problem]`

## Goal

An emergency fix for a critical problem in the mini-game. It bypasses the normal development
process while keeping a full audit trail. Use it for:
- Critical RNG bugs (an incorrect distribution)
- An impossible level or broken difficulty curve
- State leakage (incorrect score, moves or saved progress)
- A crash during move resolution
- A critical UI bug (input cannot make a move)

## When NOT to use it

- Ordinary bugs → use the standard process
- New features → `/add-feature`
- Refactoring → a normal PR

## Order of work

### Step 1: assessing severity

The `lead-programmer` agent assesses:
- Does it corrupt the rules, RNG replay or progression? → CRITICAL
- Can the player lose saved progress? → CRITICAL
- Purely a visual bug? → NOT A HOTFIX

### Step 2: diagnosis

```bash
# Check dart analyze
dart analyze lib/

# Look for the obvious cause
grep -rn "TODO\|FIXME\|HACK" lib/ --include="*.dart"

# Check the tests
flutter test --name "broken_mechanic"
```

The `mechanics-programmer` agent analyses the casual rules and state files:
- `lib/systems/game_rng.dart` — checking the RNG
- `lib/systems/board_engine.dart (or the category's rules engine)` — checking the logic
- `lib/game/game_config.dart` — checking the config
- `lib/models/game_state.dart` — checking the state machine

### Step 3: creating the hotfix branch

```bash
DATE=$(date '+%Y%m%d')
git checkout -b hotfix/$DATE-short-description
```

### Step 4: the fix

- Fix ONLY the identified problem
- No opportunistic improvements
- The smallest possible diff

### Step 5: verification

```bash
# Mandatory after the fix
flutter test
dart analyze lib/
python3 tools/simulate_balance.py --model [b1-b6|report] --config design/balance/[file].json
```

The verification checklist:
- [ ] The fix does not break existing tests
- [ ] The category's balance curve is inside its B1–B6 windows (rerun if affected)
- [ ] Gameplay still uses one seeded GameRng; no wager, currency or random reward was introduced
- [ ] No state leakage appeared

### Step 6: the audit trail

Create `production/session-logs/hotfix-YYYY-MM-DD.md`:
```markdown
# Hotfix — [date and time]

## Problem
[A description of the critical problem]

## Diagnosis
[The root cause]

## The fix
[What was changed and why]

## Files changed
- path/to/file.dart — [what changed]

## Verification
- flutter test: [PASS/FAIL]
- dart analyze: [0 issues / N issues]
- Balance simulation: [PASS/CONCERNS/FAIL, report path]

## Approved
- Technically: [lead-programmer / technical-director]
- Balance: [balance-designer — if difficulty or scoring changed]
```

### Step 7: recording the fix

```bash
git add [only the changed files]
git commit -m "hotfix: [a short description of the problem]

Problem: [what was wrong]
Fix: [what changed]
Verification: tests GREEN, balance verified, no-gambling gate clean"
```

## Arguments

- `[description]` — a short description of the problem (required)
- `--rng` — focus on the RNG/probabilities
- `--balance` — focus on scoring and the difficulty curve
- `--crash` — focus on the crash/error
