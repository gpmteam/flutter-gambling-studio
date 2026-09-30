# Learning proposal: Reject reused browser profiles before cold Web verification

Status: proposed; human review and merge required.

## Observed problem

A supposedly final output directory already carried a browser profile and historical contacts; mixing them invalidated a fresh-profile evidence claim.

## Proposed improvement

Add a directory-freshness precondition to the existing cold-profile verification requirement; preserve earlier evidence and choose a new output directory.

Base commit: `0e4d3a8d373fa044f8e0e3941654884d5ce3337e`

## Source evidence

### learning-fresh-profile-evidence.md

SHA-256: `14db80bbda1040f2b35a57151ee2944fa7f334ee601835c2af28b3dd248f0d86`

    # Reused verification output carried historical browser evidence

    The final Chrome QA attempt selected 20260930-web-final, assuming it was unused. Inspection found phones-review.png dated 20:21 and a historical chrome-profile while the current menu capture was dated 21:24. The process was deliberately interrupted; no game failure was asserted, but old and new evidence could not establish a clean-profile claim. The mixed directory is explicitly INVALIDATED.md and is retained for provenance.

    Repair: Chrome QA launch rejects an existing chrome-profile before starting its server or writing browser data. The final rerun uses a new output directory. A synthetic occupied profile causes the guard to fail before server/browser launch; no prior evidence is deleted. Existing technical preferences already require a cold new profile, but the runbook does not instruct verifying directory freshness. The proposed guidance should add that one concrete check, without changing runtime or release gates.

## Validation

- Command: `["python3", "-B", "docs/learning/check_fresh_profile.py"]`; exit 0; 2026-09-30T21:30:05.951411+00:00
  Output SHA-256: `8821e8f874b501d5a3724ced8264e6ef4f0746802426e1cd4bc01c5780cb834c`

    PASS: freshness precondition is scoped; prior technical guidance and runtime gates preserved; review limits recorded.

