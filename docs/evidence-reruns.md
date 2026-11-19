# Rerun để thu ảnh thật - 2026-11-19

MSSV 23120330. Múi giờ Asia/Ho_Chi_Minh. Các run gốc trong main-report.md giữ nguyên; các run trong phụ lục này không tự thay thế chúng.

## Điều kiện và provenance

- Backend local http://127.0.0.1:3000, PID 32692. Cổng dashboard riêng http://127.0.0.1:5665 chỉ có khi k6 phục vụ dashboard.
- Runtime mới: runtime/evidence-20261119-1511/backend. DB test cũ runtime/backend/database.sqlite và DB SUT gốc không bị reset. NODE_PATH dùng node_modules đã cài từ lockfile ở runtime/backend; không cài dependency trong lượt đo này.
- Commit test plan khi bắt đầu: c673a8b. Thêm m5_scenario_start_epoch_ms từ k6 scenario.startTime để chia stage trực tiếp; workflow, assertion và tải giữ nguyên.
- Namespace CSV riêng cho từng run. Manifest mới có runtime hashes, DB path, test plan commit và workflow SHA256.
- Người dùng tự bố trí/chụp Task Manager do higher integrity chặn helper. Không dùng ảnh ghép, ảnh dựng hoặc ảnh của lượt khác.

## Sự cố dashboard và mẫu số throughput

Ảnh ban đầu ERR_CONNECTION_REFUSED không phải lỗi HTTP của SUT: chỉ backend3000 đang chạy, chưa có dashboard5665. Sau khi bật k6 Load rerun, kiểm tra socket thấy PID k6 11300 trên5665 và HTTP GET dashboard trả200.

K6 có thể đợi tab dashboard sau khi workload kết thúc. Không lấy thời gian người dùng đang xem/đóng tab để đánh giá RPS thực thi. Analyzer mới giữ wall-window để truy vết, bổ sung RPS/throughput theo summary.state.testRunDurationMs. Cả hai cửa sổ được ghi nhãn riêng; không sửa raw hay thời gian của lượt cũ. Trong rerun Load, CLI đã báo 689 complete/0 interrupted ở2m45s nhưng summary/manifest hoàn tất còn đợi tab đóng tại thời điểm ghi ghi chú này.

## Run register

| Profile | Run ID | Trạng thái | Ảnh cùng khung |
|---|---|---|---|
| Load | rerun-load-20261119-162216-d7ab78da | Workload kết thúc; đang đợi dashboard để hoàn tất artifacts | Chưa nhận ảnh đủ dashboard+TaskManager |
| Load - ảnh trong hold | rerun-load-20261119-163449-813f2702 | CLI báo 691 complete/0 interrupted, 2m45s; đang đợi tab đóng để có summary | Đã nhận load-k6-taskmanager.png, chart tới khoảng16:36:10 trong vùng hold, PID32692/CPU/Memory rõ |
| Stress | Chưa chạy | Đợi cổng5665 của Load được giải phóng | Chưa có |
| Spike | Chưa chạy | Sau Stress | Chưa có |

Ảnh người dùng đã gửi được giữ nguyên byte trong results/evidence-support/taskmanager-selected-pid-32692.png và dashboard-before-rerun-connection-refused.png. Đây là ảnh hỗ trợ chẩn đoán, không đánh dấu resource_screenshots.Load/Stress/Spike=true từ hai ảnh này. Timestamp import không phải timestamp chụp.

Ảnh Load mới hợp lệ được người dùng gửi từ codex-clipboard-7229886a-05c8-4679-bbfc-199d4ea80511.png. Đã sao nguyên byte vào results/rerun-load-20261119-163449-813f2702/load-k6-taskmanager.png; metadata và SHA256 trong screenshot-evidence.json. submission-state.json liên kết ảnh với đúng rerun qua resource_screenshot_runs.Load. Card25/s là snapshot, không phải RPS tổng run. Task Manager CPU00 là giá trị hiển thị được làm tròn, không được diễn giải là không sử dụng CPU. Đây là agent kiểm tra bằng chứng, không phải sinh viên duyệt toàn bộ báo cáo/critique.
