# Route initialization guidance review

Observed failure: a new gameplay route started a session in didChangeDependencies.
The service synchronously published statistics to the menu still mounted behind it,
causing Flutter's publication-during-build exception. Daily refresh exposed the same
cause. The active game fixes defer those publishing calls to guarded post-frame
callbacks; its 14 real-navigation and geometry tests passed on 2026-09-30.

This proposal changes only existing UI guidance. It does not import game code or
adopt the proposal in the active project. Existing guidance covers async mounted
checks and notifier disposal, which do not explain this separate initialization case.

Review findings:

- Scope: only initialization that publishes to other mounted listeners is deferred.
  Pure local constructors retain their normal lifecycle.
- Ownership: the example schedules once and checks mounted before starting a session.
  The required disposal-before-callback scenario protects abandoned routes.
- Repetition: the one-time guard prevents dependency rebuilds from starting extra runs.
- Gameplay integrity: the rule explicitly retains engine commit before animation.
- Regression scenario: real navigation retains a listening menu under the new route;
  repeated dependencies and early disposal are required verification cases.
- Boundaries: no RNG, balance, no-gambling, assets, layout or authorization rules change.

Validation is a structured documentation review plus a check of the relevant rule
section, guard order and review findings. No claim is made that this documentation
example was compiled in the isolated framework worktree. The observed game's tests
are evidence of the remedy, not tests of every future service or route.
