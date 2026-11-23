# Hướng dẫn và Nội dung đăng GitHub Issues

Repository đích: [https://github.com/luc1fe4/eshop-sut-hw05](https://github.com/luc1fe4/eshop-sut-hw05)

---

## Issue 1

- **Title:** `[BUG_FR03] Forgot-password reset token has 4 digits instead of 6 digits`
- **Labels:** `bug`, `backend`

### Body (Sao chép đoạn dưới vào ô description):
```markdown
### Summary
The `POST /api/forgot-password` endpoint generates a 4-digit reset token/OTP instead of the required 6-digit random token specified in the requirements.

### Environment
- SUT: EShop Backend (Node.js Express + SQLite3)
- OS: Windows 11 Home 64-bit

### Steps to Reproduce
1. Start the backend service (`node server.js` on port 3000).
2. Register a new user:
   `POST /api/register` with JSON `{"name":"Test User","email":"test_otp@example.invalid","password":"Password123!"}`
3. Request password reset:
   `POST /api/forgot-password` with JSON `{"email":"test_otp@example.invalid"}`
4. Observe the returned `resetToken` in the response JSON.

### Expected Behavior
According to SRS/README FR-03 and `api_specification.md` (line 42), the `resetToken` must be a 6-digit random numeric string (e.g. `"123456"`).

### Actual Behavior
The endpoint returns a 4-digit string (e.g. `"4829"`). 
Source code in `backend/server.js:72`:
```javascript
const resetToken = Math.floor(1000 + Math.random() * 9000).toString();
```
This formula only produces integers between 1000 and 9999 (4 digits).

### Impact & Severity
- Severity: Medium
- Impact: 4-digit numeric OTP has only 10,000 combinations, making it susceptible to brute-force attacks if rate limiting is absent.
```

---

## Issue 2

- **Title:** `[SEC_FR02] POST /api/login response leaks password field in user object`
- **Labels:** `bug`, `security`

### Body (Sao chép đoạn dưới vào ô description):
```markdown
### Summary
The `POST /api/login` endpoint returns the full user database record in the response payload, including the plaintext `password` field.

### Environment
- SUT: EShop Backend (Node.js Express + SQLite3)
- OS: Windows 11 Home 64-bit

### Steps to Reproduce
1. Start the backend service (`node server.js` on port 3000).
2. Authenticate with a valid account:
   `POST /api/login` with JSON `{"email":"test_otp@example.invalid","password":"Password123!"}`
3. Inspect the JSON response body.

### Expected Behavior
Per SEC-01 security requirements and secure authentication best practices, sensitive credentials like `password` must never be exposed or returned in API response bodies.

### Actual Behavior
The response body contains:
```json
{
  "token": "eyJhbGciOi...",
  "user": {
    "id": 1,
    "name": "Test User",
    "email": "test_otp@example.invalid",
    "password": "Password123!",
    "role": "customer"
  }
}
```
Source code in `backend/server.js:35, 52`:
```javascript
db.get('SELECT * FROM users WHERE email = ?', [email], (err, user) => { ...
  res.json({ token, user: { id: user.id, name: user.name, email: user.email, password: user.password, role: user.role } });
});
```

### Impact & Severity
- Severity: High
- Impact: Credential disclosure vulnerability. Clients/frontends caching or logging the user object inadvertently leak the plaintext password.
```

---

## Sau khi tạo 2 Issue trên GitHub:
1. Mở trang danh sách Issues: `https://github.com/luc1fe4/eshop-sut-hw05/issues`
2. Chụp ảnh màn hình hiển thị cả 2 Issue (có URL và tên repo rõ ràng).
3. Lưu ảnh vào thư mục: `hw05-m5/docs/screenshots/github-issues.png` (hoặc gửi ảnh vào chat).
