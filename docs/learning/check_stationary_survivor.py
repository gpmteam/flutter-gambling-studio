from pathlib import Path
import subprocess

p = Path('.claude/rules/engine-code.md')
base = subprocess.check_output(['git', 'show', 'HEAD:' + str(p)]).decode()
current = p.read_text()
start = current.index('## Delta-plan presentation\n')
end = current.index('## Performance\n', start)
addition = current[start:end]
assert current[:start] + current[end:] == base
for phrase in ['only displaced pieces', 'stationary survivors', 'moving pieces and refills', 'outside `update()`/`render()`', 'never recompute gameplay', 'mid-fall frame', 'committed board and score']:
    assert phrase in addition, phrase
for name in ['.claude/rules/game-code.md', '.claude/rules/no-gambling.md', '.claude/rules/test-standards.md', '.claude/docs/mobile-first-contract.md', '.claude/docs/balance-models.md']:
    assert Path(name).read_bytes() == subprocess.check_output(['git', 'show', 'HEAD:' + name]), name
review = Path('docs/learning/stationary-survivor-review.md').read_text()
for phrase in ['failed before and pass after', 'not tests run in this framework worktree', 'no-allocation', 'byte-identical', 'final release visual replay']:
    assert phrase in review, phrase
print('PASS: scoped delta presentation obligation, unchanged prior rules/gates, recorded evidence and review limits.')
