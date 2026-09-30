# Learning proposal: Preserve stationary survivors when rendering delta fall plans

Status: proposed; human review and merge required.

## Observed problem

A fall phase drew only displaced events and refills, so unchanged surviving tiles disappeared until reveal.

## Proposed improvement

Clarify delta-plan presentation: keep stationary survivors visible, precompute masks outside hot paths, and inspect a mid-fall frame.

Base commit: `0e4d3a8d373fa044f8e0e3941654884d5ce3337e`

## Source evidence

### stationary-survivor-evidence.md

SHA-256: `0e9a5e47f70200ac646c82c9bc4ca08983911e1e6e08a6b168a6174178d3d27d`

    # Stationary survivors vanished during the fall phase

    Observed in the final release phone capture: after a legal three-object top-row link, the frame briefly contained only incoming pieces while the HUD had already committed 30 points. Other board cells returned at reveal.

    Concrete diagnosis: BoardEngine publishes TileFall only when from != to. LinkBoardComponent's normal fall phase drew those displaced pieces and refills, omitting unchanged surviving pieces. The engine's before/after snapshots and score were correct. This was a rendering omission, not a balance or RNG problem.

    Reproduction: flutter test test/components/link_board_component_test.dart. Two actual-canvas pixel checks use engine-resolved top-row and bottom-row links and verify every stationary survivor's center retains alpha 255 at mid-fall. Before the fix, both failed at survivor 3 with actual alpha 0. The log is production/qa/stationary-survivors-before.log. After the fix, both pass; production/qa/stationary-survivors-after.log.

    Game repair: prepare a finite movement mask from the immutable plan outside render. Draw all unchanged surviving pieces, then moving pieces and refills. No allocations were added to render/update, and the engine, source assets, RNG, scoring and balance config are unchanged. The final Web release must be rebuilt and visually rechecked after this repair.

    Reusable discovery gap: logic-before-animation guidance already requires committed snapshots but did not make delta-plan composition explicit. A bounded engine presentation note should distinguish displaced events from the full field, require stationary survivors to remain visible, and require a mid-phase frame check. Do not change engine event semantics or animate gameplay rules to hide the omission.

## Validation

- Command: `["python3", "-B", "docs/learning/check_stationary_survivor.py"]`; exit 0; 2026-09-30T21:24:40.517523+00:00
  Output SHA-256: `9987d03b44c4141a32e2495e6c6c3571884289df9e30702a86903486160f3c51`

    PASS: scoped delta presentation obligation, unchanged prior rules/gates, recorded evidence and review limits.

