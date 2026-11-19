# Evidence checklist and Vietnamese recording script

Kịch bản quay chi tiết hiện tại: [video-recording-script-vi.md](video-recording-script-vi.md), khoảng16-18phút, gồm thao tác, lời đọc và lệnh PowerShell. Bản7phút bên dưới là draft trước, giữ để truy vết. Chapter demo skill chính thức chỉ cập nhật sau khi có video thật.

Đã chạy Load/Stress/Spike chính thức, soak5VU/10phút đã hoàn tất; xem measurement-results.md và manifest để biết trạng thái mới nhất. Đã có ảnh dxdiag thật và ảnh HTML QA headless, đã có ba ảnh k6+TaskManager của các rerun do người dùng chụp; **chưa có video**. Máy đo Windows hostname Phuc; sinh viên phản hồi còn cần kiểm tra khớp bài trước. Không sử dụng screenshot giả hay môi trường khác để thay bằng chứng Windows.

## Chạy lại bằng PowerShell

Từ thư mục SUT gốc, backend test riêng đang chạy theo api-contract.md:

```powershell
# Smoke; mỗi lệnh tạo CSV/run_id và thư mục results riêng
& ./hw05-m5/scripts/run.ps1 -Profile Load -Kind smoke -Rows 10
# Chỉ chạy chính thức sau review + pilot; đây là lệnh đã chuẩn bị
& ./hw05-m5/scripts/run.ps1 -Profile Load -Kind pilot -Rows 20000 -StagesJson '[{"duration":"10s","target":1},{"duration":"30s","target":1},{"duration":"10s","target":2},{"duration":"30s","target":2},{"duration":"10s","target":5},{"duration":"30s","target":5},{"duration":"10s","target":0}]' -BackendPid <PID>
& ./hw05-m5/scripts/run.ps1 -Profile Load -Kind official -BackendPid <PID>
& ./hw05-m5/scripts/run.ps1 -Profile Stress -Kind official -BackendPid <PID>
& ./hw05-m5/scripts/run.ps1 -Profile Spike -Kind official -BackendPid <PID>
& ./hw05-m5/scripts/run.ps1 -Profile Load -Kind soak -Vus 2 -Duration 10m -BackendPid <PID>
python ./hw05-m5/scripts/analyze.py ./hw05-m5/results/<run-id>
```

Thay <PID> bằng PID node chạy runtime/backend/server.js, không lấy PID theo tên node chung nếu có nhiều tiến trình. Resource sampler ghi CPU seconds tích lũy, working_set_bytes và private_bytes mỗi giây. CPU% một core = delta CPU_seconds / delta wall_seconds *100; CPU% toàn máy chia tiếp logical processor count. Không diễn giải CPU seconds như %. Cần mở rộng theo dõi k6/system cho chạy chính thức để kiểm tra máy phát tải có bị giới hạn.

Runner bật dashboard export với period=1s, mặc định port=-1 để tự thoát. Các run chính dùng `-DashboardPort 5665`; mở http://127.0.0.1:5665 để xem live, đóng tab sau run nếu k6 đợi. HTML export tự chứa ở results/<run-id>/dashboard.html. Ba report chính đã mở bằng Edge headless, có biểu đồ dữ liệu và không lỗi JavaScript; ảnh QA không thay ảnh desktop. Grafana yêu cầu run dài hơn ba kỳ tổng hợp: https://grafana.com/docs/k6/latest/results-output/web-dashboard/.

## Bằng chứng cần thu chính thức

- Mỗi Load/Stress/Spike: raw.json, summary.json, cli.txt, manifest.json, dashboard.html; ảnh `<run-id>-k6-taskmanager.png` chụp thật CLI/dashboard và Task Manager tab Details cùng khung hình, PID backend/CPU/Memory rõ ràng.
- Load: bảng endpoint n,p95,RPS,failure,threshold. Stress: đồ thị từng bậc configured/actual VU, throughput,p95,failure, hold windows. Spike: timeline baseline/peak/recovery. Chưa tạo ba view từ smoke rồi gắn nhãn chính thức.
- Soak: thư mục riêng, raw/summary và resources.csv, chia cửa sổ steady, RPS,p95,error,RSS/CPU theo thời gian. Chưa kết luận ngưỡng.
- dxdiag: Win+R -> dxdiag -> System; ảnh hostname/CPU/RAM/OS. Save All Information ra hardware-dxdiag.txt trong results/hardware. Đối chiếu bài trước do sinh viên cung cấp, không đoán.
- Chỉ người dùng: review thực, xác nhận hostname bài trước, ghi hình/thu giọng tiếng Việt, YouTube Unlisted thật, điểm tự chấm, duyệt push/public/Issue/Moodle.

## Kịch bản dự kiến 7 phút, chưa phải transcript đã quay

00:00-00:45: “Tôi là sinh viên 23120330. Đây là workflow M5 với ba nhóm endpoint. Tôi dùng Windows Phuc; commit SUT chưa có vì bản archive, nên tôi lưu hash mã nguồn.” Chỉ nói hostname khớp bài trước sau xác nhận thật.

00:45-01:30: “Tôi đối chiếu payload và response với đặc tả, handler và smoke. Token reset được truyền trong cùng iteration, login dùng mật khẩu mới, JWT chỉ giữ trong bộ nhớ. Giỏ của tài khoản mới là mảng rỗng.” Hiển thị code không có mật khẩu/token.

01:30-02:40: Chạy Load đã duyệt, mở Task Manager cùng CLI/dashboard. “Tôi phân biệt VU cấu hình và throughput đo được. Đây là bảng endpoint, cửa sổ giữ tải và threshold dự thảo/đã chốt.” Đọc đúng số từ run chính thức khi có.

02:40-03:45: Hiển thị Stress và resource cùng khung hình. “Tôi so từng bậc giữ tải; nếu chưa vượt ngưỡng thì chưa tìm được giới hạn tối đa.” Không nói mức quá tải khi chưa có bằng chứng.

03:45-04:35: Spike: chỉ baseline, ramp, peak và recovery trên timeline thật, nói rõ recovery đủ dữ liệu hay chưa.

04:35-05:00: Soak 10 phút từ log thật, xem RAM/CPU theo thời gian; không cần phát video toàn bộ 10 phút nhưng phải có log đầy đủ.

05:00-06:30: Demo áp dụng SKILL.md lên toàn nhóm M5: đọc contract, sinh CSV namespace mới, smoke register/forgot/reset/login/cart, lưu raw, chạy analyzer và kiểm tra mẫu số. Hiển thị Task Manager cùng CLI. Đoạn này chưa thực hiện, không nhận là đã có video.

06:30-07:00: AI audit, sai sót thực sự, human review đã nhận và flowchart pipeline. Chỉ đưa số liệu đã đối chiếu, không đọc mẫu giả. Người dùng tự thuyết minh và cung cấp link Unlisted thật.

Skill replay thực tế sau khi tạo skill: skill-demo-load-20261119-144618-45deee1a, 5/5 E2E pass, 25requests, exit0. Chưa có video/giọng thuyết minh của sinh viên.

Đợt rerun có ảnh: xem evidence-reruns.md và resource_screenshot_runs trong submission-state.json. Stress5665 từng còn tab preview in-app giữ kết nối sau khi Chrome đóng; agent đã đóng đúng localhost preview bằng browser API. Spike dùng5666. Trước video lần tới, chỉ mở một tab live và đóng sau khi quay để k6 xuất summary; đọc số liệu theo execution window.
