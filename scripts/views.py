"""Three distinct views from real samples, plus soak windows/resources."""
import collections, csv, datetime as dt, html, json, math, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime/pydeps'))
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'runtime/mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze import analyze, percentile

STAGES={
 'Load':[(30,5),(120,5),(15,0)],
 'Stress':[(15,5),(45,5),(15,15),(45,15),(15,30),(45,30),(15,0)],
 'Spike':[(15,5),(45,5),(2,40),(30,40),(2,5),(60,5),(10,0)]}

def main(folder):
    result=analyze(folder)
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
    samples=collections.defaultdict(list)
    for line in (folder/'raw.json').open(encoding='utf-8-sig'):
        r=json.loads(line)
        if r['type']=='Point':
            d=r['data']; samples[r['metric']].append((dt.datetime.fromisoformat(d['time'].replace('Z','+00:00')).timestamp(),d['value'],d.get('tags',{})))
    # Earliest VU gauge is emitted by k6's periodic 1-second collector.
    # This is an inferred run clock, NOT the first iteration (ramp from zero delays it).
    # Keep a conservative 2-second margin off each hold boundary for jitter.
    direct_clock = [v/1000 for _,v,_ in samples['m5_scenario_start_epoch_ms']]
    if direct_clock:
        if max(direct_clock)-min(direct_clock)>0.001:raise ValueError('Multiple scenario clocks found')
        origin=direct_clock[0]
        clock_method='direct k6 scenario.startTime; 2s trimmed on each hold edge'
    else:
        origin=min(t for t,_,_ in samples['vus'])-1
        clock_method='inferred from first 1-second VU gauge minus 1s; timing uncertainty not exactly bounded; 2s trimmed on each hold edge'
    if manifest['kind']=='soak':
        seconds=600 if manifest['duration']=='10m' else int(manifest['duration'].rstrip('s'))
        stages=[(min(60,seconds-i),manifest['vus']) for i in range(0,seconds,60)]
    elif manifest['stages_override']:
        stages=[(int(x['duration'].rstrip('s')),x['target']) for x in json.loads(manifest['stages_override'])]
    else: stages=STAGES[manifest['profile']]
    def window(begin,end,label,vu):
        def get(metric):return [v for t,v,_ in samples[metric] if begin <= t-origin < end]
        hd=get('http_req_duration'); hf=get('http_req_failed'); es=get('m5_e2e_success'); ok=get('m5_passed'); ed=get('m5_e2e_all_ms')
        return {'phase':label,'start_seconds':begin,'end_seconds':end,'target_vus':vu,
            'observed_vus_min':min(get('vus'),default=None),'observed_vus_max':max(get('vus'),default=None),
            'http_samples':len(hd),'http_rps':len(hd)/(end-begin),'http_p95_ms':percentile(hd),
            'http_failed':sum(hf),'http_failure_denominator':len(hf),'http_failure_rate':sum(hf)/len(hf) if hf else None,
            'e2e_finalized':len(es),'e2e_failed':len(es)-sum(es),'e2e_p95_all_ms':percentile(ed),
            'successful_e2e_per_s':sum(ok)/(end-begin)}
    phases=[]; elapsed=0; last=0
    for index,(seconds,target) in enumerate(stages):
        hold=target==last or manifest['kind']=='soak'
        begin=elapsed+2 if hold else elapsed
        end=elapsed+seconds-2 if hold else elapsed+seconds
        phases.append(window(begin,end,f'{"hold" if hold else "ramp"}-{index+1}',target))
        elapsed+=seconds; last=target
    bins=[window(i,min(i+5,elapsed),f'{i}-{min(i+5,elapsed)}s',None) for i in range(0,elapsed,5)]
    resources=[]
    if (folder/'resources.csv').exists():
        previous=None
        for row in csv.DictReader((folder/'resources.csv').open(encoding='utf-8-sig')):
            when=dt.datetime.fromisoformat(row['time']).timestamp()
            cpu=float(row['cpu_seconds'])
            resources.append({'seconds':when-origin,'rss_mib':int(row['working_set_bytes'])/1048576,
                'cpu_percent_machine':(cpu-previous[1])/(when-previous[0])*100/16 if previous else None,
                'k6_rss_mib':float(row.get('k6_working_set_bytes') or 0)/1048576,
                'system_cpu_percent':float(row['system_cpu_percent']) if row.get('system_cpu_percent') else None,
                'system_available_mib':float(row['system_available_bytes'])/1048576 if row.get('system_available_bytes') else None})
            previous=(when,cpu)
    (folder/'phases.json').write_text(json.dumps({'origin_epoch':origin,'clock_method':clock_method, 'allocation':'request/iteration completion timestamp; boundary-crossing requests assigned by completion',
        'phases':phases,'timeline_5s':bins,'resources':resources},indent=2),encoding='utf-8')
    with (folder/'phases.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(phases[0]));w.writeheader();w.writerows(phases)
    if manifest['profile']=='Load' and manifest['kind']!='soak':
        body='<h2>Endpoint aggregate table (entire run)</h2><table><tr><th>Endpoint</th><th>n</th><th>p95 ms</th><th>RPS</th><th>HTTP failure</th><th>p95&lt;500ms</th></tr>'
        for key,v in result['endpoints'].items():
            body+=f'<tr><td>{key}</td><td>{v["samples"]}</td><td>{v["p95_ms"]:.4f}</td><td>{v["http_rps_wall_window"]:.4f}</td><td>{v["http_failure_numerator"]}/{v["http_failure_denominator"]}</td><td>{v["draft_p95_lt_500ms"]}</td></tr>'
        body+='</table><p>RPS denominator: manifest wall interval including startup/export. See phases.csv for steady hold only.</p>'
        title='Load - endpoint aggregate table'
    elif manifest['profile']=='Stress':
        holds=[p for p in phases if p['phase'].startswith('hold')]
        fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True)
        x=[p['target_vus'] for p in holds]
        for ax,key,label in zip(axes,['http_rps','http_p95_ms','http_failure_rate'],['HTTP RPS','HTTP p95 (ms)','HTTP failure rate']):
            ax.plot(x,[p[key] for p in holds],'o-');ax.set_ylabel(label);ax.grid(alpha=.3)
        axes[-1].set_xlabel('Configured VUs (steady hold only)');fig.suptitle(manifest['run_id']);fig.tight_layout();fig.savefig(folder/'stress-stages.png',dpi=140);plt.close(fig)
        body='<img src="stress-stages.png" alt="Stress stage throughput latency error chart"><p>Only hold phases; completion-time allocation. Detailed denominators in phases.csv.</p>'
        title='Stress - stepped load comparison'
    else:
        is_soak=manifest['kind']=='soak'
        fig,axes=plt.subplots(4 if is_soak else 3,1,figsize=(11,10),sharex=True)
        x=[(p['start_seconds']+p['end_seconds'])/2 for p in bins]
        axes[0].plot(x,[p['http_rps'] for p in bins],label='HTTP RPS');axes[0].legend()
        vu=samples['vus'];axes[0].twinx().plot([t-origin for t,_,_ in vu],[v for _,v,_ in vu],color='gray',alpha=.6,label='actual VUs')
        axes[0].set_ylabel('RPS / VU (right)')
        axes[1].plot(x,[p['http_p95_ms'] for p in bins],label='HTTP p95');axes[1].plot(x,[p['e2e_p95_all_ms'] for p in bins],label='E2E p95');axes[1].set_ylabel('ms');axes[1].legend()
        axes[2].plot(x,[p['http_failure_rate'] for p in bins],label='HTTP failure');axes[2].set_ylabel('rate');axes[2].legend()
        if is_soak:
            axes[3].plot([p['seconds'] for p in resources],[p['rss_mib'] for p in resources],label='backend RSS MiB')
            axes[3].twinx().plot([p['seconds'] for p in resources],[p['cpu_percent_machine'] for p in resources],color='orange',label='CPU % machine')
            axes[3].set_ylabel('RSS MiB / CPU % (right)');axes[3].legend()
        else:
            for ax in axes:
                for begin,end,color in [(15,60,'green'),(62,92,'red'),(94,154,'blue')]:ax.axvspan(begin,end,color=color,alpha=.08)
        for ax in axes:ax.grid(alpha=.3)
        axes[-1].set_xlabel(('Seconds from scenario.startTime' if direct_clock else 'Seconds from inferred k6 clock')+'; 5-second bins')
        fig.suptitle(manifest['run_id']);fig.tight_layout()
        filename='soak-windows.png' if is_soak else 'spike-timeline.png'
        fig.savefig(folder/filename,dpi=140);plt.close(fig)
        body=f'<img src="{filename}" alt="Measured timeline"><p>5-second bins; p95 bins with few samples are noisy. See phases.csv for holds and recovery. Think-time excluded from E2E.</p>'
        title='Soak - time windows and resources' if is_soak else 'Spike - baseline peak recovery timeline'
    page=f'<!doctype html><meta charset="utf-8"><title>{html.escape(title)}</title><style>body{{font:16px Arial;max-width:1150px;margin:40px auto;color:#172b4d}}table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;border:1px solid #ccc}}th{{background:#e7eef7}}img{{max-width:100%}}</style><h1>{title}</h1><p>{manifest["run_id"]}</p>{body}<p>Source: raw.json, manifest.json, resources.csv; scripts/views.py. No synthetic measurements.</p>'
    (folder/'view.html').write_text(page,encoding='utf-8')
    print(json.dumps({'run':manifest['run_id'],'phases':phases,'resources_samples':len(resources)},indent=2))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);main(p.parse_args().folder)
