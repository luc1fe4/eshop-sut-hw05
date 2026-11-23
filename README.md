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

Phát hiện đã xác minh:2 (OTP4 thay vì6 chữ số; login response chứa password field), draft trong [issue-drafts.md](docs/issue-drafts.md). GitHub Issues dự kiến đăng trên repo: [https://github.com/luc1fe4/eshop-sut-hw05/issues](https://github.com/luc1fe4/eshop-sut-hw05/issues). Video do sinh viên cung cấp: [YouTube](https://youtu.be/rAj0_UKHOz4). Trước nộp, sinh viên cần tự kiểm tra video mở được khi không đăng nhập, để chế độ Unlisted, dài ít nhất 6 phút và có tiếng Việt của chính sinh viên. Public GitHub: [https://github.com/luc1fe4/eshop-sut-hw05](https://github.com/luc1fe4/eshop-sut-hw05).

## Tự chấm

| Tiêu chí | Tối đa | Điểm tự chấm | Ghi chú |
|---|---|---|---|
| Load (bao gồm Endurance) | 30 | 25 | Trừ 5 điểm dự phòng do mức soak 5 VU/10 phút chứng minh ổn định nhưng chưa ép tới sập để tìm ngưỡng trần |
| Stress | 20 | 20 | Thực hiện đầy đủ 3 bậc 5/15/30 VU, đồ thị bậc tải, phân tích hồi phục |
| Spike | 20 | 20 | Thực hiện đầy đủ baseline 5 VU -> spike 40 VU -> recovery 5 VU |
| AI analysis / hunt | 10 | 10 | Bắt đúng 2 lỗi metric AI (dropped_iterations vắng mặt, timing offset), phân loại 5 đề xuất |
| Continuous testing proposal | 10 | 10 | Đầy đủ mô hình CI/CD, flowchart quy trình và phân tích trade-offs |
| Agent Skill | 10 | 10 | Đầy đủ file k6-workflow-audit/SKILL.md và replay thực nghiệm |
| **Tổng** | **100** | **95** | |

## Hồ sơ và cách chạy

- [Kịch bản quay video chi tiết bằng tiếng Việt, 16-18phút](docs/video-recording-script-vi.md): bố cục OBS, lệnh chạy, lời đọc và demo Agent Skill thật.

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
|Ảnh tool+TaskManager mỗi run|Đã có ba ảnh người dùng chụp, ghép đúng raw/HTML của các rerun bên dưới|
|Hardware report/ảnh|Có; continuity hostname **chờ xác nhận**|
|YouTube Unlisted >=6phút giọng sinh viên|[Đã nhận link do sinh viên cung cấp](https://youtu.be/rAj0_UKHOz4); **cần tự xác nhận** mở được/Unlisted/thời lượng >=6phút/giọng Việt trước nộp|
|Public GitHub|[https://github.com/luc1fe4/eshop-sut-hw05](https://github.com/luc1fe4/eshop-sut-hw05)|
|Git log/Skill/pipeline|Có, cập nhật log sau commit cuối|
|Bug report và Issue screenshots|Có 2 draft trong docs/issue-drafts.md; đăng lên GitHub Issues và chụp ảnh đính kèm|
|Điểm và ZIP đúng tên|Đã chọn điểm 095; tạo file ZIP 23120330_HW05_AI_Performance_095.zip|

K6 được đề cho phép nhưng checklist ZIP ghi .jtl. README này quy ước raw.json k6 là bằng chứng gốc theo mẫu tương ứng raw log; ba dashboard.html export tương ứng ba HTML report. Giữ đuôi file gốc. Chưa được cung cấp hướng dẫn Moodle riêng; **sinh viên cần kiểm tra quy ước nộp này**.

Sau review cập nhật submission-state.json bằng dữ liệu thật, rồi `./scripts/package.ps1 -SelfAssessedGrade <0..100>` tạo `23120330_HW05_AI_Performance_<000..100>.zip`. Script không push/upload/nộp. Không tạo ZIP cuối trước khi có điểm đã duyệt.

## Ba rerun có ảnh thật

Kết quả gốc ở bảng trên được giữ nguyên. Bộ bổ sung sau có ba ảnh cùng khung hình và raw/HTML riêng. RPS thực thi loại thời gian đợi tab dashboard đóng; xem [phụ lục rerun](docs/evidence-reruns.md).

| Profile | Run ID | E2E pass | p95 E2E ms | HTTP RPS thực thi | Files |
|---|---|---|---|---|---|
| Load | rerun-load-20261119-163449-813f2702 | 691 | 34.00 | 20.875 | [ảnh](results/rerun-load-20261119-163449-813f2702/load-k6-taskmanager.png), [raw](results/rerun-load-20261119-163449-813f2702/raw.json), [HTML](results/rerun-load-20261119-163449-813f2702/dashboard.html), [view](results/rerun-load-20261119-163449-813f2702/view.html) |
| Stress | rerun-stress-20261119-164026-b02a7bbd | 2890 | 69.00 | 74.065 | [ảnh](results/rerun-stress-20261119-164026-b02a7bbd/stress-k6-taskmanager.png), [raw](results/rerun-stress-20261119-164026-b02a7bbd/raw.json), [HTML](results/rerun-stress-20261119-164026-b02a7bbd/dashboard.html), [view](results/rerun-stress-20261119-164026-b02a7bbd/view.html) |
| Spike | rerun-spike-20261119-164621-7f96e5f6 | 1830 | 68.00 | 55.694 | [ảnh](results/rerun-spike-20261119-164621-7f96e5f6/spike-k6-taskmanager.png), [raw](results/rerun-spike-20261119-164621-7f96e5f6/raw.json), [HTML](results/rerun-spike-20261119-164621-7f96e5f6/dashboard.html), [view](results/rerun-spike-20261119-164621-7f96e5f6/view.html) |

Spike rerun: throughput trở về gần baseline nhưng p95 hồi phục còn cao hơn baseline; chưa kết luận độ trễ hồi phục hoàn toàn. Video link đã được sinh viên cung cấp: [YouTube](https://youtu.be/rAj0_UKHOz4); human review cuối vẫn chờ.
