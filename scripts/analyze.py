"""Independent analysis of k6 sample JSON (linear interpolated percentile)."""
import argparse, collections, datetime, json, math
from pathlib import Path

def percentile(values, q=.95):
    if not values: return None
    values = sorted(values)
    pos = (len(values)-1)*q
    lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] + (values[hi]-values[lo])*(pos-lo)

def analyze(folder):
    samples = collections.defaultdict(list)
    with (folder/'raw.json').open(encoding='utf-8-sig') as f:
        for line in f:
            r = json.loads(line)
            if r['type'] == 'Point':
                d = r['data']
                t = datetime.datetime.fromisoformat(d['time'].replace('Z','+00:00')).timestamp()
                samples[r['metric']].append((t,d['value'],d.get('tags',{})))
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
    start = datetime.datetime.fromisoformat(manifest['start']).timestamp()
    end = datetime.datetime.fromisoformat(manifest['end']).timestamp()
    window = end-start
    endpoints = {}
    for name in ['register','forgot','reset','login','cart']:
        durations = [v for t,v,tags in samples['http_req_duration'] if tags.get('endpoint')==name]
        failures = [v for t,v,tags in samples['http_req_failed'] if tags.get('endpoint')==name]
        endpoints[name] = {'samples':len(durations),'p95_ms':percentile(durations),
            'http_rps_wall_window':len(durations)/window,
            'http_failure_numerator':sum(failures),'http_failure_denominator':len(failures),
            'http_failure_rate':sum(failures)/len(failures) if failures else None,
            'draft_p95_lt_500ms':percentile(durations)<500 if durations else None}
    counts = {m:sum(v for _,v,_ in samples[m]) for m in ['m5_started','m5_finished','m5_passed','m5_csv_exhausted','iterations','dropped_iterations']}
    if not samples['dropped_iterations']:
        counts['dropped_iterations'] = None
    report = {'run_id':manifest['run_id'],'window':'manifest start/end (includes k6 startup/export overhead)',
        'window_seconds':window,'endpoints':endpoints,'counts':counts,
        'unfinished_started_minus_finished':counts['m5_started']-counts['m5_finished'],
        'e2e_all_finalized_p95_ms':percentile([v for _,v,_ in samples['m5_e2e_all_ms']]),
        'e2e_success_only_p95_ms':percentile([v for _,v,_ in samples['m5_e2e_success_ms']]),
        'e2e_think_time_included':False,
        'e2e_failure_rate_finalized':1-counts['m5_passed']/counts['m5_finished'] if counts['m5_finished'] else None,
        'e2e_success_throughput_wall_window':counts['m5_passed']/window,
        'dropped_iterations_observed':bool(samples['dropped_iterations']),
        'dropped_iterations_applicable':False,
        'note':'Closed VU executors; absent dropped_iterations is not an observed arrival-rate guarantee.'}
    (folder/'analysis.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('folder',type=Path)
    print(json.dumps(analyze(p.parse_args().folder),indent=2))
