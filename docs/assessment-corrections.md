# Đối chiếu đánh giá và đợt hoàn thiện bằng chứng

Ngày: 2026-11-19, Asia/Ho_Chi_Minh. Nguồn là đề gốc trong workspace và file yêu cầu/đánh giá được người dùng đính kèm. Đánh giá có tiêu đề tự đánh giá không tự trở thành human review hoặc điểm đã duyệt.

| Nhận định | Đối chiếu đề gốc | Xử lý |
|---|---|---|
| Task 3 chưa triển khai CI | Mục 6 Task 3 yêu cầu **propose**, flowchart và trade-offs; không bắt buộc implementation | Không triển khai CI để bù một yêu cầu không có trong đề |
| Chỉ có hai misinterpretation | Task 2 không quy định số lượng tối thiểu; cần lỗi thật, giá trị đúng và raw source | Giữ hai trường hợp đã có; không tạo thêm lỗi giả |
| Stress đều pass nên đã tìm maximum | Chưa có bậc vượt guardrail; throughput còn tăng | Giữ kết luận chưa xác định giới hạn, không đổi threshold sau run để tạo failure |
| Soak 5 VU là maximum | Một mức 5 VU/10 phút chỉ chứng minh mức đó | Giữ số đo thực tế và giới hạn bằng chứng; không tự đổi thành ngưỡng tối đa |
| Ảnh tool + resource cùng khung | Task 1 mục 6 và checklist mục 14 yêu cầu ảnh; mục 11 yêu cầu bằng chứng thật và video cùng khung | Phải chụp khi run thực sự đang chạy; không ghép ảnh riêng hoặc gắn ảnh mới cho raw cũ |
| Điểm 63-79 hay 75-85 | Đó là khoảng ước tính trong tài liệu đánh giá, chưa có điểm cụ thể được người dùng duyệt | Không điền điểm hay tạo ZIP tên điểm |
| Hai draft Issue là hai Issue đã đăng | Draft không phải bài đăng, chưa có URL hay ảnh Issue | Giữ 0 Issue đã đăng; chờ duyệt trước công khai |
| Raw JSON phải đổi đuôi sang .jtl | Đề cho phép k6 nhưng checklist dùng tên JMeter | Giữ JSON gốc; quy ước Moodle vẫn cần người dùng kiểm tra |

## Những việc thực sự đã làm trong đợt tiếp tục

- Đã đọc lại đề, hướng dẫn, Git status/log, README, submission-state và báo cáo. Working tree sạch trước sửa.
- Cổng 3000 trống khi chuẩn bị; tạo runtime mới tại runtime/evidence-20261119-1511/backend, sao nguyên bốn file nguồn/package. Dùng NODE_PATH tới dependencies đã cài từ lockfile; không cài lại trong lượt đo.
- Backend mới PID 32692. DB mới seed 2 tài khoản; không khởi động lại hay DROP DB test cũ. Hash DB SUT gốc vẫn C63F00544180BA1FBB1427A9B9DD3F1784842698809972F33CE90482E7420BA6.
- Smoke mới smoke-load-20261119-151305-4910eb8a: 5/5 E2E, exit 0. Metric m5_scenario_start_epoch_ms ghi trực tiếp scenario.startTime. Commit c673a8b thêm clock/provenance và tham số runtime riêng; không sửa handler/business assertions.
- Task Manager vẫn higher integrity so với helper; người dùng đã gửi ảnh chọn đúng PID 32692. Ảnh đó chỉ có Task Manager, chưa phải ảnh cho Load/Stress/Spike.
- Người dùng gửi ảnh ERR_CONNECTION_REFUSED tại 127.0.0.1:5665. Kiểm tra cổng xác nhận backend 3000 đang chạy nhưng chưa có dashboard 5665. Bật Load rerun; dashboard đã trả HTTP 200. Không thay firewall hay chính sách quyền.
- Bắt đầu rerun-load-20261119-162216-d7ab78da lúc 16:22; raw mới, CSV namespace mới, cùng profile Load. Chưa tự coi ảnh hỗ trợ là ảnh đã hoàn tất cho run này.

Ảnh do người dùng cung cấp được sao byte nguyên vẹn vào results/evidence-support; file yêu cầu/đánh giá được giữ trong docs/audit/20261119-user-followup-and-assessment.txt. Thời điểm import file không được nhận là thời điểm chụp hoặc thời điểm gửi prompt. Còn cần ảnh cùng khung khi run hoạt động, human review, hostname continuity, transcript đầy đủ, video/giọng thật, URL công khai và điểm tự chấm.
