# 23120330 - HW05-AI M5 submission workspace

**Draft: chưa sẵn sàng nộp.** Chỉ hw05-m5 là Git repo mới; SUT archive gốc không có .git. Không có public remote, không push.

## Test summary

Workflow: Register (Auth-heavy) -> Forgot/Reset (Transactional) -> Login hỗ trợ -> GET Cart (Read-heavy). Human đã xác nhận GET Cart không trùng theo method+path.

| Scenario | Run ID | E2E | p95 E2E ms | Raw / HTML / view |
|---|---|---|---|---|
| Load | official-load-20261119-142516-6bca3e35 | 682 pass / 682 finalized | 62.00 | [raw](results/official-load-20261119-142516-6bca3e35/raw.json), [HTML](results/official-load-20261119-142516-6bca3e35/dashboard.html), [view](results/official-load-20261119-142516-6bca3e35/view.html) |
| Stress | official-stress-20261119-142841-f8a69e2c | 2864 pass / 2864 finalized | 100.00 | [raw](results/official-stress-20261119-142841-f8a69e2c/raw.json), [HTML](results/official-stress-20261119-142841-f8a69e2c/dashboard.html), [view](results/official-stress-20261119-142841-f8a69e2c/view.html) |
| Spike | official-spike-20261119-143230-4cb4886b | 1810 pass / 1810 finalized | 98.00 | [raw](results/official-spike-20261119-143230-4cb4886b/raw.json), [HTML](results/official-spike-20261119-143230-4cb4886b/dashboard.html), [view](results/official-spike-20261119-143230-4cb4886b/view.html) |
| Soak | soak-load-20261119-143548-37e75817 | 2858 pass / 2858 finalized | 67.00 | [raw](results/soak-load-20261119-143548-37e75817/raw.json), [HTML](results/soak-load-20261119-143548-37e75817/dashboard.html), [view](results/soak-load-20261119-143548-37e75817/view.html) |

Endurance đã thử: **5 VU / 10 phút**, 23.723 HTTP RPS trung bình wall, p95 E2E 67.00ms, HTTP/E2E lỗi0. Backend RSS peak 100.96MiB. Đây là mức đã kiểm chứng, **chưa xác định ngưỡng tối đa**.

Phát hiện đã xác minh:2 (OTP4 thay vì6 chữ số; login response chứa password field), draft trong [issue-drafts.md](docs/issue-drafts.md). GitHub Issues đã đăng:0. Không có issue hiệu năng đã chứng minh. Video Unlisted: **chờ người dùng cung cấp link thật**. Public GitHub: **chờ duyệt và link thật**.

## Tự chấm - chưa nhận điểm sinh viên

| Tiêu chí | Tối đa | Điểm tự chấm |
|---|---|---|
| Load | 30 | Chờ |
| Stress | 20 | Chờ |
| Spike | 20 | Chờ |
| AI analysis / hunt | 10 | Chờ |
| Continuous testing proposal | 10 | Chờ |
| Agent Skill | 10 | Chờ |
| Tổng | 100 | Chờ |

## Hồ sơ và cách chạy

- [Main report Markdown](docs/main-report.md) và [PDF draft](output/pdf/main-report.pdf).
- [API contract](docs/api-contract.md), [assertions/workload draft](docs/review-workload.md), [measured analysis](docs/measurement-results.md).
- [AI Audit Markdown](docs/ai-audit.md) và [PDF draft](output/pdf/ai-audit.pdf); actual outputs trong docs/audit; transcript đầy đủ còn thiếu.
- [AI Critique 248 words](docs/ai-critique.md) và [PDF draft](output/pdf/ai-critique.pdf), chưa được human duyệt.
- Ba testplans đúng tên trong plans/; workflow.js dùng chung. CSV private trong data/; generator scripts/new-data.py và schema data/README.md có thể công khai sau review. Không commit mật khẩu test.
- [PowerShell commands/evidence/video7phút](docs/evidence-and-video.md). Runtime/backend là bản sao test riêng, không khởi động backend gốc do module DB tự DROP/seed.
- [Pipeline proposal với flowchart](docs/pipeline-proposal.md), có hình vector trong PDF chính.
- [Reusable SKILL.md](skills/k6-workflow-audit/SKILL.md); skill replay thực tế skill-demo-load-20261119-144618-45deee1a đã pass5/5E2E, video05:00-06:30 mới là lịch dự kiến.
- [Git commit log](git-commit-log.txt). Chỉ commit file M5; dữ liệu/results/runtime không đưa vào Git public candidate.
- Hardware: [dxdiag screenshot thật](results/hardware/dxdiag-system.jpg), [CIM report](results/hardware/hardware.json). PHUC thực tế, chưa xác nhận khớp bài trước.

## Đối chiếu mục14 và những mục còn thiếu

| Yêu cầu | Trạng thái |
|---|---|
| Main/Audit/Critique MD+PDF | Có bản draft; cần review, Audit chưa có full transcript |
|3 JS + CSV|Có; CSV chứa mật khẩu synthetic giữ riêng tư, không public|
|3 raw logs|Có raw.json nguyên định dạng k6, từng mẫu; không đổi đuôi thành .jtl|
|3 HTML exports +3 views|Có; exports mở bằng Edge có đồ thị, views khác loại|
|Soak 10-15phút|Xem test summary và raw riêng; không gọi maximum|
|Ảnh tool+TaskManager mỗi run|**Thiếu**; quyền UI TaskManager chặn điều khiển agent|
|Hardware report/ảnh|Có; continuity hostname **chờ xác nhận**|
|YouTube Unlisted >=6phút giọng sinh viên|**Thiếu**; chỉ có kịch bản7phút|
|Public GitHub|**Thiếu**; chờ quyền push/public và URL thật|
|Git log/Skill/pipeline|Có, cập nhật log sau commit cuối|
|Bug report và Issue screenshots|Có2 draft;0Issue đã đăng, chưa có screenshotIssue|
|Điểm và ZIP đúng tên|**Chưa có điểm**; chưa tạo ZIP cuối|

K6 được đề cho phép nhưng checklist ZIP ghi .jtl. README này quy ước raw.json k6 là bằng chứng gốc theo mẫu tương ứng raw log; ba dashboard.html export tương ứng ba HTML report. Giữ đuôi file gốc. Chưa được cung cấp hướng dẫn Moodle riêng; **sinh viên cần kiểm tra quy ước nộp này**.

Sau review cập nhật submission-state.json bằng dữ liệu thật, rồi `./scripts/package.ps1 -SelfAssessedGrade <0..100>` tạo `23120330_HW05_AI_Performance_<000..100>.zip`. Script không push/upload/nộp. Không tạo ZIP cuối trước khi có điểm đã duyệt.
