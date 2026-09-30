from pathlib import Path
import subprocess
p=Path('.claude/docs/technical-preferences.md');s=p.read_text()
b=subprocess.check_output(['git','show','HEAD:.claude/docs/technical-preferences.md'],text=True)
a=s[s.index('### Pinned Web touch-state retention'):s.index('### Web font and engine resource verification')]
for requirement in ['strong retaining paths','raw down/up/cancel/leave','When this exact','only finished touch leaves','active touch, mouse and pen','up/cancel delivery','scrolling and real gameplay','forced-GC','SDK/native versions pinned','path is absent']:
 assert requirement in a, requirement
assert s.replace(a,'')==b
assert Path('.claude/docs/mobile-first-contract.md').is_file()
r=Path('docs/learning/touch-state-retention-review.md').read_text()
assert '20→80' in r and '0→0' in r and 'Raw Chrome probe' in r
print('PASS: event/root evidence, conditional scope, input propagation, pinned versions, repeated heap verification, actual review and unchanged prior guidance.')
