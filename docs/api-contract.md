# M5 API contract - review draft

MSSV 23120330. Ngày 2026-11-19, Asia/Ho_Chi_Minh. Đã đọc đề, README, setup_guide và thử Git status trước sửa. Không tìm thấy AGENTS.md ở workspace/các thư mục cha đã kiểm tra. Input là archive, không có `.git`, nên **chưa xác định được commit SUT**. Không suy ra commit từ GitHub HEAD. SUT tham chiếu: https://github.com/ttbhanh/eshop-sut.

Nguồn dòng dưới đây tương đối với thư mục SUT gốc (ngoài hw05-m5). Bản runtime sao nguyên server.js/database.js, không sửa handler. SHA256:

- server.js: `47573CE5A6BF9A894748D2BB56CC8D1659AD7ACD033FDD6DB6B3E4D9473EB487`
- database.js: `3366420632BB9C982905B22E3969F69515E39E7A37A4F84EBA56EAD7E94AFED8`
- DB gốc trước/sau smoke: `C63F00544180BA1FBB1427A9B9DD3F1784842698809972F33CE90482E7420BA6` (không đổi).

| Vai trò | Method/path | Payload / header | Thành công và correlation | Nguồn |
|---|---|---|---|---|
| Auth-heavy | POST /api/register | name,email,password từ CSV | 200; message chính xác; id nguyên dương, giữ id để so login | api_specification.md:12-21; backend/server.js:20-30 |
| Transactional, bước 1 | POST /api/forgot-password | email của cùng dòng | 200; resetToken chuỗi số, giữ trong bộ nhớ iteration | api_specification.md:35-42; backend/server.js:68-85 |
| Transactional, bước 2 | POST /api/reset-password | email, resetToken vừa nhận, newPassword từ cùng dòng | Runtime 200; message Password reset successfully; ghi DB, xóa reset_token | api_specification.md:45-55 không nêu status; backend/server.js:87-98 |
| Hỗ trợ xác thực | POST /api/login | email, password=newPassword | 200; token 3 phần; user.id=id register và user.email=email CSV | api_specification.md:24-32; backend/server.js:32-66 |
| Read-heavy | GET /api/cart | Authorization: Bearer token login vừa nhận | 200; JSON array có length=0 | api_specification.md:112-115 yêu cầu JWT; backend/server.js:100-110,284-288; results/contract-probe.json |

Forgot/reset tạo và cập nhật trạng thái tài khoản; đây là nhóm transactional của workflow đã được người dùng chỉ định. Không thêm cart write/checkout để thay đổi phạm vi. Login là hỗ trợ, register là đại diện Auth-heavy.

## Runtime confirmation

Probe lúc 2026-11-19 14:15:32 +07:00: năm status 200, resetToken string dài 4 ký tự số, JWT có 3 phần, identity_matches=true, giỏ `[]`. Chỉ lưu metadata an toàn trong results/contract-probe.json. Không assert độ dài 6 cho bài performance vì runtime hiện sinh 4; đây là sai khác cần báo riêng so README FR-03/SEC-07. Login response chứa trường password; không log response body.

## Scope and review

Đối chiếu theo bảng người dùng cung cấp: M4 GET /api/users/me; M1/M2 POST /api/cart. Repo chỉ có backend/test_profile.js là test profile, không có script k6 hay bảng phân công nhóm. **Chưa xác nhận M1/M2 có GET /api/cart hoặc quy tắc trùng bỏ qua method.** Giữ GET /api/cart cho tới khi có phản hồi thật. Nếu trùng, trao đổi M1 trước khi đổi GET /api/products/:id; đó là đọc công khai theo api_specification.md:87 và backend/server.js:164, login vẫn chứng minh mật khẩu mới. Không tự đổi.

Human review đã nhận trong chat: “Giữ GET /api/cart; không trùng theo method+path”. Phần assertion và workload chưa có phản hồi cụ thể; các nhận xét kỹ thuật trong hồ sơ là agent tự kiểm tra.

## Safe startup

Không chạy node database.js hay node server.js trong backend gốc: database.js:15-20 DROP bảng; initDatabase() được gọi vô điều kiện tại dòng 117. Tạo runtime/backend bằng bản sao bốn file server.js,database.js,package.json,package-lock.json, không sao DB. Cài `npm ci --prefix ./hw05-m5/runtime/backend --no-audit --no-fund`, rồi `Set-Location ./hw05-m5/runtime/backend; node server.js`. Backend hardcode cổng 3000 (server.js:8), không có PORT env. Không khởi động nếu cổng đang dùng. Chờ seed hoàn tất trước smoke; mỗi restart DB test riêng được seed lại. Không restart khi đang có run.
