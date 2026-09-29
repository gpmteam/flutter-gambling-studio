# Learning proposal: Fit panorama references within built-in image limit

Status: proposed; human review and merge required.

## Observed problem

The store panorama runbook lists six attached image references, while built-in image generation accepts at most five; the first call was rejected.

## Proposed improvement

Keep the five authoritative inputs attached and inspect matching previews separately when the image tool has a five-reference limit.

Base commit: `67468a8fd24e403ab0a67f8960134167f778cc91`

## Source evidence

### store-reference-limit-evidence.txt

SHA-256: `7ab35dd1f86a00481ae771344364ad7c4088cba39eb350efff69ac5be3344a7a`

    During Joker's Jewels /store-screenshots on 2026-09-29, a built-in image generation call that attached six panorama references failed immediately: the tool permits at most five referenced images. The six were the original character, accepted banner, original multiplier asset, real gameplay capture, shipped-symbol contact sheet, and matching-preview contact sheet. The current `.claude/skills/store-screenshots/SKILL.md` panorama step instructs attaching all six in that order. Retrying with the first five attached and inspecting the preview sheet separately succeeded. The prompt still cited the preview identity, and the final panorama met the reference-game visual and gameplay topology checks. This is a tool-input limit, not a reason to omit the required character, ball, banner, gameplay capture, or visible shipped sprites.

## Validation

- Command: `["git", "diff", "--check"]`; exit 0; 2026-09-29T19:56:07.996891+00:00
  Output SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Command: `["python3", "-c", "from pathlib import Path; p=Path(\".claude/skills/store-screenshots/SKILL.md\").read_text(); section=p.split(\"### 1b \u2014 Panorama\",1)[1].split(\"Only for\",1)[0]; terms=(\"original character asset\",\"accepted banner\",\"multiplier reference\",\"gameplay\\ncapture\",\"visible shipped sprites\"); assert all(t in section for t in terms), \"authoritative source missing\"; assert section.index(\"visible shipped sprites\") < section.index(\"matching previews\"), \"preview displaced required sources\"; assert \"sixth reference\" in section and \"five-image limit\" in section, \"tool limit not handled\"; assert \"Inspect the matching previews\" in section, \"preview review lost\"; print(\"PASS: five authoritative panorama inputs retained; sixth preview is conditional and still inspected\")"]`; exit 0; 2026-09-29T19:56:21.630239+00:00
  Output SHA-256: `550a2549998c54f3f3d60c183eb6d9961906b1f2a178830418cb36b97d95aa66`

    PASS: five authoritative panorama inputs retained; sixth preview is conditional and still inspected

