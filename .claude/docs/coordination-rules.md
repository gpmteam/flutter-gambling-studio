# Game Studio Coordination Rules

A mini-game succeeds when balance (difficulty and pacing), code design and juiciness stay in sync.

## Collaboration principles

1. **English**
   All interaction between the user and the agents — answers, questions, logs — is in
   **English**, and so is everything the studio produces: design documents, reports, code and
   the player-facing copy in the game itself. The only exception is an explicit user request
   for the game in another language, which affects the player-facing strings only. See
   `CLAUDE.md` → Language.

2. **A consultative style**
   Agents do not make decisions on their own without the user (except in the `/auto-*` skills).
   The pattern: *Ask a question → offer 2-3 options → the user chooses → write a draft →
   the user approves → save to file*.

3. **Respect the chain of command**
   - Only `creative-director` changes the core gameplay and the vision (pillars).
   - Only `balance-designer` approves a new balance model after `/balance-check` passes.
   - `mechanics-programmer` MAY NOT hardcode game parameters. They must be read from
     `GameConfig`/the GDD.
   - `mechanics-programmer` does not hardcode spawn weights or budgets, does not construct its own
     `Random()` (all gameplay randomness goes through the seeded `GameRng`), and never adds a
     chance-based reward (e.g. `if (Random().nextDouble() < 0.1) awardBooster();`).
   - `juice-artist` does not make an animation longer than 3–4 seconds, so the game loop does
     not slow down. `game-designer` approves the length.
   - Nobody lifts a no-gambling blocker (`.claude/rules/no-gambling.md`). No agent adds a wager,
     a currency or a chance-based reward "to make it more exciting"; `release-manager` enforces it.

## Conflict resolution

For evidence-backed framework learning, `.claude/skills/auto-learn/SKILL.md` has standing owner
authorization to implement and push tested `learning/*` proposals. This exception does not
authorize merging or silently changing active production rules; the owner reviews and merges.
Record reusable findings from every stage and deduplicate. Process them in a dedicated learning
task; do not interrupt production or prolong a blocked store run with learning implementation.
An explicit request for a framework fix keeps that fix as the primary task.

Mistakes are inevitable. If one mechanic contradicts another, pause and bring in the specialist:

**If the code contradicts the GDD:** `lead-programmer` and `game-designer` find common ground.
If a feature is impossible because of Flame's architecture, the GDD is updated.

**If the balance model is outside its window** (`tools/simulate_balance.py` returns FAIL):
production stops. Bring in `balance-designer`, who iterates ONLY on the numbers in the model's JSON
config. Only after a green run does `mechanics-programmer` update the code. The thresholds for
models B1–B6 are in `.claude/docs/balance-models.md`.

**If "prettier" conflicts with "honest":** honesty wins. Feedback shows exactly what the move
did; a fake "almost cleared" moment or a celebration bigger than the event is a breach of
game integrity, not a juice-artist's clever find.

## Handing off work

When passing a task from the balance designer → designer → programmer → VFX, use the `/team-dev`
skill. Each agent must pass the exact reference to the working documents (for example the GDD
at `design/gdd/[file].md`) to the next agent in the chain.
