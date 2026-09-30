from pathlib import Path
import subprocess
p=Path('.claude/rules/ui-code.md')
s=p.read_text()
addition='Player-facing claims that a served Web game starts without external resources require\nthe fresh-profile, external-request-blocked startup and gameplay verification in\n`.claude/docs/technical-preferences.md` → "Web font and engine resource verification".\nBundled theme fonts or a normal-network run alone do not establish that behavior.\n\n'
base=subprocess.check_output(['git','show','HEAD:.claude/rules/ui-code.md'],text=True)
assert s.count(addition)==1 and s.replace(addition,'')==base
linked=Path('.claude/docs/technical-preferences.md').read_text()
assert '### Web font and engine resource verification' in linked
for text in ['startup and gameplay', 'fresh-profile', 'external-request-blocked']:
 assert text in addition
assert Path('docs/learning/local-font-invocation-review.md').is_file()
assert 'Roboto' not in addition and 'PWA' not in addition
print('PASS: prior rules preserved; exact link, cold startup/gameplay obligations, scoped remedy and review verified')
