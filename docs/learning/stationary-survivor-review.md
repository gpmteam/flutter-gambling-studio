# Delta-plan presentation review

The proposal addresses one observed omission: rendering displaced events as though they were the whole field. It adds eight lines to the existing engine rule rather than duplicating a skill or changing pure-engine semantics. The current game's two pixel regressions failed before and pass after a movement-mask repair; these are app evidence, not tests run in this framework worktree.

Review findings:
- Stationary survivors, moving pieces and refills all participate in the resolved visual plan.
- Masks are prepared outside render/update; the previous no-allocation requirement remains intact.
- The rule requires visual evidence at mid-fall for small clears and displaced-piece clears.
- Gameplay is still committed first; no animation mutates score, RNG or the board.
- All prior engine guidance is byte-identical outside the inserted section.
- Game-code, no-gambling, test-standards, phone contracts and balance requirements are untouched.

The proposal does not claim every game uses fall deltas and does not ban still idle frames or require additional cosmetic motion. A final release visual replay is still required for this game after the fix.
