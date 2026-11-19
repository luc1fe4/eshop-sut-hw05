import hashlib,json
from pathlib import Path
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1]
runs=[];inventory=[]
for manifest in sorted((root/'results').glob('*/manifest.json')):
    m=json.loads(manifest.read_text(encoding='utf-8-sig'));folder=manifest.parent
    item={'run_id':m['run_id'],'kind':m['kind'],'profile':m['profile'],'status':m['status'],'exit_code':m.get('exit_code')}
    if (folder/'controller-stop-note.json').exists():
        stop=json.loads((folder/'controller-stop-note.json').read_text())
        item['manifest_status_as_recorded']=item['status'];item['status']=stop['status']
        item['controller_exit_code']=stop['controller_exit_code']
    if m['status']=='completed':
        assert (folder/'raw.json').stat().st_size>0
        assert (folder/'summary.json').stat().st_size>0
        s=json.loads((folder/'summary.json').read_text(encoding='utf-8-sig'))
        item['e2e_passed']=s['metrics']['m5_passed']['values']['count']
        item['e2e_p95_ms']=s['metrics']['m5_e2e_success_ms']['values']['p(95)']
        item['http_samples']=s['metrics']['http_reqs']['values']['count']
        if m['kind'] in ['official','soak']:
            assert (folder/'view.html').exists() and (folder/'dashboard.html').exists()
            v=json.loads((folder/'verification.json').read_text());assert v['all_p95_match']
            assert item['http_samples']==item['e2e_passed']*5
            item['independent_p95_match']=True
    runs.append(item)
assert {r['profile'] for r in runs if r['kind']=='official'}=={'Load','Stress','Spike'}
assert any(r['kind']=='soak' and r['status']=='completed' for r in runs)
for scenario in ['Load','Stress','Spike']:
    assert (root/'plans'/f'23120330_{scenario}_20261119.js').exists()
pdfs={}
for path in (root/'output/pdf').glob('*.pdf'):
    reader=PdfReader(path);txt=''.join(p.extract_text() or '' for p in reader.pages)
    assert '23120330' in txt
    pdfs[path.name]=len(reader.pages)
assert len(pdfs)==3
state=json.loads((root/'submission-state.json').read_text(encoding='utf-8-sig'))
photo_checks=[]
for profile,relative in state['resource_screenshots'].items():
    if not relative:continue
    photo=root/relative;folder=photo.parent
    proof=json.loads((folder/'screenshot-evidence.json').read_text(encoding='utf-8-sig'))
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
    assert proof['profile']==profile and proof['run_id']==state['resource_screenshot_runs'][profile]
    assert manifest['status']=='completed' and manifest['profile']==profile
    assert hashlib.sha256(photo.read_bytes()).hexdigest()==proof['sha256']
    verification=json.loads((folder/'verification.json').read_text())
    assert verification['all_p95_match']
    assert (folder/'dashboard.html').exists() and (folder/'view.html').exists()
    photo_checks.append({'profile':profile,'run_id':proof['run_id'],'image':relative,'sha256_verified':True,'completed_raw_matched':True})
for directory in ['docs','plans','skills','output/pdf','data','results']:
    for path in (root/directory).rglob('*'):
        if not path.is_file() or path.name in ['artifact-inventory.json','final-check.json']:continue
        with path.open('rb') as f:
            digest=hashlib.file_digest(f,'sha256').hexdigest()
        inventory.append({'path':str(path.relative_to(root)),'bytes':path.stat().st_size,'sha256':digest})
(root/'results/artifact-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
result={'technical_artifact_checks_passed':True,'submission_complete':False,
        'runs':runs,'pdf_pages':pdfs,'resource_photo_checks':photo_checks,
        'remaining':'Human review, full chat export, hostname continuity, real public GitHub/YouTube URLs, grade and final ZIP.'}
(root/'results/final-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
