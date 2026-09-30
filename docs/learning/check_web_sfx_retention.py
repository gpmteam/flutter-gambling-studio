from pathlib import Path
import subprocess
p=Path('.claude/docs/technical-preferences.md')
current=p.read_text()
base=subprocess.check_output(['git','show','HEAD:.claude/docs/technical-preferences.md'],text=True)
start=current.index('- On Web, diagnose growing native audio nodes')
end=current.index('\n### Graphical assets',start)
addition=current[start:end]
assert 'strong retaining paths' in addition
assert 'installed backend' in addition and 'backend-specific' in addition
assert 'finite SFX catalog' in addition and 'three concurrently playing voices' in addition
assert 'dispose every prepared player' in addition and 'cancellation' in addition
assert current.replace(addition,'')==base
assert Path('.claude/rules/no-gambling.md').is_file()
review=Path('docs/learning/web-sfx-retention-review.md').read_text()
assert '20→80' in review and '3→3' in review and 'guidance only' in review
print('PASS: conditional cause/remedy, retained-source verification, active-voice cap, disposal, review evidence and unchanged prior guidance.')
