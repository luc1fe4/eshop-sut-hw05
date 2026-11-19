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
| Load | rerun-load-20261119-162216-d7ab78da | Workload 689 complete/0 interrupted; controller đã dừng sau workload khi đợi dashboard để nhường cổng. Không có summary; không nhận là run hoàn tất artifacts | Chưa nhận ảnh đủ khi workload hoạt động |
| Load - ảnh trong hold | rerun-load-20261119-163449-813f2702 | Completed, exit0; 691/691 E2E, 3455HTTP, 0lỗi; p95E2E34ms; đã verify raw độc lập | Đã nhận load-k6-taskmanager.png, chart tới khoảng16:36:10 trong vùng hold, PID32692/CPU/Memory rõ |
| Stress | rerun-stress-20261119-164026-b02a7bbd | Workload5/15/30VU đã chạy hết:2890complete/0interrupted; đợi tab đóng để xuất summary | Đã nhận stress-k6-taskmanager.png trong hold15VU, khoảng73HTTP/s, PID32692/CPU/Memory |
| Spike | Chưa chạy | Sau Stress | Chưa có |

Ảnh người dùng đã gửi được giữ nguyên byte trong results/evidence-support/taskmanager-selected-pid-32692.png và dashboard-before-rerun-connection-refused.png. Đây là ảnh hỗ trợ chẩn đoán, không đánh dấu resource_screenshots.Load/Stress/Spike=true từ hai ảnh này. Timestamp import không phải timestamp chụp.

Ảnh Load mới hợp lệ được người dùng gửi từ codex-clipboard-7229886a-05c8-4679-bbfc-199d4ea80511.png. Đã sao nguyên byte vào results/rerun-load-20261119-163449-813f2702/load-k6-taskmanager.png; metadata và SHA256 trong screenshot-evidence.json. submission-state.json liên kết ảnh với đúng rerun qua resource_screenshot_runs.Load. Card25/s là snapshot, không phải RPS tổng run. Task Manager CPU00 là giá trị hiển thị được làm tròn, không được diễn giải là không sử dụng CPU. Đây là agent kiểm tra bằng chứng, không phải sinh viên duyệt toàn bộ báo cáo/critique.

Load có ảnh: duration k6=165.5063627s, HTTP throughput thực thi=3455/165.5063627=20.875330HTTP/s, E2E throughput=4.175066/s. Wall interval260.483492s có cả chờ dashboard; không dùng giá trị wall13.263796HTTP/s để đánh giá tải thực thi. Các p95 endpoint register/forgot/reset/login/cart lần lượt10.6319/10.14365/8.97615/6.4244/2.449ms. Raw, summary, analysis, verification và view được giữ tại đúng thư mục rerun, không thay bảng kết quả run gốc.
