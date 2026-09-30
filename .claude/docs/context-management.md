# Context management — Flutter Game Studio

Context is a critical resource in a session. Manage it actively.

## File-backed state (the main strategy)

**The file is the memory, not the conversation.** Conversations are ephemeral and will be
compacted or lost. Files on disk survive compaction and restarts.

### The session state file

Keep `production/session-state/active.md` as a living checkpoint.
Update it after every meaningful step.

```markdown
<!-- STATUS -->
Epic: Thunder Link
Feature: Board engine
Task: Implement the link-chain resolver
<!-- /STATUS -->

## Current task
[What we are doing]

## Progress
- [x] GDD written
- [x] level-config.json → B1 PASS (L1–3 ≥ 90%, hardest 31%)
- [ ] Link-chain resolver — in progress
- [ ] Resolver tests
- [ ] Clear animation

## Key decisions
- Using a sealed class GameState (ADR-001)
- RNG: one seeded GameRng injected into the board engine
- Chains of 6+ call down a bolt that clears a column

## Files in flight
- lib/systems/board_engine.dart
- test/systems/board_engine_test.dart
- design/gdd/board-rules.md

## Open questions
- Should diagonal links be allowed on the 7×6 board?

## Last compaction
[date and time — updated automatically by the hook]
```

### Writing documents incrementally

When creating a GDD or an ADR (multi-section documents):
1. Create the file immediately with all the headings (empty)
2. Discuss and write one section at a time
3. Write each section to the file once it is approved
4. Update `active.md` after every section
5. Earlier discussion of finished sections can safely be compacted — the decisions are in the file

### After any failure (compaction, crash)

1. The `session-start.sh` hook automatically shows `active.md`
2. Read the full state file to restore context
3. Read the files that were in flight
4. Continue from the unfinished task

## Proactive compaction

- Compact proactively at around 60–70% context usage
- Use `/clear` between unrelated tasks
- Natural compaction points: after writing a section to a file, after a commit, after
  finishing a task

```
/compact Focus on [current task] — sections 1-3 are written to the file, we are on section 4
```

## Context budgets by task type

| Task | Budget | Notes |
|------|--------|-------|
| Reading/reviewing a GDD | ~3k tokens | A quick read |
| Implementing one component | ~8k tokens | Read the files + write |
| Refactoring several files | ~15k tokens | Analysis + changes |
| A full /autocreate pipeline | ~40k tokens | Many parallel tasks |

## Delegating to sub-agents

Use sub-agents to protect the main context:
- Research across many files → an Explore sub-agent
- Deep analysis → a Plan sub-agent
- Code review → `/code-review` (which uses several agents)
- Sub-agents receive full context in the prompt — they do not inherit the conversation history

## Game-specific strategy

### Balancing — fast cycles

Balance iterations (parameters → simulation → adjustment) repeat many times. Each cycle saves
context:

The cycle is the same in every category — only the config and the model change:

```bash
# edit the numbers in JSON → run → read the verdict
python3 tools/simulate_balance.py --model b1 --config design/balance/level-config.json --trials 20
```

| Category | What `balance-designer` turns | Model |
|----------|-------------------------------|-------|
| G1 | Symbol kinds, move budgets, targets, collect goals | B1 |
| G2 | Kinds, layers, empty containers, generator policy | B2 |
| G3 | Board size, spawn table, goal tier | B3 |
| G4 | Layouts, shot budgets, target counts | B4 |
| G5 | Tempo ramp, reaction windows, grace period | B5 |
| G6 | Level size, constraints, move/time budgets | B6 |

Do NOT keep all the balance numbers in the conversation. It lives in files — the config and the
report survive compaction.

### After /balance-check

The simulation/analysis result is written to `design/balance/simulation-report.md`.
Compact the context afterwards — every decision is in the file.

## What to preserve when compacting

Save this to `active.md` before compacting:
- A pointer to `active.md` (read it to restore)
- The list of changed files and what each is for
- Architectural decisions and their rationale
- The current task and the next step
- Open questions awaiting a user answer
- Test status (green/red)
- The game's category (G1–G6), its balance model (B1–B6) and the latest run verdict
