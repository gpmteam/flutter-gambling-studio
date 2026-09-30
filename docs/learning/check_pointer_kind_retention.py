from pathlib import Path
import subprocess
p=Path('.claude/rules/ui-code.md');s=p.read_text()
b=subprocess.check_output(['git','show','HEAD:.claude/rules/ui-code.md'],text=True)
start=s.index('\n### Historical pointer-kind maps');end=s.index('\n---',start);a=s[start:end]
for item in ['forced-GC','historical pointer-kind map','pinned implementation','separately','tap-only control','primary down kind','permission checks','standard arena tracking','callback','unbounded replacement map','supported gestures','simultaneous pointers','canceled drags','active touch/mouse/pen','keyboard and semantic','unchanged touch bounds','previously','stable DOM','pinned SDK','strong retention path','regression evidence']:
 assert item in a,item
assert s[:start]+s[end:]==b
for file in ['.claude/docs/mobile-first-contract.md','.claude/rules/test-standards.md','.claude/rules/no-gambling.md','.claude/rules/engine-code.md']:
 assert Path(file).read_bytes()==subprocess.check_output(['git','show','HEAD:'+file]),file
r=Path('docs/learning/pointer-kind-retention-review.md').read_text()
for item in ['619→649','709→809','609→609','115','guidance-only','strong path','permission checks','unmerged arena-entry proposal']:
 assert item in r,item
print('PASS: traced map-specific diagnosis, bounded primary kind, preserved input/accessibility, independent owner checks and unchanged existing gates.')
