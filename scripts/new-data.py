"""Generate a NEW, non-reusable private dataset. No credentials on stdout."""
import argparse, csv, secrets
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--run-id', required=True)
p.add_argument('--rows', type=int, required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
if not a.run_id.replace('-', '').replace('_', '').isalnum() or a.rows < 1:
    p.error('invalid run id or row count')
out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('x', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['name','email','password','newPassword'])
    for i in range(a.rows):
        w.writerow([f'M5 Test {i}', f'm5-{a.run_id}-{i}@example.invalid',
                    'Aa1!' + secrets.token_hex(12), 'Bb2!' + secrets.token_hex(12)])
print(f'Generated {a.rows} private rows: {out}')
