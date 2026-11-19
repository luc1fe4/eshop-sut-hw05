# Phụ lục: ba rerun có ảnh Windows thật

Ngày 2026-11-19, Asia/Ho_Chi_Minh. Ba ảnh do sinh viên chụp và gửi trong chat; lưu nguyên byte, SHA256 và nguồn trong screenshot-evidence.json của từng run. Mỗi ảnh ghép cặp với raw/summary/HTML của chính lượt chụp, không gắn vào lượt gốc. Các run gốc và soak vẫn được giữ nguyên để truy vết.

Backend mới PID32692 tại runtime/evidence-20261119-1511/backend, dùng DB riêng mới thay vì reset DB test cũ. Nguồn server/database không sửa; NODE_PATH dùng dependencies đã cài từ lockfile. Workflow và tải giữ nguyên, bổ sung metric m5_scenario_start_epoch_ms từ scenario.startTime. Manifest có test-plan commit và runtime/workflow hashes.

| Profile / run ID | E2E pass / finalized | HTTP n | E2E p95 ms | HTTP RPS thực thi | Exit |
|---|---|---|---|---|---|
| Load: rerun-load-20261119-163449-813f2702 | 691/691 | 3455 | 34.00 | 20.875 | 0 |
| Stress: rerun-stress-20261119-164026-b02a7bbd | 2890/2890 | 14450 | 69.00 | 74.065 | 0 |
| Spike: rerun-spike-20261119-164621-7f96e5f6 | 1830/1830 | 9150 | 68.00 | 55.694 | 0 |

Mọi rerun trên có HTTP/E2E failure0, started=finished=iterations; không có mẫu dropped_iterations vì executor closed-VU. P95 toàn finalized và success-only giống nhau ở đây vì toàn bộ E2E pass, không tính think1s. Phép tính độc lập statistics.quantiles khớp summary k6 trong1e-7ms.

RPS thực thi = HTTP request count / summary.state.testRunDurationMs. Thời gian này gồm ramp/hold/drain của workload, loại thời gian đợi tab dashboard đóng. Wall interval start/end vẫn giữ riêng trong analysis.json; không dùng để đánh giá tốc độ khi có chờ UI. Clock stage trực tiếp từ scenario.startTime; các hold vẫn trim2s mỗi đầu, cấp mẫu theo timestamp hoàn tất. Resources dùng các sample nằm trong cửa sổ thực thi, loại phần sampler tiếp tục khi chờ dashboard.

## Rerun Load: rerun-load-20261119-163449-813f2702

Manifest start=2026-11-19T16:34:50.0951818+07:00, end=2026-11-19T16:39:10.5786736+07:00; execution=165.5063627s, wall=260.4834919s. Test-plan commit 2362af2. Endpoints và correlation không đổi.

Nguồn: results/rerun-load-20261119-163449-813f2702/raw.json, summary.json, analysis.json, verification.json, phases.json, resources.csv, dashboard.html và view.html.

| Endpoint | n | HTTP p95 ms | HTTP RPS thực thi | HTTP failure | p95<500ms |
|---|---|---|---|---|---|
| register | 691 | 10.6319 | 4.1751 | 0/691 | pass |
| forgot | 691 | 10.1437 | 4.1751 | 0/691 | pass |
| reset | 691 | 8.9762 | 4.1751 | 0/691 | pass |
| login | 691 | 6.4244 | 4.1751 | 0/691 | pass |
| cart | 691 | 2.4490 | 4.1751 | 0/691 | pass |

| Hold (s từ scenario.startTime) | Target VU / min-max đo | HTTP RPS | HTTP p95 ms | E2E p95 ms | HTTP n / fail |
|---|---|---|---|---|---|
| 32-148 | 5 / 5-5 | 24.569 | 8.973 | 34.000 | 2850 / 0 |

Resource trong execution window: 104 mẫu, backend RSS peak=88.54MiB, CPU peak toàn máy=0.794% (deltaCPU/deltaTime/16 logical processors). Raw sampler tiếp tục trong thời gian đợi tab được giữ nguyên; phần ngoài cửa sổ được loại khỏi thống kê này.

Ảnh do sinh viên cung cấp: PID32692, CPU hiển thị00, Memory hiển thị57,228 K; card HTTP 25/s là snapshot. Timestamp chụp chính xác chưa được cung cấp; mốc trên chart và pha tải nhìn thấy được đối chiếu với run. Không đồng nhất cột Memory của TaskManager với RSS sampler.

![User supplied Load dashboard and Task Manager](../results/rerun-load-20261119-163449-813f2702/load-k6-taskmanager.png)

## Rerun Stress: rerun-stress-20261119-164026-b02a7bbd

Manifest start=2026-11-19T16:40:26.5726194+07:00, end=2026-11-19T16:50:45.5521080+07:00; execution=195.0996785s, wall=618.9794891s. Test-plan commit 8dfae37. Endpoints và correlation không đổi.

Nguồn: results/rerun-stress-20261119-164026-b02a7bbd/raw.json, summary.json, analysis.json, verification.json, phases.json, resources.csv, dashboard.html và view.html.

| Endpoint | n | HTTP p95 ms | HTTP RPS thực thi | HTTP failure | p95<500ms |
|---|---|---|---|---|---|
| register | 2890 | 17.5242 | 14.8129 | 0/2890 | pass |
| forgot | 2890 | 24.0909 | 14.8129 | 0/2890 | pass |
| reset | 2890 | 18.4183 | 14.8129 | 0/2890 | pass |
| login | 2890 | 15.8214 | 14.8129 | 0/2890 | pass |
| cart | 2890 | 5.8240 | 14.8129 | 0/2890 | pass |

| Hold (s từ scenario.startTime) | Target VU / min-max đo | HTTP RPS | HTTP p95 ms | E2E p95 ms | HTTP n / fail |
|---|---|---|---|---|---|
| 17-58 | 5 / 5-5 | 24.390 | 18.017 | 73.100 | 1000 / 0 |
| 77-118 | 15 / 15-15 | 72.415 | 15.382 | 61.000 | 2969 / 0 |
| 137-178 | 30 / 30-30 | 144.073 | 20.011 | 69.000 | 5907 / 0 |

Resource trong execution window: 123 mẫu, backend RSS peak=90.03MiB, CPU peak toàn máy=2.406% (deltaCPU/deltaTime/16 logical processors). Raw sampler tiếp tục trong thời gian đợi tab được giữ nguyên; phần ngoài cửa sổ được loại khỏi thống kê này.

Throughput tăng qua5/15/30VU; p95 không tăng đơn điệu. Không bậc nào vượt guardrail đặt trước. Chưa có bằng chứng ngưỡng tối đa hoặc nguyên nhân bottleneck.

![Measured rerun Stress stage view](../results/rerun-stress-20261119-164026-b02a7bbd/stress-stages.png)

Ảnh do sinh viên cung cấp: PID32692, CPU hiển thị01, Memory hiển thị53,060 K; card HTTP 73/s là snapshot. Timestamp chụp chính xác chưa được cung cấp; mốc trên chart và pha tải nhìn thấy được đối chiếu với run. Không đồng nhất cột Memory của TaskManager với RSS sampler.

![User supplied Stress dashboard and Task Manager](../results/rerun-stress-20261119-164026-b02a7bbd/stress-k6-taskmanager.png)

## Rerun Spike: rerun-spike-20261119-164621-7f96e5f6

Manifest start=2026-11-19T16:46:21.9610949+07:00, end=2026-11-19T16:49:08.0540753+07:00; execution=164.2908387s, wall=166.0929811s. Test-plan commit 3d9346e. Endpoints và correlation không đổi.

Nguồn: results/rerun-spike-20261119-164621-7f96e5f6/raw.json, summary.json, analysis.json, verification.json, phases.json, resources.csv, dashboard.html và view.html.

| Endpoint | n | HTTP p95 ms | HTTP RPS thực thi | HTTP failure | p95<500ms |
|---|---|---|---|---|---|
| register | 1830 | 16.0201 | 11.1388 | 0/1830 | pass |
| forgot | 1830 | 23.1229 | 11.1388 | 0/1830 | pass |
| reset | 1830 | 16.9132 | 11.1388 | 0/1830 | pass |
| login | 1830 | 14.4921 | 11.1388 | 0/1830 | pass |
| cart | 1830 | 5.8168 | 11.1388 | 0/1830 | pass |

| Hold (s từ scenario.startTime) | Target VU / min-max đo | HTTP RPS | HTTP p95 ms | E2E p95 ms | HTTP n / fail |
|---|---|---|---|---|---|
| 17-58 | 5 / 5-5 | 24.390 | 12.144 | 48.050 | 1000 / 0 |
| 64-90 | 40 / 40-40 | 193.077 | 18.283 | 69.800 | 5020 / 0 |
| 96-152 | 5 / 5-5 | 23.929 | 20.580 | 77.000 | 1340 / 0 |

Resource trong execution window: 104 mẫu, backend RSS peak=88.51MiB, CPU peak toàn máy=4.118% (deltaCPU/deltaTime/16 logical processors). Raw sampler tiếp tục trong thời gian đợi tab được giữ nguyên; phần ngoài cửa sổ được loại khỏi thống kê này.

Spike baseline/peak/recovery HTTP RPS=24.390/193.077/23.929; E2E p95=48.05/69.80/77.00ms. Throughput đã trở về gần baseline, nhưng p95 E2E hồi phục còn cao hơn baseline. **Chưa chứng minh độ trễ đã hồi phục hoàn toàn.** Tất cả vẫn dưới guardrail, không đồng nghĩa đã trở về baseline. Cần lặp lại trong điều kiện tương đương trước kết luận regression hoặc nguyên nhân.

![Measured rerun Spike timeline](../results/rerun-spike-20261119-164621-7f96e5f6/spike-timeline.png)

Ảnh do sinh viên cung cấp: PID32692, CPU hiển thị03, Memory hiển thị61,564 K; card HTTP 207/s là snapshot. Timestamp chụp chính xác chưa được cung cấp; mốc trên chart và pha tải nhìn thấy được đối chiếu với run. Không đồng nhất cột Memory của TaskManager với RSS sampler.

![User supplied Spike dashboard and Task Manager](../results/rerun-spike-20261119-164621-7f96e5f6/spike-k6-taskmanager.png)

## Hạn chế và trạng thái hồ sơ

Một lượt Load trước khi thu ảnh hợp lệ (rerun-load-20261119-162216-d7ab78da) đã chạy hết689iteration nhưng controller bị dừng trong khi đợi dashboard. Không có summary, nên không nhận là completed hoặc dùng làm kết quả chính. Raw và manifest cũ giữ nguyên; controller-stop-note.json ghi hạn chế.

Stress sau workload còn kết nối từ tab localhost trong in-app browser dù Chrome đã đóng. Agent dùng browser API đọc đúng trang k6 và đóng duy nhất tab5665, không thao tác UI ChatGPT hay vượt quyền TaskManager. Sau đó Stress xuất summary exit0. Spike dùng dashboard5666 và chỉ bắt đầu sau khi workload Stress đã kết thúc; sampler Stress vẫn chạy lúc đợi tab. Có thêm overhead sampler trong Spike, cần ghi nhận khi so sánh.

Đã có ba ảnh cùng khung hình thật. Chưa có video thuyết minh tiếng Việt, public GitHub/YouTube URL, full chat export, hostname continuity, điểm tự chấm và human review cuối. Không suy việc người dùng gửi ảnh thành duyệt assertions/critique/điểm. Task3 vẫn là proposal đúng yêu cầu; không tự triển khai CI. Không thay mức soak5VU thành maximum.
