# Bản ghi Audit tương tác Skill Demo M5 - 2026-11-22

- **Công cụ / Agent**: Antigravity (Gemini 3.8 Flash)
- **Mã số sinh viên**: 23120330
- **Múi giờ**: Asia/Ho_Chi_Minh (+07:00)
- **Thời điểm agent ghi nhận bắt đầu**: 2026-11-22T20:03:10+07:00 *(Lưu ý: Đây là mốc thời gian môi trường agent ghi nhận khi nhận lượt xử lý, không tự nhận là giờ gửi chính xác từ phía người dùng)*.
- **Thời điểm chạy test thực tế**: 2026-11-22T20:08:15.9307488+07:00 đến 2026-11-22T20:08:23.0552430+07:00
- **Mã run ID**: `skill-demo-load-20261122-200815-7a78d5c4`

---

## 1. Prompt người dùng nguyên văn

```text
Tôi đang quay video HW05-AI của MSSV23120330.
Áp dụng skill trong hw05-m5/skills/k6-workflow-audit/SKILL.md
để thực hiện một demo thật trên đủ Register -> Forgot -> Reset
-> Login mật khẩu mới -> GET Cart.

Đọc SKILL.md, API contract và Git status; xác minh backend local
và runtime test riêng đang dùng. Không khởi động lại DB hiện có.
Chạy scripts/run.ps1 với Profile Load, Kind skill-demo, Rows10,
1VU/5iterations theo cấu hình smoke, DashboardPort=-1,
BackendPid và BackendDir đã xác minh đúng.

Giữ nguyên các lượt trước, không đổi profile chính hay SUT.
Không in CSV, password, resetToken, JWT, cookie hay response auth.
Không dump nguyên server.js hoặc .env lên output; chỉ hiển thị
thông tin đã loại giá trị bí mật nếu cần đối chiếu mã nguồn.
Sau run, chạy analyze.py và verify-raw.py cho chính thư mục mới.
Hiển thị bảng đủ năm endpoint: số mẫu, p95 và tỷ lệ HTTP failure;
hiển thị E2E pass/fail, iteration chưa hoàn tất, nguồn raw và
trạng thái exit. Phân biệt HTTP với E2E và mẫu số throughput.

Lưu prompt này và output thực tế cho audit; nếu thời điểm chỉ là
giờ agent ghi nhận thì ghi rõ, không tự nhận là giờ gửi chính xác.
Không push, đăng Issue hoặc upload bất kỳ dữ liệu nào.
```

---

## 2. Xác minh môi trường & SUT trước khi thực thi

1. **Giới hạn Git SUT**:
   - Thư mục gốc `eshop-sut-main` là archive tải về, không có `.git`. Hashing mã nguồn runtime để xác định tính toàn vẹn:
     - `backend/server.js`: `47573CE5A6BF9A894748D2BB56CC8D1659AD7ACD033FDD6DB6B3E4D9473EB487`
     - `backend/database.js`: `3366420632BB9C982905B22E3969F69515E39E7A37A4F84EBA56EAD7E94AFED8`
2. **Git status của `hw05-m5`**:
   - Commit HEAD: `659295e90e9cedbbc0a88ef8fe48a668d39e1959`
   - Nhánh: `master`, trạng thái `working tree clean`.
3. **Backend local đang phục vụ**:
   - Cổng 3000 đang được lắng nghe bởi PID `28820` (`node server.js`).
   - Thư mục backend hoạt động: `D:\Regular_School\N4\HK1\Testing\HW04\eshop-sut-main\backend`.
   - CSDL `database.sqlite` được giữ nguyên, không khởi động lại hoặc chạy seed DROP table.
   - Thử nghiệm kết nối an toàn: `curl.exe http://127.0.0.1:3000/api/cart` trả về HTTP `401 Unauthorized` (đúng API contract do chưa có JWT).

---

## 3. Lệnh thực thi k6

```powershell
& .\hw05-m5\scripts\run.ps1 -Profile Load -Kind skill-demo -Rows 10 -BackendPid 28820 -BackendDir ((Resolve-Path .\backend).Path) -DashboardPort -1
```

- Cấu hình smoke sinh ra namespace riêng biệt `skill-demo-load-20261122-200815-7a78d5c4`.
- Dữ liệu CSV 10 dòng độc lập, nạp qua `SharedArray`, không wrap lặp.
- Pacing 1 giây được thực hiện an toàn trong khối `finally` của workflow.
- Không in CSV, password, resetToken, JWT, cookie, hoặc auth body.

---

## 4. Kết quả thực thi thực tế & Phân tích độc lập

- **Thư mục kết quả**: `hw05-m5/results/skill-demo-load-20261122-200815-7a78d5c4/`
- **Nguồn raw samples**: `raw.json` (SHA256: `b7a3647b704a96f94ef266536dd26f608c0a0deaa5895c2d4c3f947464172e4d`)
- **Trạng thái k6 exit**: `0` (`completed`)
- **E2E Outcomes**:
  - `m5_started`: 5
  - `m5_finished`: 5
  - `m5_passed`: 5 (Pass rate 100%, 0 failed E2E)
  - `unfinished_started_minus_finished`: 0 (Không có iteration nào bị đứt đoạn hoặc bỏ dở)
  - `m5_csv_exhausted`: 0
- **Thời lượng đo**:
  - Execution window (`summary.state.testRunDurationMs`): 5.132 giây
  - Wall-clock window (từ manifest start tới end): 7.124 giây

### Bảng chỉ số 5 Endpoint (HTTP Metrics)

| Endpoint | Method/Path | Số mẫu (Samples) | p95 Response Time (ms) | HTTP Failure Rate |
|---|---|---|---|---|
| **Register** | POST /api/register | 5 | 10.24 ms | 0.0% (0/5) |
| **Forgot** | POST /api/forgot-password | 5 | 5.38 ms | 0.0% (0/5) |
| **Reset** | POST /api/reset-password | 5 | 5.37 ms | 0.0% (0/5) |
| **Login** | POST /api/login | 5 | 3.75 ms | 0.0% (0/5) |
| **Cart** | GET /api/cart | 5 | 3.13 ms | 0.0% (0/5) |

### Phân biệt HTTP vs E2E & Mẫu số Throughput

- **Tổng số HTTP Requests**: 25 requests (5 requests / iteration * 5 iterations), HTTP failure = 0.
- **HTTP Throughput**:
  - Theo Execution Window (5.132s): $25 / 5.132 \approx 4.871\text{ req/s}$
  - Theo Wall Window (7.124s): $25 / 7.124 \approx 3.509\text{ req/s}$
- **E2E Workflow Throughput** (Chỉ tính E2E hoàn thành trọn vẹn 5 bước):
  - Theo Execution Window (5.132s): $5 / 5.132 \approx 0.974\text{ workflow/s}$
  - Theo Wall Window (7.124s): $5 / 7.124 \approx 0.702\text{ workflow/s}$
- **E2E Latency**:
  - p95 E2E (không bao gồm think-time 1s): 33.0 ms
  - Thuộc tính think-time: 1.0 giây được đưa vào `sleep` giữa các iteration và tách biệt hoàn toàn khỏi `m5_e2e_all_ms` / `m5_e2e_success_ms`.
- **Dropped iterations**:
  - `dropped_iterations`: Không quan sát được mẫu nào (`dropped_iterations_sample_count = 0`). Vì test dùng executor `shared-iterations` (closed VU model), k6 không phát sinh metric dropped iterations như ở open model (arrival-rate). Do đó ghi nhận đúng bản chất là không quan sát / không áp dụng, không ngộ nhận là đo được dropped=0 của arrival-rate.

---

## 5. Kết quả kiểm tra độc lập (`verify-raw.py`)

- Thuật toán độc lập: `statistics.quantiles(n=100, method='inclusive')` của Python standard library.
- Kết quả đối chiếu với k6 summary:
  - `http_req_duration{endpoint:register}`: 10.23906 ms (khớp 100%)
  - `http_req_duration{endpoint:forgot}`: 5.37614 ms (khớp 100%)
  - `http_req_duration{endpoint:reset}`: 5.37208 ms (khớp 100%)
  - `http_req_duration{endpoint:login}`: 3.74696 ms (khớp 100%)
  - `http_req_duration{endpoint:cart}`: 3.12764 ms (khớp 100%)
  - `m5_e2e_all_ms`: 33.0 ms (khớp 100%)
  - `m5_e2e_success_ms`: 33.0 ms (khớp 100%)
  - `all_p95_match`: `true`
