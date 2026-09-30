# Balancing the difficulty curve: [System name]

**Category:** [G1–G6]
**Model:** [B1–B6]
**Target curve:** [e.g. "L1–3 ≥ 85% pass, final world 30–45%" / "median first run 60–90 s"]
**Config:** `design/balance/[level-config | endless-config].json`
**Date computed:** [date]

## Parameter table

For B1 (board levels):

| Level | Board | Kinds | Moves | Goal | New element | Player bot | Skilled bot |
|-------|-------|-------|-------|------|-------------|-----------|-------------|
| 1 | 7×8 | 4 | 20 | 1,800 pts | — (tutorial) | 100% | 100% |
| 5 | 7×8 | 5 | 18 | 1,550 pts | ice blocker | 61% | 89% |
| ... | | | | | | | |

For the other models, use the corresponding table: kinds/containers and par per level (B2), tier
chain and spawn weights (B3), layouts and shot budgets (B4), the tempo ramp (B5), level sizes and
par (B6).

## Levers
Symbol kinds, budgets, goals, blockers, specials, spawn weights, tempo — exactly how each moves the
pass rate or run length, and which levels act as breathers after a spike.

## Run results

```bash
python3 tools/simulate_balance.py --model [b1-b6|report] --config design/balance/[file].json
```

- Onboarding (L1–3, worst): [XX%]
- Hardest level (player / skilled): [XX% / XX%]
- Ramp (first quarter − last quarter): [XX pp]
- Verdict: [PASS / CONCERNS / FAIL]

The full report: `design/balance/simulation-report.md`.

> A run that is not written to a report does not count as having happened. The
> `simulation.last_run_date` field in the config is stamped by every run.
