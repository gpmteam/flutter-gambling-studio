# Report format guidance review

- Observation: two preserved simulator Markdown reports carried `.json` names and correctly failed strict JSON validation during the no-gambling gate.
- Remedy: clarify serialization in the existing data-files rule; the active task preserves both reports under `.md` names.
- The simulator’s `--report` writer is Markdown. Machine-readable balance configs and actual-engine bot reports remain JSON.
- All original category/model tables, thresholds, seeded rules and forbidden fields remain byte-identical outside the inserted guidance.
- Referenced simulator and no-gambling checker exist. Neither tool changes in this proposal.
- Validation checks the exact original rule after removing the insertion and verifies the Markdown writer’s existing CLI/source references.
