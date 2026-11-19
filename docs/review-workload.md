# Assertions và workload - chờ human review

Workflow chỉ gồm Register -> Forgot -> Reset -> Login mật khẩu mới -> GET Cart. Mỗi bước check status và business contract trong plans/workflow.js, return sớm nếu lỗi. finally ghi started/finished, E2E success/failure, failed_step, E2E toàn bộ finalized và E2E success-only; hard interruption có thể bỏ qua finally nên phải đối chiếu started-finished và CLI interrupted. CSV exhaustion abort toàn run, không modulo. Không bật HTTP debug.

Mỗi run có đúng một scenario. SharedArray đọc CSV generator có field đơn giản, không dấu phẩy/nháy/newline; parser từ chối CSV có format khác, không tự nhận là parser RFC4180 tổng quát. iterationInTest lấy duy nhất một dòng; email có namespace RUN_ID mới. Generator tạo file bằng chế độ x, không ghi đè. Dữ liệu mật khẩu được sinh local, không commit; cần giữ CSV riêng tư để nộp sau rà soát. Thư mục results/data/runtime bị Git ignore.

## Smoke thực tế

Run thành công `smoke-load-20261119-141451-dc433d78`, 1 VU, 5 iterations, think 1 s cuối iteration, exit 0. 25 requests, 50 checks đạt; 5 started=finished=passed, CSV không hết. HTTP failed 0/25, E2E failed 0/5. p95 E2E success và toàn finalized =43.4 ms, không chứa think-time. Không có mẫu dropped_iterations; executor closed VU không dùng để chứng minh khả năng đáp ứng arrival-rate.

| endpoint | n | p95 ms | HTTP failures |
|---|---|---|---|
| register | 5 | 24.71626 | 0/5 |
| forgot | 5 | 5.53628 | 0/5 |
| reset | 5 | 4.91606 | 0/5 |
| login | 5 | 4.05164 | 0/5 |
| cart | 5 | 3.07404 | 0/5 |

Nguồn results/<run-id>/raw.json; script độc lập scripts/analyze.py ghi analysis.json. Cửa sổ manifest start/end 5.7435009479522705 s gồm startup/export: HTTP 25/5.7435=4.352746 RPS; E2E 5/5.7435=0.870549/s. k6 summary rate dùng cửa sổ khác (HTTP 4.865844/s), không so hai giá trị như cùng mẫu số. Năm mẫu/endpoint không đủ kết luận p95 ổn định.

Hai smoke trước đó (141350-b8bcb06e, 141405-d6f8dd6c) lỗi kết nối môi trường; exit 99, 5 E2E fail mỗi run. Giữ log riêng; loại khỏi kết luận SUT. Lần đầu socket bị sandbox cấm; lần hai backend ở môi trường sandbox khác. Chạy cả hai tiến trình ở Windows cùng môi trường thì pass. Không phát sinh login sai/lockout trên run thành công. Không cần reset lockout.

## Tải draft, chưa pilot, chưa duyệt

| Profile | Cấu hình closed VU | Mục đích |
|---|---|---|
| Pilot (dự kiến) | dùng Load override 1/2/5 VU, mỗi bậc 30 s hold, ramp 10 s | đo tài nguyên, latency, throughput trước chọn tải chính thức |
| Load draft | 0->2/30 s; giữ 2 VU/120 s; xuống 0/15 s | đo vùng ổn định riêng khỏi ramp |
| Stress draft | 2,5,10 VU; ramp 15 s và hold 45 s mỗi bậc; xuống 0/15 s | tìm bậc đầu vượt ngưỡng đề xuất nếu thực sự thấy |
| Spike draft | baseline 2/45 s sau ramp 15 s; lên 15/2 s; giữ 30 s; về 2/2 s; hồi phục 60 s; xuống 0/10 s | so baseline/peak/recovery với cửa sổ đủ mẫu |
| Soak draft | 2 VU liên tục 10 phút | chỉ chứng minh mức này nếu chạy ổn định; chưa có ngưỡng endurance |

Think 1 s, timeout request 10 s, graceful stop/ramp-down 15 s. Closed VU tự giảm throughput khi latency tăng, cần báo tải thực tế và xem xét arrival-rate nếu mục tiêu sau review cần RPS cố định. 20000 dòng mặc định đủ soak draft: tối đa xấp xỉ VU*giây/1s + grace; kiểm tra lại khi đổi tải/think. Threshold sơ bộ p95 HTTP từng endpoint<500 ms, p95 E2E success<2000 ms, HTTP fail<1%, E2E success>99%, CSV exhausted=0. Đây là giả thuyết chất lượng để review, chưa suy ra từ 5 mẫu smoke hay SLA của đề.

Agent corrections thực tế: chuyển pacing vào finally vì return sớm bỏ qua sleep ở cuối hàm; bổ sung mẫu số/cửa sổ RPS; đánh dấu dropped metric không xuất hiện thay vì nói đã đo 0; status reset lấy từ runtime vì đặc tả không ghi. Human feedback về assertion/workload: chưa nhận; người dùng đã xác nhận phạm vi GETcart theo method+path và cung cấp ảnh, không đồng nghĩa duyệt toàn bộ assertions/tải.
