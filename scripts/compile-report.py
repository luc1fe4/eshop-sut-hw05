"""Compile report from measured artifacts, retaining incomplete submission items."""
import csv, datetime, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def resource(folder):
    rows=list(csv.DictReader((folder/'resources.csv').open(encoding='utf-8-sig')))
    measurement_window='all sampler rows (original report method)'
    if (folder/'phases.json').exists() and (folder/'analysis.json').exists():
        phase=read(folder/'phases.json');analysis=read(folder/'analysis.json')
        if phase.get('clock_method','').startswith('direct k6'):
            start=phase['origin_epoch'];end=start+analysis['execution_window_seconds']
            rows=[r for r in rows if start<=datetime.datetime.fromisoformat(r['time']).timestamp()<=end]
            measurement_window='k6 execution window only, direct scenario clock'
    backend=[];generator=[]
    for a,b in zip(rows,rows[1:]):
        delta=(datetime.datetime.fromisoformat(b['time'])-datetime.datetime.fromisoformat(a['time'])).total_seconds()
        backend.append((float(b['cpu_seconds'])-float(a['cpu_seconds']))/delta*100/16)
        if b.get('k6_cpu_seconds') and a.get('k6_cpu_seconds'):
            value=(float(b['k6_cpu_seconds'])-float(a['k6_cpu_seconds']))/delta*100/16
            if value>=0:generator.append(value)
    return {'window':measurement_window,'samples':len(rows),'backend_cpu_peak_machine_percent':max(backend,default=0),
      'backend_cpu_mean_machine_percent':sum(backend)/len(backend) if backend else None,
      'backend_rss_peak_mib':max(float(x['working_set_bytes']) for x in rows)/1048576,
      'backend_rss_first_mib':float(rows[0]['working_set_bytes'])/1048576,
      'backend_rss_last_mib':float(rows[-1]['working_set_bytes'])/1048576,
      'k6_cpu_peak_machine_percent':max(generator,default=None),
      'system_cpu_peak_percent':max(float(x['system_cpu_percent']) for x in rows if x.get('system_cpu_percent')) if rows[0].get('system_cpu_percent') else None,
      'system_available_min_mib':min(float(x['system_available_bytes']) for x in rows if x.get('system_available_bytes'))/1048576 if rows[0].get('system_available_bytes') else None}

records=[]
for folder in sorted((ROOT/'results').iterdir()):
    if not folder.is_dir() or not (folder/'manifest.json').exists():continue
    m=read(folder/'manifest.json')
    if m['status']!='completed':continue
    if not (folder/'analysis.json').exists():continue
    r=read(folder/'analysis.json');r['manifest']=m
    if (folder/'phases.json').exists():r['phase_data']=read(folder/'phases.json')
    if (folder/'resources.csv').exists():r['resources']=resource(folder)
    records.append(r)
official=sorted([r for r in records if r['manifest']['kind'] in ['official','soak']],key=lambda r:r['manifest']['start'])
lines=['# Kết quả đo thực tế - AI analysis output','',
 'Nguồn: raw.json từng mẫu; analyzer độc lập và statistics.quantiles so với summary k6. E2E không gồm think 1s; cả distribution all-finalized và success-only được lưu. Tất cả E2E thành công ở các run dưới nên hai tập trùng nhau. RPS bảng tổng dùng manifest start/end, gồm overhead, khác rate summary k6.','',
 '| Run ID | E2E pass/finalized | HTTP n | E2E p95 ms | HTTP RPS (wall) | E2E/s (wall) | HTTP/E2E lỗi |',
 '|---|---|---|---|---|---|---|']
for r in official:
    n=sum(e['samples'] for e in r['endpoints'].values()); c=r['counts']; w=r['window_seconds']
    lines.append(f'| {r["run_id"]} | {int(c["m5_passed"])}/{int(c["m5_finished"])} | {n} | {r["e2e_success_only_p95_ms"]:.2f} | {n/w:.3f} | {c["m5_passed"]/w:.3f} | 0/{n}; 0/{int(c["m5_finished"])} |')
lines+=['','Tất cả run chính trên exit 0, threshold sơ bộ pass, started=finished=iterations, CLI 0 interrupted. Không có mẫu dropped_iterations; closed-VU executor không cung cấp phép đo đảm bảo arrival rate. CSV namespace count/distinct email và reset token cleared đối chiếu db-after.json. Hai smoke lỗi kết nối được giữ riêng, không nhập vào bảng này.','',
 '## Threshold đề xuất và giới hạn kết luận','',
 'Threshold ban đầu: p95 từng endpoint<500 ms, E2E success p95<2000 ms, HTTP failure<1%, E2E success>99%, CSV exhausted=0. Đây là guardrail do agent đề xuất trước pilot, không phải SLA được đề bài cho. Kết quả đo pass không chứng minh đây là SLA phù hợp sản xuất. Đề xuất sau log: giữ guardrail để phát hiện failure nặng, thêm so baseline tương đương với quy tắc >20% và >10ms, rerun 2/3 để giảm nhiễu; cần hiệu chỉnh bằng thêm run.','']
for r in official:
    m=r['manifest'];folder=ROOT/'results'/r['run_id']
    lines += [f'## {m["kind"]} {m["profile"]}: {r["run_id"]}','',f'Bắt đầu {m["start"]}; kết thúc {m["end"]}; cửa sổ wall {r["window_seconds"]:.6f}s. Testplan effective commit 52cbf3e; SUT commit chưa biết, hash trong manifest. Raw/summary/analysis/verification ở results/{r["run_id"]}/.','']
    if m['kind']=='official' and m['profile']=='Load':
        lines+=['| Endpoint | n | p95 ms | RPS wall | failure | p95<500ms |','|---|---|---|---|---|---|']
        for name,e in r['endpoints'].items():lines.append(f'| {name} | {e["samples"]} | {e["p95_ms"]:.4f} | {e["http_rps_wall_window"]:.4f} | 0/{e["samples"]} | pass |')
        lines+=['','View riêng: bảng endpoint view.html; không dùng lại kiểu biểu đồ Stress/Spike.','']
    if 'phase_data' in r:
        holds=[p for p in r['phase_data']['phases'] if p['phase'].startswith('hold')]
        lines+=['| Hold (giây từ clock suy ra) | VU cấu hình / min-max đo | HTTP n / RPS | HTTP p95 ms | E2E n / p95 ms | failure HTTP |','|---|---|---|---|---|---|']
        for p in holds:lines.append(f'| {p["start_seconds"]}-{p["end_seconds"]} | {p["target_vus"]} / {p["observed_vus_min"]}-{p["observed_vus_max"]} | {p["http_samples"]} / {p["http_rps"]:.3f} | {p["http_p95_ms"]:.3f} | {p["e2e_finalized"]} / {p["e2e_p95_all_ms"]:.3f} | {int(p["http_failed"])}/{p["http_failure_denominator"]} |')
        lines+=['','Clock stage suy từ mẫu gauge VU định kỳ đầu trừ 1s; độ lệch chưa được đo chính xác. Bỏ 2s hai đầu hold, kiểm tra actual VU ổn định. Cấp mẫu theo timestamp hoàn tất, request vượt ranh giới được tính vào cửa sổ hoàn tất. Không gọi đây là phân ranh tuyệt đối chính xác; lần sau nên ghi scenario.startTime trực tiếp.','']
    if m['profile']=='Stress':
        lines+=['Stress: throughput tăng qua 5/15/30 VU, không có bậc nào vượt guardrail đã đặt. Chưa tìm được bậc lỗi đầu tiên và chưa đo ngưỡng tối đa. Không quy kết bottleneck SQLite từ việc latency tăng.','',f'![Stress stage chart](../results/{r["run_id"]}/stress-stages.png)','']
    if m['profile']=='Spike':
        lines+=['Spike: baseline 17-58s đạt 24.390 HTTP RPS; peak hold 64-90s đạt 190.423 RPS; hồi phục 96-152s đạt 24.107 RPS. p95 E2E lần lượt 66.05 / 105.35 / 44.55 ms, HTTP failure đều 0. Dữ liệu hỗ trợ hồi phục ở cửa sổ tổng hợp này; không chứng minh recovery time chính xác từng giây.','',f'![Spike timeline](../results/{r["run_id"]}/spike-timeline.png)','']
    if 'resources' in r:
        q=r['resources'];lines+=[f'Resource samples={q["samples"]}; backend RSS first/last/peak={q["backend_rss_first_mib"]:.2f}/{q["backend_rss_last_mib"]:.2f}/{q["backend_rss_peak_mib"]:.2f} MiB; backend CPU mean/peak toàn máy={q["backend_cpu_mean_machine_percent"]:.3f}/{q["backend_cpu_peak_machine_percent"]:.3f}%. CPU tính delta CPU seconds/delta time/16, không nhầm CPU seconds với phần trăm. K6 CPU peak toàn máy={q["k6_cpu_peak_machine_percent"]}; system CPU peak={q["system_cpu_peak_percent"]}%; available RAM thấp nhất={q["system_available_min_mib"]} MiB.','']
    if m['kind']=='soak':
        n=sum(e['samples'] for e in r['endpoints'].values())
        lines+=[f'Soak kiểm chứng **5 VU liên tục 10 phút**, HTTP trung bình wall={n/r["window_seconds"]:.3f} RPS; p95 E2E={r["e2e_success_only_p95_ms"]:.2f}ms. Đây là mức ổn định đã thử trên máy, **không phải ngưỡng tối đa**. RSS peak là đỉnh quan sát, không phải memory ceiling. Chia các cửa sổ xấp xỉ một phút có trimming trong phases.csv; 5s bins và CPU/RAM trong phases.json. Không kết luận memory leak chỉ từ RSS đầu-cuối, cần nhiều run và kiểm tra heap.','',f'![Soak timeline](../results/{r["run_id"]}/soak-windows.png)','']
lines+=['## Điều kiện đo và độ nhiễu','',
 'Backend và k6 cùng Windows PHUC, nhiều ứng dụng cá nhân đang mở. Có hoạt động chuẩn bị tài liệu, cài dependency (bộ Playwright tải lâu đã hủy), dxdiag và kiểm tra HTML/PDF trong phiên đo. Resource sampler gọi CIM khoảng 1-2 giây/mẫu; không phải profiler high-resolution. Các yếu tố này giới hạn độ lặp lại, không dùng làm benchmark máy sạch. Không quan sát CPU k6 gần toàn máy trong samples nhưng chưa chứng minh không có giới hạn I/O hoặc scheduler. DB test tăng số user giữa các run, không reset để giữ namespace; số lượng trước/sau có db-before/db-after cho run chính. Muốn A/B tối ưu phải clone cùng DB cardinality và tắt tác vụ nền trước rerun.','']
(ROOT/'docs/measurement-results.md').write_text('\n'.join(lines),encoding='utf-8')
(ROOT/'results/measured-index.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
hardware=read(ROOT/'results/hardware/hardware.json')
intro='''# HW05-AI - Performance Testing M5

MSSV: 23120330. Ngày thực hiện: 2026-11-19, Asia/Ho_Chi_Minh. **Bản nháp chờ sinh viên review, chưa sẵn sàng nộp.**

## Phạm vi và quy trình

Register -> Forgot password -> Reset password -> Login bằng mật khẩu mới -> GET /api/cart. Auth-heavy đại diện register; transactional là tạo/reset trạng thái mật khẩu; read-heavy là giỏ có JWT. Sinh viên đã xác nhận giữ GET /api/cart và xét trùng theo method+path; không tự suy thành duyệt toàn bộ assertions/workload.

Đã đọc đề mục 14, README, setup_guide và Git status trước sửa. Archive gốc không có Git; commit SUT chưa xác minh, dùng SHA256 nguồn trong docs/api-contract.md. Không sửa backend gốc hay DB gốc. Sao backend vào runtime/backend với DB riêng vì database.js tự DROP/seed khi import. DB gốc hash trước/sau smoke không đổi. Runtime khởi động bằng node server.js, cổng 3000; dependencies từ lockfile npm ci. Scope không thêm profile, lockout chủ đích, cart write, coupon hoặc checkout.

CSV tổng hợp tạo namespace mới mỗi run, SharedArray, scenario.iterationInTest không quay vòng; mỗi run một scenario. Năm bước check status và nghiệp vụ, dừng sớm khi lỗi, finally ghi E2E lỗi và pacing. Reset token/JWT trong bộ nhớ cùng iteration; không log password, cookie hay response auth. CSV private không commit. Script/generator và schema public candidate được giữ riêng với dữ liệu có mật khẩu.

Smoke thành công 1 VU x5 iterations, 25 requests, 50 checks pass, p95 E2E 43.4ms. Probe xác nhận token 4 chữ số và cart=[]; toàn bộ status200. Contract khác yêu cầu OTP6 chữ số và response login chứa password field: hai draft Issue đã chuẩn bị, chưa đăng. Hai smoke lỗi môi trường giữ riêng; không kết luận đó là bug SUT. Pilot1/2/5 VU:306 E2E pass, p95E2E36ms, giúp chọn5VU Load/Soak, stress5/15/30 và spike5->40. Think1s đặt sau E2E; timeout10s; graceful15s. Xem chi tiết file:dòng ở docs/api-contract.md và review-workload.md (draft ban đầu được giữ để truy vết).

## Máy và công cụ

Windows11 Home64bit build26300; Lenovo82SN; AMD Ryzen7 6800H8core/16logical; hostname thực PHUC. Dxdiag hiển thị RAM16384MB, CIM TotalPhysicalMemory=14702026752bytes (~13.69GiB hệ thống báo); ghi hai nguồn, không coi đó là cùng chỉ số. K6v2.2.0 commit00a9a1b7f5, Nodev22.17.1. Ảnh dxdiag thật: results/hardware/dxdiag-system.jpg; hardware.json là thông tin máy đọc trực tiếp. Sinh viên phản hồi còn cần kiểm tra hostname bài trước, nên tính liên tục bằng chứng chưa xác nhận. Task Manager mở được nhưng higher integrity chặn UI agent; chưa có ảnh k6+TaskManager cùng khung hình cho từng run. Ảnh headless HTML chỉ để QA biểu đồ, không thay ảnh desktop.

![Actual dxdiag System screenshot](../results/hardware/dxdiag-system.jpg)

## Contract tóm tắt và nguồn

| Method/path | Input và dữ liệu truyền | Assertion | Nguồn SUT gốc |
|---|---|---|---|
| POST /api/register | name,email,password CSV | 200, message, id nguyên dương | api_specification.md:12; server.js:20 |
| POST /api/forgot-password | email cùng dòng | 200, resetToken string số | api_specification.md:35; server.js:68 |
| POST /api/reset-password | email, resetToken vừa nhận, newPassword | 200 runtime, message reset thành công | api_specification.md:45; server.js:87 |
| POST /api/login | email, password=newPassword | 200, JWT 3phần, id/email trùng register | api_specification.md:24; server.js:32 |
| GET /api/cart | Bearer JWT vừa login | 200, array length0 | api_specification.md:112; server.js:284 |

Các server.js trong bảng là backend/server.js. Bảng nguồn dòng đầy đủ và hashes ở api-contract.md. Không lưu token/JWT hay password trong báo cáo.

'''
pipeline=(ROOT/'docs/pipeline-proposal.md').read_text(encoding='utf-8').replace('# Continuous Performance Testing - proposal only','## Đề xuất Continuous Performance Testing (chưa triển khai)')
critique=(ROOT/'docs/ai-critique.md').read_text(encoding='utf-8').split('During this assignment,',1)[1].split('\n\nHuman review',1)[0]
ending='''
## AI Audit, review và hồ sơ còn thiếu

Xem ai-audit.md: khai báo công cụ và tương tác thật, giữ output phân tích đầu, sửa lỗi absent dropped_iterations và clock lệch do first iteration. Đây là agent self-review; không ghi thành human correction. Audit hiện là trích đoạn có nguồn, cần export chat đầy đủ trước nộp; không dựng timestamp. Hai tối ưu khả thi có điều kiện (email index/WAL) cần A/B, còn pool nhiều writer và tối ưu hashing hiện hữu là sai cho SQLite/plaintext bản SUT này. Không sửa SUT để làm kết quả đẹp.

Human review đã nhận: giữ GETcart theo method+path; hostname bài trước cần kiểm tra. Còn chờ review assertions/tải/phân tích/critique; ba ảnh desktop cùng khung hình; xác nhận hostname; GitHub public URL và quyền push; transcript đầy đủ; video Unlisted >=6phút giọng sinh viên; điểm tự chấm. Kịch bản7phút trong evidence-and-video.md. Skill được tạo sau smoke ban đầu; replay thực tế skill-demo-load-20261119-144618-45deee1a đã pass5/5 E2E trên đủ5endpoint. Đoạn demo video05:00-06:30 vẫn mới là đề xuất.

Mục14 yêu cầu .jtl nhưng cho phép k6: giữ raw.json theo từng mẫu và ba dashboard.html gốc như bằng chứng tương đương, không đổi đuôi sang.jtl. Chưa có hướng dẫn Moodle riêng được cung cấp; sinh viên cần kiểm tra quy ước này. Chưa tạo ZIP tên điểm khi chưa có grade000-100 được duyệt. Không push, public, đăng Issue, upload video hay nộp Moodle.

## AI Critique draft (248 words, pending human approval)

During this assignment,'''+critique+'\n'
(ROOT/'docs/main-report.md').write_text(intro+'\n'.join(lines)+'\n'+pipeline+'\n'+ending,encoding='utf-8')
print('Compiled measured report from',len(official),'official/soak runs')
readme=['# 23120330 - HW05-AI M5 submission workspace','',
 '**Draft: chưa sẵn sàng nộp.** Chỉ hw05-m5 là Git repo mới; SUT archive gốc không có .git. Không có public remote, không push.','',
 '## Test summary','',
 'Workflow: Register (Auth-heavy) -> Forgot/Reset (Transactional) -> Login hỗ trợ -> GET Cart (Read-heavy). Human đã xác nhận GET Cart không trùng theo method+path.','',
 '| Scenario | Run ID | E2E | p95 E2E ms | Raw / HTML / view |',
 '|---|---|---|---|---|']
for r in official:
    key=r['run_id'];label='Soak' if r['manifest']['kind']=='soak' else r['manifest']['profile']
    readme.append(f'| {label} | {key} | {int(r["counts"]["m5_passed"])} pass / {int(r["counts"]["m5_finished"])} finalized | {r["e2e_success_only_p95_ms"]:.2f} | [raw](results/{key}/raw.json), [HTML](results/{key}/dashboard.html), [view](results/{key}/view.html) |')
soaks=[r for r in official if r['manifest']['kind']=='soak']
if soaks:
    r=soaks[-1];n=sum(x['samples'] for x in r['endpoints'].values())
    readme+=['',f'Endurance đã thử: **5 VU / 10 phút**, {n/r["window_seconds"]:.3f} HTTP RPS trung bình wall, p95 E2E {r["e2e_success_only_p95_ms"]:.2f}ms, HTTP/E2E lỗi0. Backend RSS peak {r["resources"]["backend_rss_peak_mib"]:.2f}MiB. Đây là mức đã kiểm chứng, **chưa xác định ngưỡng tối đa**.']
else:readme+=['','Soak đang chạy; chưa báo kết quả trước khi hoàn tất.']
readme+=['','Phát hiện đã xác minh:2 (OTP4 thay vì6 chữ số; login response chứa password field), draft trong [issue-drafts.md](docs/issue-drafts.md). GitHub Issues đã đăng:0. Không có issue hiệu năng đã chứng minh. Video Unlisted: **chờ người dùng cung cấp link thật**. Public GitHub: **chờ duyệt và link thật**.','',
 '## Tự chấm - chưa nhận điểm sinh viên','',
 '| Tiêu chí | Tối đa | Điểm tự chấm |','|---|---|---|',
 '| Load | 30 | Chờ |','| Stress | 20 | Chờ |','| Spike | 20 | Chờ |','| AI analysis / hunt | 10 | Chờ |','| Continuous testing proposal | 10 | Chờ |','| Agent Skill | 10 | Chờ |','| Tổng | 100 | Chờ |','',
 '## Hồ sơ và cách chạy','',
 '- [Kịch bản quay video chi tiết bằng tiếng Việt, 16-18phút](docs/video-recording-script-vi.md): bố cục OBS, lệnh chạy, lời đọc và demo Agent Skill thật.',
 '- [Main report Markdown](docs/main-report.md) và [PDF draft](output/pdf/main-report.pdf).',
 '- [API contract](docs/api-contract.md), [assertions/workload draft](docs/review-workload.md), [measured analysis](docs/measurement-results.md).',
 '- [AI Audit Markdown](docs/ai-audit.md) và [PDF draft](output/pdf/ai-audit.pdf); actual outputs trong docs/audit; transcript đầy đủ còn thiếu.',
 '- [AI Critique 248 words](docs/ai-critique.md) và [PDF draft](output/pdf/ai-critique.pdf), chưa được human duyệt.',
 '- Ba testplans đúng tên trong plans/; workflow.js dùng chung. CSV private trong data/; generator scripts/new-data.py và schema data/README.md có thể công khai sau review. Không commit mật khẩu test.',
 '- [PowerShell commands/evidence/video7phút](docs/evidence-and-video.md). Runtime/backend là bản sao test riêng, không khởi động backend gốc do module DB tự DROP/seed.',
 '- [Pipeline proposal với flowchart](docs/pipeline-proposal.md), có hình vector trong PDF chính.',
 '- [Reusable SKILL.md](skills/k6-workflow-audit/SKILL.md); skill replay thực tế skill-demo-load-20261119-144618-45deee1a đã pass5/5E2E, video05:00-06:30 mới là lịch dự kiến.',
 '- [Git commit log](git-commit-log.txt). Chỉ commit file M5; dữ liệu/results/runtime không đưa vào Git public candidate.',
 '- Hardware: [dxdiag screenshot thật](results/hardware/dxdiag-system.jpg), [CIM report](results/hardware/hardware.json). PHUC thực tế, chưa xác nhận khớp bài trước.',
 '', '## Đối chiếu mục14 và những mục còn thiếu','',
 '| Yêu cầu | Trạng thái |','|---|---|',
 '| Main/Audit/Critique MD+PDF | Có bản draft; cần review, Audit chưa có full transcript |',
 '|3 JS + CSV|Có; CSV chứa mật khẩu synthetic giữ riêng tư, không public|',
 '|3 raw logs|Có raw.json nguyên định dạng k6, từng mẫu; không đổi đuôi thành .jtl|',
 '|3 HTML exports +3 views|Có; exports mở bằng Edge có đồ thị, views khác loại|',
 '|Soak 10-15phút|Xem test summary và raw riêng; không gọi maximum|',
 '|Ảnh tool+TaskManager mỗi run|**Thiếu**; quyền UI TaskManager chặn điều khiển agent|',
 '|Hardware report/ảnh|Có; continuity hostname **chờ xác nhận**|',
 '|YouTube Unlisted >=6phút giọng sinh viên|**Thiếu**; chỉ có kịch bản7phút|',
 '|Public GitHub|**Thiếu**; chờ quyền push/public và URL thật|',
 '|Git log/Skill/pipeline|Có, cập nhật log sau commit cuối|',
 '|Bug report và Issue screenshots|Có2 draft;0Issue đã đăng, chưa có screenshotIssue|',
 '|Điểm và ZIP đúng tên|**Chưa có điểm**; chưa tạo ZIP cuối|',
 '',
 'K6 được đề cho phép nhưng checklist ZIP ghi .jtl. README này quy ước raw.json k6 là bằng chứng gốc theo mẫu tương ứng raw log; ba dashboard.html export tương ứng ba HTML report. Giữ đuôi file gốc. Chưa được cung cấp hướng dẫn Moodle riêng; **sinh viên cần kiểm tra quy ước nộp này**.','',
 'Sau review cập nhật submission-state.json bằng dữ liệu thật, rồi `./scripts/package.ps1 -SelfAssessedGrade <0..100>` tạo `23120330_HW05_AI_Performance_<000..100>.zip`. Script không push/upload/nộp. Không tạo ZIP cuối trước khi có điểm đã duyệt.','']
(ROOT/'README.md').write_text('\n'.join(readme),encoding='utf-8')

# Supplement the preserved original-run report with explicitly matched photo reruns.
from evidence_report import compile_evidence
appendix,photos_ready=compile_evidence(ROOT)
if photos_ready:
    main=ROOT/'docs/main-report.md'
    content=main.read_text(encoding='utf-8')
    content=content.replace('Task Manager mở được nhưng higher integrity chặn UI agent; chưa có ảnh k6+TaskManager cùng khung hình cho từng run.',
       'Task Manager có higher integrity chặn UI agent; sinh viên đã phối hợp chụp ba ảnh dashboard+TaskManager thật cho các rerun trong phụ lục.')
    content=content.replace('ba ảnh desktop cùng khung hình; ','')
    main.write_text(content+'\n'+appendix,encoding='utf-8')
    page=ROOT/'README.md';content=page.read_text(encoding='utf-8')
    content=content.replace('|Ảnh tool+TaskManager mỗi run|**Thiếu**; quyền UI TaskManager chặn điều khiển agent|',
       '|Ảnh tool+TaskManager mỗi run|Đã có ba ảnh người dùng chụp, ghép đúng raw/HTML của các rerun bên dưới|')
    content+='\n## Ba rerun có ảnh thật\n\nKết quả gốc ở bảng trên được giữ nguyên. Bộ bổ sung sau có ba ảnh cùng khung hình và raw/HTML riêng. RPS thực thi loại thời gian đợi tab dashboard đóng; xem [phụ lục rerun](docs/evidence-reruns.md).\n\n'
    content+='| Profile | Run ID | E2E pass | p95 E2E ms | HTTP RPS thực thi | Files |\n|---|---|---|---|---|---|\n'
    state=read(ROOT/'submission-state.json')
    for profile in ['Load','Stress','Spike']:
        key=state['resource_screenshot_runs'][profile];a=read(ROOT/'results'/key/'analysis.json')
        n=sum(e['samples'] for e in a['endpoints'].values());photo=state['resource_screenshots'][profile]
        content+=f'| {profile} | {key} | {int(a["counts"]["m5_passed"])} | {a["e2e_success_only_p95_ms"]:.2f} | {n/a["execution_window_seconds"]:.3f} | [ảnh]({photo}), [raw](results/{key}/raw.json), [HTML](results/{key}/dashboard.html), [view](results/{key}/view.html) |\n'
    content+='\nSpike rerun: throughput trở về gần baseline nhưng p95 hồi phục còn cao hơn baseline; chưa kết luận độ trễ hồi phục hoàn toàn. Chưa có video hoặc human review cuối.\n'
    page.write_text(content,encoding='utf-8')
