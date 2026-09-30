# Component motion finder guidance review

This documentation-only proposal addresses one observed false test failure, not a
product animation defect. The evidence records three settled stars plus two
unrelated route transforms and the corrected 52-test pass.

- Scope: the rule applies to component property assertions inside a route host.
  It does not require every finder to be narrowed or alter application code.
- Cardinality: asserting the expected count prevents a narrower finder from
  silently omitting an expected star or other component node.
- Navigation: retaining the real route host preserves navigation and lifecycle
  coverage; route transitions remain independently testable.
- Integrity: the text explicitly forbids relaxing motion or lifecycle assertions.
  Seeded rules, scoring, balance, geometry and coverage thresholds are unchanged.
- Discovery: the correction belongs in the existing canonical test standards,
  immediately before coverage requirements; no extra skill or agent is needed.
- Verification: this is a structured guidance review. The application rerun is
  historical evidence, not a claim that an isolated framework worktree contains
  or executes the generated game's tests. A structural check verifies the scope,
  cardinality and integrity clauses plus all existing coverage thresholds.
