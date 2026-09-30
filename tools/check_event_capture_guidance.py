"""Validate one bounded, guidance-only insertion and its existing reference."""
from pathlib import Path
import subprocess
p = Path('.claude/docs/technical-preferences.md')
text = p.read_text()
start = text.index('### Transient gameplay capture evidence\n')
end = text.index('## Flutter + Flame 1.18.x\n', start)
section = text[start:end]
baseline = subprocess.check_output(['git', 'show', 'HEAD:.claude/docs/technical-preferences.md']).decode()
assert text[:start] + text[end:] == baseline, 'Prior guidance changed'
assert text.count('### Transient gameplay capture evidence') == 1
runbook = Path('.claude/skills/playtest/SKILL.md').read_text()
assert all(item in runbook for item in ('| P1 |', '| P2 |', '| P5 |'))
for phrase in ('P1/P2/P5', 'when that state is actually observed',
               'assert it in the saved screenshot state', 'fixed action index',
               'Inspect the pixels', 'Preserve mislabeled raw captures',
               'supplemental runs separately', 'never inject an engine state'):
    assert phrase in section, phrase
assert Path('docs/learning/event-capture-guidance-review.md').is_file()
print('PASS: prior bytes preserved, existing P1/P2/P5 reference, scoped capture/assert/vision/preservation obligations')
