from pathlib import Path
import subprocess
p=Path('.claude/docs/technical-preferences.md');base=subprocess.check_output(['git','show','HEAD:'+str(p)]).decode();t=p.read_text()
addition='Confirm the profile directory does not already exist before launch; choose a new output\ndirectory rather than mixing historical captures or cache with the current run. Preserve\nprior evidence and reject accidental profile reuse before writing new browser data.\n'
assert t.count(addition)==1
assert t.replace(addition,'')==base
for f in ['.claude/rules/no-gambling.md','.claude/docs/balance-models.md','.claude/docs/mobile-first-contract.md','.claude/skills/autocreate-finalize/SKILL.md']:
 assert Path(f).read_bytes()==subprocess.check_output(['git','show','HEAD:'+f])
r=Path('docs/learning/fresh-profile-review.md').read_text()
for phrase in ['three-line','before starting','rather than a framework browser test','byte-identical','must still pass']:
 assert phrase in r
print('PASS: freshness precondition is scoped; prior technical guidance and runtime gates preserved; review limits recorded.')
