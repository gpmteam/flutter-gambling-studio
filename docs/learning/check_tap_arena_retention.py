from pathlib import Path
import subprocess
p=Path('.claude/rules/ui-code.md');s=p.read_text()
b=subprocess.check_output(['git','show','HEAD:.claude/rules/ui-code.md'],text=True)
a=s[s.index('### Pinned recognizer retention'):s.index('\n---',s.index('### Pinned recognizer retention'))]
for requirement in ['forced-GC','arena-entry map','confirmed pinned-version','after normal tap callbacks','gesture competition','canceled drags','simultaneous pointers','keyboard/semantic','unchanged touch bounds','pinned SDK','no measured retention path']:
 assert requirement in a, requirement
assert s.replace(a,'').replace('48x48\n\n\n---','48x48\n\n---')==b
assert Path('.claude/docs/mobile-first-contract.md').is_file()
r=Path('docs/learning/tap-arena-retention-review.md').read_text()
assert '10→40' in r and '0→0' in r and 'separate device-kind map' in r
print('PASS: conditional arena diagnosis, scoped settlement, preserved input/semantics/bounds, actual review and unchanged prior guidance.')
