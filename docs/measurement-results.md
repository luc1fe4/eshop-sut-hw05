# Kết quả đo thực tế - AI analysis output

Nguồn: raw.json từng mẫu; analyzer độc lập và statistics.quantiles so với summary k6. E2E không gồm think 1s; cả distribution all-finalized và success-only được lưu. Tất cả E2E thành công ở các run dưới nên hai tập trùng nhau. RPS bảng tổng dùng manifest start/end, gồm overhead, khác rate summary k6.

| Run ID | E2E pass/finalized | HTTP n | E2E p95 ms | HTTP RPS (wall) | E2E/s (wall) | HTTP/E2E lỗi |
|---|---|---|---|---|---|---|
| official-load-20261119-142516-6bca3e35 | 682/682 | 3410 | 62.00 | 20.429 | 4.086 | 0/3410; 0/682 |
| official-stress-20261119-142841-f8a69e2c | 2864/2864 | 14320 | 100.00 | 72.365 | 14.473 | 0/14320; 0/2864 |
| official-spike-20261119-143230-4cb4886b | 1810/1810 | 9050 | 98.00 | 54.345 | 10.869 | 0/9050; 0/1810 |
| soak-load-20261119-143548-37e75817 | 2858/2858 | 14290 | 67.00 | 23.723 | 4.745 | 0/14290; 0/2858 |

Tất cả run chính trên exit 0, threshold sơ bộ pass, started=finished=iterations, CLI 0 interrupted. Không có mẫu dropped_iterations; closed-VU executor không cung cấp phép đo đảm bảo arrival rate. CSV namespace count/distinct email và reset token cleared đối chiếu db-after.json. Hai smoke lỗi kết nối được giữ riêng, không nhập vào bảng này.

## Threshold đề xuất và giới hạn kết luận

Threshold ban đầu: p95 từng endpoint<500 ms, E2E success p95<2000 ms, HTTP failure<1%, E2E success>99%, CSV exhausted=0. Đây là guardrail do agent đề xuất trước pilot, không phải SLA được đề bài cho. Kết quả đo pass không chứng minh đây là SLA phù hợp sản xuất. Đề xuất sau log: giữ guardrail để phát hiện failure nặng, thêm so baseline tương đương với quy tắc >20% và >10ms, rerun 2/3 để giảm nhiễu; cần hiệu chỉnh bằng thêm run.

## official Load: official-load-20261119-142516-6bca3e35

Bắt đầu 2026-11-19T14:25:17.0690722+07:00; kết thúc 2026-11-19T14:28:03.9900675+07:00; cửa sổ wall 166.920995s. Testplan effective commit 52cbf3e; SUT commit chưa biết, hash trong manifest. Raw/summary/analysis/verification ở results/official-load-20261119-142516-6bca3e35/.

| Endpoint | n | p95 ms | RPS wall | failure | p95<500ms |
|---|---|---|---|---|---|
| register | 682 | 19.4701 | 4.0858 | 0/682 | pass |
| forgot | 682 | 21.8586 | 4.0858 | 0/682 | pass |
| reset | 682 | 17.0243 | 4.0858 | 0/682 | pass |
| login | 682 | 12.0904 | 4.0858 | 0/682 | pass |
| cart | 682 | 3.3359 | 4.0858 | 0/682 | pass |

View riêng: bảng endpoint view.html; không dùng lại kiểu biểu đồ Stress/Spike.

| Hold (giây từ clock suy ra) | VU cấu hình / min-max đo | HTTP n / RPS | HTTP p95 ms | E2E n / p95 ms | failure HTTP |
|---|---|---|---|---|---|
| 32-148 | 5 / 5-5 | 2800 / 24.138 | 18.758 | 560 / 63.000 | 0/2800 |

Clock stage suy từ mẫu gauge VU định kỳ đầu trừ 1s; độ lệch chưa được đo chính xác. Bỏ 2s hai đầu hold, kiểm tra actual VU ổn định. Cấp mẫu theo timestamp hoàn tất, request vượt ranh giới được tính vào cửa sổ hoàn tất. Không gọi đây là phân ranh tuyệt đối chính xác; lần sau nên ghi scenario.startTime trực tiếp.

Resource samples=103; backend RSS first/last/peak=72.64/55.84/89.10 MiB; backend CPU mean/peak toàn máy=0.297/0.796%. CPU tính delta CPU seconds/delta time/16, không nhầm CPU seconds với phần trăm. K6 CPU peak toàn máy=5.660935472289436; system CPU peak=45.0%; available RAM thấp nhất=1560.26171875 MiB.

## official Stress: official-stress-20261119-142841-f8a69e2c

Bắt đầu 2026-11-19T14:28:41.6478615+07:00; kết thúc 2026-11-19T14:31:59.5336918+07:00; cửa sổ wall 197.885830s. Testplan effective commit 52cbf3e; SUT commit chưa biết, hash trong manifest. Raw/summary/analysis/verification ở results/official-stress-20261119-142841-f8a69e2c/.

| Hold (giây từ clock suy ra) | VU cấu hình / min-max đo | HTTP n / RPS | HTTP p95 ms | E2E n / p95 ms | failure HTTP |
|---|---|---|---|---|---|
| 17-58 | 5 / 5-5 | 1000 / 24.390 | 17.524 | 200 / 55.050 | 0/1000 |
| 77-118 | 15 / 15-15 | 2945 / 71.829 | 22.054 | 589 / 76.000 | 0/2945 |
| 137-178 | 30 / 30-30 | 5850 / 142.683 | 31.068 | 1170 / 104.000 | 0/5850 |

Clock stage suy từ mẫu gauge VU định kỳ đầu trừ 1s; độ lệch chưa được đo chính xác. Bỏ 2s hai đầu hold, kiểm tra actual VU ổn định. Cấp mẫu theo timestamp hoàn tất, request vượt ranh giới được tính vào cửa sổ hoàn tất. Không gọi đây là phân ranh tuyệt đối chính xác; lần sau nên ghi scenario.startTime trực tiếp.

Stress: throughput tăng qua 5/15/30 VU, không có bậc nào vượt guardrail đã đặt. Chưa tìm được bậc lỗi đầu tiên và chưa đo ngưỡng tối đa. Không quy kết bottleneck SQLite từ việc latency tăng.

![Stress stage chart](../results/official-stress-20261119-142841-f8a69e2c/stress-stages.png)

Resource samples=124; backend RSS first/last/peak=55.89/58.84/94.37 MiB; backend CPU mean/peak toàn máy=0.939/2.450%. CPU tính delta CPU seconds/delta time/16, không nhầm CPU seconds với phần trăm. K6 CPU peak toàn máy=3.1878346735971173; system CPU peak=33.0%; available RAM thấp nhất=1279.95703125 MiB.

## official Spike: official-spike-20261119-143230-4cb4886b

Bắt đầu 2026-11-19T14:32:30.6281249+07:00; kết thúc 2026-11-19T14:35:17.1555854+07:00; cửa sổ wall 166.527461s. Testplan effective commit 52cbf3e; SUT commit chưa biết, hash trong manifest. Raw/summary/analysis/verification ở results/official-spike-20261119-143230-4cb4886b/.

| Hold (giây từ clock suy ra) | VU cấu hình / min-max đo | HTTP n / RPS | HTTP p95 ms | E2E n / p95 ms | failure HTTP |
|---|---|---|---|---|---|
| 17-58 | 5 / 5-5 | 1000 / 24.390 | 18.337 | 200 / 66.050 | 0/1000 |
| 64-90 | 40 / 40-40 | 4951 / 190.423 | 27.715 | 994 / 105.350 | 0/4951 |
| 96-152 | 5 / 5-5 | 1350 / 24.107 | 12.439 | 270 / 44.550 | 0/1350 |

Clock stage suy từ mẫu gauge VU định kỳ đầu trừ 1s; độ lệch chưa được đo chính xác. Bỏ 2s hai đầu hold, kiểm tra actual VU ổn định. Cấp mẫu theo timestamp hoàn tất, request vượt ranh giới được tính vào cửa sổ hoàn tất. Không gọi đây là phân ranh tuyệt đối chính xác; lần sau nên ghi scenario.startTime trực tiếp.

Spike: baseline 17-58s đạt 24.390 HTTP RPS; peak hold 64-90s đạt 190.423 RPS; hồi phục 96-152s đạt 24.107 RPS. p95 E2E lần lượt 66.05 / 105.35 / 44.55 ms, HTTP failure đều 0. Dữ liệu hỗ trợ hồi phục ở cửa sổ tổng hợp này; không chứng minh recovery time chính xác từng giây.

![Spike timeline](../results/official-spike-20261119-143230-4cb4886b/spike-timeline.png)

Resource samples=104; backend RSS first/last/peak=58.87/83.50/94.54 MiB; backend CPU mean/peak toàn máy=0.854/3.514%. CPU tính delta CPU seconds/delta time/16, không nhầm CPU seconds với phần trăm. K6 CPU peak toàn máy=3.5099219310602265; system CPU peak=40.0%; available RAM thấp nhất=1464.7265625 MiB.

## soak Load: soak-load-20261119-143548-37e75817

Bắt đầu 2026-11-19T14:35:49.0068393+07:00; kết thúc 2026-11-19T14:45:51.3734876+07:00; cửa sổ wall 602.366648s. Testplan effective commit 52cbf3e; SUT commit chưa biết, hash trong manifest. Raw/summary/analysis/verification ở results/soak-load-20261119-143548-37e75817/.

| Hold (giây từ clock suy ra) | VU cấu hình / min-max đo | HTTP n / RPS | HTTP p95 ms | E2E n / p95 ms | failure HTTP |
|---|---|---|---|---|---|
| 2-58 | 5 / 5-5 | 1344 / 24.000 | 20.765 | 267 / 62.000 | 0/1344 |
| 62-118 | 5 / 5-5 | 1330 / 23.750 | 20.288 | 266 / 65.750 | 0/1330 |
| 122-178 | 5 / 5-5 | 1325 / 23.661 | 22.032 | 265 / 66.000 | 0/1325 |
| 182-238 | 5 / 5-5 | 1330 / 23.750 | 21.341 | 266 / 69.000 | 0/1330 |
| 242-298 | 5 / 5-5 | 1325 / 23.661 | 22.923 | 265 / 71.800 | 0/1325 |
| 302-358 | 5 / 5-5 | 1325 / 23.661 | 24.017 | 265 / 74.000 | 0/1325 |
| 362-418 | 5 / 5-5 | 1335 / 23.839 | 17.279 | 267 / 55.700 | 0/1335 |
| 422-478 | 5 / 5-5 | 1330 / 23.750 | 21.612 | 266 / 67.750 | 0/1330 |
| 482-538 | 5 / 5-5 | 1335 / 23.839 | 20.711 | 267 / 68.400 | 0/1335 |
| 542-598 | 5 / 5-5 | 1355 / 24.196 | 17.798 | 271 / 57.500 | 0/1355 |

Clock stage suy từ mẫu gauge VU định kỳ đầu trừ 1s; độ lệch chưa được đo chính xác. Bỏ 2s hai đầu hold, kiểm tra actual VU ổn định. Cấp mẫu theo timestamp hoàn tất, request vượt ranh giới được tính vào cửa sổ hoàn tất. Không gọi đây là phân ranh tuyệt đối chính xác; lần sau nên ghi scenario.startTime trực tiếp.

Resource samples=377; backend RSS first/last/peak=83.48/99.13/100.96 MiB; backend CPU mean/peak toàn máy=0.340/0.861%. CPU tính delta CPU seconds/delta time/16, không nhầm CPU seconds với phần trăm. K6 CPU peak toàn máy=0.973291631809849; system CPU peak=61.0%; available RAM thấp nhất=1632.69140625 MiB.

Soak kiểm chứng **5 VU liên tục 10 phút**, HTTP trung bình wall=23.723 RPS; p95 E2E=67.00ms. Đây là mức ổn định đã thử trên máy, **không phải ngưỡng tối đa**. RSS peak là đỉnh quan sát, không phải memory ceiling. Chia các cửa sổ xấp xỉ một phút có trimming trong phases.csv; 5s bins và CPU/RAM trong phases.json. Không kết luận memory leak chỉ từ RSS đầu-cuối, cần nhiều run và kiểm tra heap.

![Soak timeline](../results/soak-load-20261119-143548-37e75817/soak-windows.png)

## Điều kiện đo và độ nhiễu

Backend và k6 cùng Windows PHUC, nhiều ứng dụng cá nhân đang mở. Có hoạt động chuẩn bị tài liệu, cài dependency (bộ Playwright tải lâu đã hủy), dxdiag và kiểm tra HTML/PDF trong phiên đo. Resource sampler gọi CIM khoảng 1-2 giây/mẫu; không phải profiler high-resolution. Các yếu tố này giới hạn độ lặp lại, không dùng làm benchmark máy sạch. Không quan sát CPU k6 gần toàn máy trong samples nhưng chưa chứng minh không có giới hạn I/O hoặc scheduler. DB test tăng số user giữa các run, không reset để giữ namespace; số lượng trước/sau có db-before/db-after cho run chính. Muốn A/B tối ưu phải clone cùng DB cardinality và tắt tác vụ nền trước rerun.
