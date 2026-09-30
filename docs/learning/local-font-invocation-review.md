# Local Web resource claim invocation review

Observed failure: a normally served Flutter Web build passed gameplay, yet a new profile with external requests blocked requested an engine Roboto fallback and failed startup. Inspection of the installed engine confirmed that the fallback family was absent from the generated manifest. A compatible local alias passed the subsequent cold profile check. This is version-specific evidence, not a universal requirement to rename fonts.

Existing technical-preferences guidance already describes the necessary check and conditional remedy. The proposed correction links that existing section at the player-facing UI accessibility rules, where a locally served or offline claim can otherwise bypass resource verification.

Structured review findings:
- Every preexisting UI rule is byte-identical after removing the inserted paragraph.
- The linked document and exact section exist in the remote-base worktree.
- The paragraph requires both startup and gameplay, a fresh profile, and blocked external requests.
- Existing typography, phone layouts, touch targets, cancellation and no-gambling rules remain unchanged.
- No version-specific font workaround is imposed by the new paragraph.
- This guidance-only proposal changes no application file, dependency or SDK; it does not establish serverless/PWA support.
