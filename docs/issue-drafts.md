# GitHub Issue drafts - chưa đăng, chờ duyệt

Đã xác minh **2 phát hiện chức năng/bảo mật trong phạm vi M5** bằng probe và mã nguồn. **0 GitHub Issues đã đăng**, chưa có link/ảnh Issue. Không có issue hiệu năng đã xác minh ở thời điểm viết draft này. Không biến lỗi socket sandbox thành bug SUT.

## Draft 1: Forgot-password reset token has four digits rather than required six

Environment: Windows PHUC, Node 22.17.1; SUT archive không có commit, source hashes trong api-contract.md. Backend bản sao không sửa handler, DB test riêng.

Reproduction: khởi động runtime test; chạy `node scripts/contract-probe.cjs results/contract-probe.json` từ hw05-m5. Script tạo một tài khoản synthetic, gọi Register -> Forgot -> Reset -> Login -> GET Cart. Không in credentials/token. Xem metadata reset_token.length.

Expected: README FR-03 quy định OTP 6 chữ số ngẫu nhiên; api_specification.md:42 minh họa resetToken 6 chữ số.

Actual: runtime trả token string dài 4, digits_only=true; server.js:72 dùng Math.floor(1000 + Math.random()*9000). Token giá trị thật không đính kèm. Workflow khôi phục vẫn thành công; performance assertion giữ correlation, báo sai khác contract riêng.

Evidence: results/contract-probe.json, scripts/contract-probe.cjs, backend/server.js:72, smoke raw/summary xác minh luồng. Còn thiếu ảnh reproduction đã redaction; raw metrics không tự chứng minh chiều dài response, phải dùng probe metadata.

## Draft 2: Login response exposes a password field in user object

Same environment and reproduction. Sau login bằng mật khẩu mới, probe chỉ ghi `login_response_contains_password_field=true`, không ghi giá trị.

Expected: API không trả password trong user profile/auth response; README SEC-01 yêu cầu không lưu plaintext. Một trường có tên password chưa đủ độc lập chứng minh giá trị trả ra là plaintext, cần kết hợp mã nguồn hoặc boolean equality probe nếu cần xác minh mạnh hơn.

Actual: server.js SELECT * users, so plaintext và trả nguyên user trong JSON; database.js schema password TEXT và đăng ký ghi input trực tiếp. Probe xác nhận trường có mặt. Không sao response body hay đưa mật khẩu vào ảnh/Issue.

Evidence: results/contract-probe.json metadata; backend/server.js:35,46,52; schema database.js:48-60. Chưa có screenshot an toàn. Đề xuất sửa response DTO bỏ password/reset_token và hashing mật khẩu trong một thay đổi riêng, sau đó tạo baseline mới vì cost auth đổi.

Chỉ đăng sau khi sinh viên duyệt nội dung và repository đích. Không có link Issue giả.
