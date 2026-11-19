"""Compile only completed reruns that match actual user-supplied resource photos."""
import json

def compile_evidence(root):
    def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
    state=read(root/'submission-state.json')
    chosen=[]
    for profile in ['Load','Stress','Spike']:
        run_id=state.get('resource_screenshot_runs',{}).get(profile)
        photo=state.get('resource_screenshots',{}).get(profile)
        if not run_id or not photo or not (root/photo).exists():continue
        folder=root/'results'/run_id
        m=read(folder/'manifest.json')
        if m['status']!='completed' or not (folder/'verification.json').exists():continue
        a=read(folder/'analysis.json');p=read(folder/'phases.json');v=read(folder/'verification.json')
        assert m['profile']==profile and m['kind']=='rerun' and v['all_p95_match']
        chosen.append((profile,run_id,photo,m,a,p))
    if len(chosen)!=3:return '',False
    lines=['# Phụ lục: ba rerun có ảnh Windows thật','',
      'Ngày 2026-11-19, Asia/Ho_Chi_Minh. Ba ảnh do sinh viên chụp và gửi trong chat; lưu nguyên byte, SHA256 và nguồn trong screenshot-evidence.json của từng run. Mỗi ảnh ghép cặp với raw/summary/HTML của chính lượt chụp, không gắn vào lượt gốc. Các run gốc và soak vẫn được giữ nguyên để truy vết.','',
      'Backend mới PID32692 tại runtime/evidence-20261119-1511/backend, dùng DB riêng mới thay vì reset DB test cũ. Nguồn server/database không sửa; NODE_PATH dùng dependencies đã cài từ lockfile. Workflow và tải giữ nguyên, bổ sung metric m5_scenario_start_epoch_ms từ scenario.startTime. Manifest có test-plan commit và runtime/workflow hashes.','',
      '| Profile / run ID | E2E pass / finalized | HTTP n | E2E p95 ms | HTTP RPS thực thi | Exit |',
      '|---|---|---|---|---|---|']
    for profile,run,photo,m,a,p in chosen:
        n=sum(e['samples'] for e in a['endpoints'].values())
        failures=sum(e['http_failure_numerator'] for e in a['endpoints'].values())
        assert failures==0 and a['e2e_failure_rate_finalized']==0
        lines.append(f'| {profile}: {run} | {int(a["counts"]["m5_passed"])}/{int(a["counts"]["m5_finished"])} | {n} | {a["e2e_success_only_p95_ms"]:.2f} | {n/a["execution_window_seconds"]:.3f} | {m["exit_code"]} |')
    lines+=['','Mọi rerun trên có HTTP/E2E failure0, started=finished=iterations; không có mẫu dropped_iterations vì executor closed-VU. P95 toàn finalized và success-only giống nhau ở đây vì toàn bộ E2E pass, không tính think1s. Phép tính độc lập statistics.quantiles khớp summary k6 trong1e-7ms.','',
      'RPS thực thi = HTTP request count / summary.state.testRunDurationMs. Thời gian này gồm ramp/hold/drain của workload, loại thời gian đợi tab dashboard đóng. Wall interval start/end vẫn giữ riêng trong analysis.json; không dùng để đánh giá tốc độ khi có chờ UI. Clock stage trực tiếp từ scenario.startTime; các hold vẫn trim2s mỗi đầu, cấp mẫu theo timestamp hoàn tất. Resources dùng các sample nằm trong cửa sổ thực thi, loại phần sampler tiếp tục khi chờ dashboard.','']
    for profile,run,photo,m,a,p in chosen:
        folder=root/'results'/run;proof=read(folder/'screenshot-evidence.json')
        lines += [f'## Rerun {profile}: {run}','',
          f'Manifest start={m["start"]}, end={m["end"]}; execution={a["execution_window_seconds"]:.7f}s, wall={a["window_seconds"]:.7f}s. Test-plan commit {m["test_plan_commit"][:7]}. Endpoints và correlation không đổi.','',
          f'Nguồn: results/{run}/raw.json, summary.json, analysis.json, verification.json, phases.json, resources.csv, dashboard.html và view.html.','',
          '| Endpoint | n | HTTP p95 ms | HTTP RPS thực thi | HTTP failure | p95<500ms |',
          '|---|---|---|---|---|---|']
        for name,e in a['endpoints'].items():
            lines.append(f'| {name} | {e["samples"]} | {e["p95_ms"]:.4f} | {e["http_rps_execution_window"]:.4f} | {int(e["http_failure_numerator"])}/{e["http_failure_denominator"]} | {"pass" if e["draft_p95_lt_500ms"] else "fail"} |')
        lines+=['','| Hold (s từ scenario.startTime) | Target VU / min-max đo | HTTP RPS | HTTP p95 ms | E2E p95 ms | HTTP n / fail |',
          '|---|---|---|---|---|---|']
        holds=[w for w in p['phases'] if w['phase'].startswith('hold')]
        for w in holds:
            lines.append(f'| {w["start_seconds"]}-{w["end_seconds"]} | {w["target_vus"]} / {w["observed_vus_min"]}-{w["observed_vus_max"]} | {w["http_rps"]:.3f} | {w["http_p95_ms"]:.3f} | {w["e2e_p95_all_ms"]:.3f} | {w["http_samples"]} / {int(w["http_failed"])} |')
        resource=p['resources']
        if resource:
            cpus=[r['cpu_percent_machine'] for r in resource if r['cpu_percent_machine'] is not None]
            lines+=['',f'Resource trong execution window: {len(resource)} mẫu, backend RSS peak={max(r["rss_mib"] for r in resource):.2f}MiB, CPU peak toàn máy={max(cpus):.3f}% (deltaCPU/deltaTime/16 logical processors). Raw sampler tiếp tục trong thời gian đợi tab được giữ nguyên; phần ngoài cửa sổ được loại khỏi thống kê này.','']
        if profile=='Stress':
            lines+=['Throughput tăng qua5/15/30VU; p95 không tăng đơn điệu. Không bậc nào vượt guardrail đặt trước. Chưa có bằng chứng ngưỡng tối đa hoặc nguyên nhân bottleneck.','',f'![Measured rerun Stress stage view](../results/{run}/stress-stages.png)','']
        if profile=='Spike':
            baseline,peak,recovery=holds
            lines += [f'Spike baseline/peak/recovery HTTP RPS={baseline["http_rps"]:.3f}/{peak["http_rps"]:.3f}/{recovery["http_rps"]:.3f}; E2E p95={baseline["e2e_p95_all_ms"]:.2f}/{peak["e2e_p95_all_ms"]:.2f}/{recovery["e2e_p95_all_ms"]:.2f}ms. Throughput đã trở về gần baseline, nhưng p95 E2E hồi phục còn cao hơn baseline. **Chưa chứng minh độ trễ đã hồi phục hoàn toàn.** Tất cả vẫn dưới guardrail, không đồng nghĩa đã trở về baseline. Cần lặp lại trong điều kiện tương đương trước kết luận regression hoặc nguyên nhân.','',f'![Measured rerun Spike timeline](../results/{run}/spike-timeline.png)','']
        obs=proof['visual_observations']
        lines += [f'Ảnh do sinh viên cung cấp: PID{obs["backend_pid"]}, CPU hiển thị{obs["task_manager_cpu_display"]}, Memory hiển thị{obs["task_manager_memory_display"]}; card HTTP {obs["http_request_rate_display"]} là snapshot. Timestamp chụp chính xác chưa được cung cấp; mốc trên chart và pha tải nhìn thấy được đối chiếu với run. Không đồng nhất cột Memory của TaskManager với RSS sampler.','',f'![User supplied {profile} dashboard and Task Manager](../{photo})','']
    lines += ['## Hạn chế và trạng thái hồ sơ','',
      'Một lượt Load trước khi thu ảnh hợp lệ (rerun-load-20261119-162216-d7ab78da) đã chạy hết689iteration nhưng controller bị dừng trong khi đợi dashboard. Không có summary, nên không nhận là completed hoặc dùng làm kết quả chính. Raw và manifest cũ giữ nguyên; controller-stop-note.json ghi hạn chế.','',
      'Stress sau workload còn kết nối từ tab localhost trong in-app browser dù Chrome đã đóng. Agent dùng browser API đọc đúng trang k6 và đóng duy nhất tab5665, không thao tác UI ChatGPT hay vượt quyền TaskManager. Sau đó Stress xuất summary exit0. Spike dùng dashboard5666 và chỉ bắt đầu sau khi workload Stress đã kết thúc; sampler Stress vẫn chạy lúc đợi tab. Có thêm overhead sampler trong Spike, cần ghi nhận khi so sánh.','',
      'Đã có ba ảnh cùng khung hình thật. Chưa có video thuyết minh tiếng Việt, public GitHub/YouTube URL, full chat export, hostname continuity, điểm tự chấm và human review cuối. Không suy việc người dùng gửi ảnh thành duyệt assertions/critique/điểm. Task3 vẫn là proposal đúng yêu cầu; không tự triển khai CI. Không thay mức soak5VU thành maximum.','']
    appendix='\n'.join(lines)
    (root/'docs/evidence-reruns.md').write_text(appendix,encoding='utf-8')
    return appendix,True
