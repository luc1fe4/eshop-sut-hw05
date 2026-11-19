import argparse, json, sqlite3
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('db',type=Path); p.add_argument('--namespace',default='')
a=p.parse_args()
c=sqlite3.connect(a.db.resolve().as_uri()+'?mode=ro',uri=True)
state={'users':c.execute('SELECT count(*) FROM users').fetchone()[0],
       'journal_mode':c.execute('PRAGMA journal_mode').fetchone()[0]}
if a.namespace:
    state['namespace_summary']=dict(zip(['accounts','unique_emails','cleared_reset_tokens','zero_login_attempts'],
      c.execute('SELECT count(*),count(distinct email),sum(reset_token IS NULL),sum(login_attempts=0) FROM users WHERE email LIKE ?',('m5-'+a.namespace+'-%@example.invalid',)).fetchone()))
print(json.dumps(state,indent=2)); c.close()
