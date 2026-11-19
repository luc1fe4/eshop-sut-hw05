"""Recompute independently using Python statistics, compare with k6 summary."""
import collections, hashlib, json, statistics, sys
from pathlib import Path

folder=Path(sys.argv[1]);values=collections.defaultdict(list)
counts=collections.Counter();failures=collections.Counter()
raw=folder/'raw.json';digest=hashlib.sha256()
with raw.open('rb') as f:
    for line in f:
        digest.update(line);r=json.loads(line)
        if r['type']!='Point':continue
        m=r['metric'];d=r['data'];v=d['value'];tag=d.get('tags',{})
        counts[m]+=1
        if m=='http_req_duration':values['http_req_duration{endpoint:'+tag['endpoint']+'}'].append(v)
        if m in ['m5_e2e_all_ms','m5_e2e_success_ms']:values[m].append(v)
        if m=='http_req_failed':failures['http']+=v
        if m=='m5_e2e_success':failures['e2e']+=1-v
summary=json.loads((folder/'summary.json').read_text(encoding='utf-8-sig'))
checks=[]
for metric,observed in values.items():
    p95=statistics.quantiles(observed,n=100,method='inclusive')[94] if len(observed)>1 else observed[0]
    expected=summary['metrics'][metric]['values']['p(95)']
    checks.append({'metric':metric,'samples':len(observed),'independent_p95_ms':p95,'k6_p95_ms':expected,'abs_difference_ms':abs(p95-expected),'match':abs(p95-expected)<1e-7})
result={'method':'stdlib statistics.quantiles(n=100,method=inclusive), independent of analyzer percentile code',
    'raw_sha256':digest.hexdigest(),'p95_checks':checks,'all_p95_match':all(x['match'] for x in checks),
    'http_failure_numerator':failures['http'],'http_denominator':counts['http_req_failed'],
    'e2e_failure_numerator':failures['e2e'],'e2e_denominator':counts['m5_e2e_success'],
    'dropped_iterations_sample_count':counts['dropped_iterations']}
(folder/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
