"""Check generated public candidates against private test secrets; never print values."""
import csv, json, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
secrets=set()
for path in (root/'data').glob('*.csv'):
    for row in csv.DictReader(path.open(encoding='utf-8-sig')):
        secrets.update([row['password'],row['newPassword']])
tracked=subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode().split('\0')
targets=[root/x for x in tracked if x]+[p for p in (root/'results').rglob('*') if p.is_file() and p.suffix in ['.json','.html','.txt','.csv']]
matches=[]
for path in targets:
    # Scan incrementally to avoid loading large raw files on the load host.
    with path.open('r',encoding='utf-8',errors='ignore') as f:
        for line in f:
            # all random credentials start with Aa1! or Bb2!; filter before set comparisons
            if ('Aa1!' in line or 'Bb2!' in line) and any(s in line for s in secrets):
                matches.append(str(path.relative_to(root)));break
result={'private_secret_count':len(secrets),'files_scanned':len(targets),'credential_value_leak_paths':matches,
        'limits':'Synthetic CSV passwords only; reset tokens/JWT/cookies must also be reviewed structurally. Auth body logging is disabled.'}
(root/'results/secret-scan.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
raise SystemExit(bool(matches))
