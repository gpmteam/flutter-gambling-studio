---
name: design-review
description: "Checks a GDD for completeness, quality, balance correctness and the no-gambling gate against the studio's standards."
argument-hint: "[file or system]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent
---

# /design-review [file or system]

Invocation: the user runs `/design-review [path to the GDD or the system's name]`

## Goal

Checks the completeness and quality of a mini-game's Game Design Document.
Confirms that the GDD contains all 8 required sections, that the scoring and balance are correct, that
edge cases are described and that the acceptance criteria are testable.

## Agents

- `game-designer` — design completeness and correctness
- `balance-designer` — verification of the scoring formulas and the difficulty curve

## Order of work

### Step 1: find the GDD documents

If a path was given, check that specific file.
If not, check every file in `design/gdd/`.

### Step 2: game-designer — GDD completeness check

The `game-designer` agent checks each GDD:

**The 8 required sections:**
- [ ] Overview — there is an introductory paragraph
- [ ] Player fantasy — the feeling is described
- [ ] Detailed rules — stated unambiguously
- [ ] Formulas — every calculation, with variables
- [ ] Edge cases — at least 5 situations
- [ ] Dependencies — the systems are listed
- [ ] Tuning knobs — a table with ranges
- [ ] Acceptance criteria — at least 5 testable criteria

**Casual-game checks (where applicable):**
- [ ] The target curve is stated and sits inside the model's windows
- [ ] Goals, budgets and star thresholds are in the balance config
- [ ] Specials/blockers: how each is created or cleared, and what combinations do
- [ ] No dead ends: reshuffle, solvable generation, retry
- [ ] Scoring is a pure function of play; combo multipliers are earned, never random
- [ ] **No gambling** (`.claude/rules/no-gambling.md`): no wager, currency, shop, chance-based
      reward, casino game, gambling copy or age gate

**Document status:**
- [ ] There is a `Status:` line (Draft / Review / Approved / Implemented)
- [ ] Approved documents carry a date

**Language:**
- [ ] The document is written in English, like everything else the studio produces

**Portrait phone product target:**
- [ ] The concept/design follows `.claude/docs/mobile-first-contract.md`: a portrait phone game,
      touch only, with no tablet, desktop or landscape layout planned
- [ ] The layout proves the four portrait phones, including thumb reach, the P strategy for short
      and tall phones, and no scrolling in the gameplay core

### Step 3: balance-designer — the balance check

The `balance-designer` agent checks:

- [ ] The scoring formulas are correct and complete
- [ ] The level table in the GDD agrees with the balance config
- [ ] The latest `tools/simulate_balance.py` run PASSES and is newer than the last config change
- [ ] New elements arrive on easier levels; breathers follow spikes
- [ ] The config contains no currency, wager or odds fields

### Step 4: the report

```markdown
# Design Review — [system] — [date]

## Documents reviewed
- design/gdd/XXX.md — [status]

## 🚨 DEFICIENCIES (they block implementation)
- Section X is missing from document Y

## ⚠️ OBSERVATIONS
- Formula Z is incomplete

## ✅ MEETS THE STANDARD
- All 8 sections are present

## Recommendation: READY TO IMPLEMENT / NEEDS REVISION
```

## Arguments

- No arguments: review every GDD in `design/gdd/`
- `board-rules` — review `design/gdd/board-rules.md`
- `--balance-only` — the balance check only
