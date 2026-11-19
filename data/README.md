CSV được sinh riêng mỗi run bằng scripts/new-data.py, không commit mật khẩu.
Schema: name,email,password,newPassword. Chỉ dữ liệu tổng hợp, email thuộc example.invalid.
CSV gốc chứa mật khẩu test nên giữ local. Bản public chỉ có schema và generator;
khi đóng gói cần rà soát yêu cầu CSV với giảng viên, không đưa secret vào repo công khai.
