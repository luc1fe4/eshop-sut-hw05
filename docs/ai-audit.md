# AI Audit Report - working appendix

I use AI tools for the following tasks,

thiết kế contract/assertion, tạo test plans/generator/runner/analyzer, chạy local và phân tích log, chuẩn bị báo cáo/pipeline/skill. Công cụ AI: Codex trong ứng dụng desktop; phiên hiện tại không cung cấp nhãn model cụ thể đáng tin cậy, không đoán phiên bản. Không dùng AI khác hay sub-agent. Công cụ hỗ trợ đã dùng: PowerShell, Git, Node.js v22.17.1, npm, k6 v2.2.0, Python, Grafana documentation qua web search, skill-creator, PDF skill, Computer Use @oai/sky, Codex workspace dependency locator. Bổ sung phiên bản package từ installation record khi tạo PDF/view.

## Tính đầy đủ và nguồn

Đây là audit đang làm, không giả làm transcript toàn bộ. Prompt gốc là yêu cầu HW05-AI của sinh viên trong chat ngày 2026-11-19 (Asia/Ho_Chi_Minh); giờ gửi chính xác không được cung cấp trong ngữ cảnh. Các câu dưới là **trích đoạn nguyên văn**, không phải prompt dựng lại. Output code thực tế nằm trong commits; output lệnh nằm trong results. Cần đính kèm bản export chat gốc trước khi nộp để đáp ứng yêu cầu toàn bộ tương tác. Không tự đặt timestamp cho tin nhắn không có timestamp.

| Tương tác thật | Prompt nguyên văn / trạng thái | Output thực tế và nguồn |
|---|---|---|
| Thiết kế và smoke; ngày 2026-11-19, giờ prompt chưa có | “Bắt đầu ngay bằng việc đọc đề và repo, lập bảng API contract, xác minh `resetToken`, JWT và response của giỏ rỗng, sau đó triển khai và chạy smoke nếu đủ điều kiện.” (trích đoạn prompt gốc; backtick giữ nguyên ý đoạn hiển thị) | docs/api-contract.md, plans/*.js, scripts/*.py, scripts/run.ps1; smoke thành công lúc 14:14:51 +07, raw.json và summary.json |
| Phản hồi human scope; ngày 2026-11-19, giờ tin nhắn chưa có | “Giữ GET /api/cart; không trùng theo method+path” | Giữ GET /api/cart, không đổi product detail. Đây là human review thực sự về phạm vi, không suy thành duyệt toàn bộ workload/assertions. |
| Hardware continuity; ngày 2026-11-19, giờ tin nhắn chưa có | “Cần kiểm tra hostname bài trước” | Host Phuc/PHUC đã đo thật; chưa xác nhận khớp bài trước. |
| Phân tích độc lập smoke lúc 14:15 sau run; timestamp lệnh chính xác không lưu | Yêu cầu gốc: “Sau khi có raw log thật, dùng AI phân tích và đề xuất threshold.” (trích đoạn) | docs/audit/actual-first-smoke-analysis.json là output thực tế của analyzer phiên đầu, được giữ nguyên trước sửa; kết quả đúng và audit bên dưới. Không coi lệnh do agent tự tạo là prompt mới do sinh viên viết. |

Trong quá trình, lần cài npm đầu bị network sandbox (ENOTFOUND), smoke đầu bị socket forbidden, smoke tiếp theo khác môi trường backend bị timeout. Chuyển cài dependencies và cả hai tiến trình test sang môi trường Windows có quyền local thì pass. Giữ hai smoke failed riêng. Một kiểm tra npm offline tạm không có lockfile cũng thất bại EUSAGE; không phải kết quả SUT. Không xóa dấu vết hay gộp failed vào success.

Auto-review từ chối đọc nodeRepl.requestMeta để tìm metadata transcript vì có thể lộ dữ liệu chat/session riêng tư không liên quan. Không đọc được metadata và không thử đường vòng. Audit dùng nội dung đang có, có ghi giới hạn.

## Misinterpretation hunt thực tế

| Phát biểu/output AI nguyên văn | Giá trị đúng | Raw/tag/cách tính | Vì sao sai hoặc thiếu | Sửa |
|---|---|---|---|---|
| `"dropped_iterations": 0` trong actual-first-smoke-analysis.json | Không có mẫu metric này; không áp dụng arrival-rate cho shared-iterations | raw smoke thành công; lọc type=Point, metric=dropped_iterations cho 0 dòng | Script sum tập rỗng cho 0 làm biểu diễn dễ bị hiểu là đã đo không drop | Phiên sau xuất null + observed=false, applicable=false; không kết luận khả năng giữ arrival rate |
| `"start_seconds": 30`, `"end_seconds": 150`, `"http_rps": 24.041666666666668` trong actual-first-load-phases.json (hold-2) | Hold đã trim theo clock suy ra 32-148s: 2800 HTTP/116s=24.137931 RPS; VU min=max=5, p95 HTTP 18.758175ms | Load raw: first VU gauge 14:25:19.3328054+07; first iteration bị trễ do ramp 0->5; phases.json mới ghi origin=first gauge-1s | AI dùng first iteration làm clock test, trộn một phần ramp-down vào hold; output cũ minVU=4 là dấu hiệu phát hiện | Sửa clock, bỏ 2s mỗi đầu hold và kiểm tra actual VU. Đây là clock suy ra, không giả định timestamp chính xác tuyệt đối. |

Chưa quan sát lỗi AI tính p95 trên smoke: linear interpolation độc lập khớp summary trong sai số float. Không dựng một phát biểu p95/RPS sai để có thêm dòng hunt. Agent tự sửa code pacing ở finally và bổ sung cửa sổ RPS; đó là self-review, chưa phải human correction.

Phân tích sau raw chính thức: measurement-results.md là output AI thật được biên soạn từ analysis.json/phases.json. verification.json dùng Python statistics.quantiles(method=inclusive), khác code percentile analyzer, xác nhận p95 mỗi endpoint và E2E khớp k6 summary trong 1e-7ms. Ba dashboard.html mở trong Edge headless có 14canvas, 2SVG/file, không lỗi JavaScript; ảnh QA thật chỉ dùng xác minh HTML. Bổ sung kết quả soak khi đủ 10phút. Đây không thay review của sinh viên.

## Đề xuất tối ưu và đối chiếu mã nguồn (AI output dự thảo)

| Đề xuất của agent | Phân loại | Bằng chứng và kiểm chứng cần thêm |
|---|---|---|
| Index users.email cho forgot/login | Feasible, cần đo | server.js:35,70 tìm email; database.js:48-60 khai báo email TEXT không index/unique. EXPLAIN QUERY PLAN và A/B cùng DB cardinality trước kết luận; unique index có thể thay hành vi nên cần rà duplicates. |
| SQLite WAL | Feasible có điều kiện, chưa chứng minh bottleneck | DB hiện PRAGMA journal_mode=delete (db-state). WAL có thể thay cạnh tranh reader/writer, vẫn một writer; cần thử riêng, không sửa SUT trong bài đo gốc. |
| Tăng SQL connection pool như PostgreSQL để mở rộng nhiều writer | Hallucinated nếu áp nguyên xi | database.js:5 tạo một sqlite3.Database, không có pool SQL server; SQLite không có nhiều writer đồng thời chỉ nhờ pool. |
| Tối ưu password hashing để giải thích CPU auth hiện tại | Hallucinated cho bản SUT này | server.js:46 so sánh plaintext; register insert trực tiếp. Có lỗi bảo mật, chưa có hashing cost để tối ưu; thêm hash đúng đắn sẽ đổi baseline. |
| Tránh seed/drop lúc mỗi startup | Feasible về vận hành test | database.js:117 init vô điều kiện; không tự sửa vì thay phiên bản SUT; dùng runtime/DB riêng trong đợt đo hiện tại. |

Các giả thuyết trên không phải kết luận nguyên nhân latency. Bổ sung kết quả chính thức và đối chiếu phase sau khi có đủ raw.
