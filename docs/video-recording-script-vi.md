# Kịch bản quay video HW05-AI M5 - MSSV 23120330

Soạn ngày 2026-11-19, múi giờ Asia/Ho_Chi_Minh. Đây là hướng dẫn và lời dẫn dự kiến, chưa phải transcript hay video đã quay. Người dùng tự thao tác, tự thu giọng tiếng Việt và cung cấp URL thật.

**Cách dùng:** đọc phần chuẩn bị trước; khi quay, lần lượt làm phần “Thao tác” và nói phần “Lời đọc”. Các mốc video là dự kiến, có thể dài hơn khi chờ agent hoặc đổi cửa sổ. Bản này khoảng16-18phút, vượt yêu cầu tối thiểu6phút. Không cần nói liên tục trong toàn bộ thời gian chạy tải.

## 1. Chuẩn bị trước khi bấm quay

### 1.1. Dựng đúng khung hình

Giữ bố cục đã dùng để chụp ảnh: Chrome/dashboard hoặc PowerShell ở bên trái; Task Manager ở bên phải. Trong Task Manager chọn Details, chọn đúng node.exe của backend và để thấy PID, CPU, Memory. Có thể dùng thao tác chia đôi cửa sổ của Windows. Tăng cỡ chữ nếu video thử không đọc được số.

PID32692 là PID ở đợt chụp ảnh vừa rồi, **phải kiểm tra lại khi quay**. Nếu backend đã khởi động lại, chọn PID mới; không đọc lại32692 theo trí nhớ.

Đóng cửa sổ chat cá nhân, không mở CSV có mật khẩu hoặc response Register/Forgot/Login. Chỉ quay code, metric JSON, summary, biểu đồ và các file đã rà soát. Không mở .env, JWT, resetToken hoặc password thật.

### 1.2. Thiết lập OBS Studio

1. Mở OBS; tạo Scene tên `HW05_23120330`.
2. Trong Sources thêm **Display Capture** và chọn màn hình có cả hai cửa sổ. Window Capture chỉ chọn Chrome sẽ không quay được Task Manager bên cạnh.
3. Kiểm tra Mic/Aux đúng micro; nói thử và xem mức âm thanh thay đổi. Tắt Desktop Audio nếu không cần âm thanh máy.
4. Đề xuất30fps; giữ cùng tỉ lệ màn hình để không cắt mất PID/Memory. Ưu tiên chữ rõ, kiểm tra bằng đoạn quay thử.
5. Chọn thư mục lưu riêng, ví dụ `hw05-m5/results/video`. Có thể quay MKV rồi dùng **File -> Remux Recordings** sang MP4 sau khi dừng.
6. Quay thử10-15giây, mở file nghe lại giọng và kiểm tra chữ. Khi ổn mới bấm **Start Recording** cho bài chính. Không bấm Start Streaming.

OBS và việc thu âm cũng dùng tài nguyên máy. Nói rõ các lượt quay mới chạy cùng OBS; không yêu cầu số đo giống hệt lượt trước. Không render PDF hoặc cài dependency trong lúc chạy tải.

Nguồn thao tác: [OBS Quick Start](https://obsproject.com/kb/quick-start-guide/), [OBS Recording Output](https://obsproject.com/kb/standard-recording-output-guide/).

### 1.3. Chuẩn bị PowerShell B - cửa sổ chạy k6

Mở PowerShell tại repo, chạy đoạn sau trước khi quay:

```powershell
$M5Root = 'D:\Regular_School\N4\HK1\Testing\HW04\eshop-sut-main'
Set-Location -LiteralPath $M5Root
$M5BackendDir = Join-Path $M5Root 'hw05-m5\runtime\evidence-20261119-1511\backend'

$M5Listeners = @(Get-NetTCPConnection -State Listen -LocalPort 3000 -ErrorAction SilentlyContinue)
$M5BackendOwners = @($M5Listeners.OwningProcess | Sort-Object -Unique)
if ($M5BackendOwners.Count -ne 1) {
    throw 'Chưa xác định được backend trên cổng 3000. Xem mục 1.4 trước khi quay.'
}
$M5BackendPid = [int]$M5BackendOwners[0]
Get-CimInstance Win32_Process -Filter "ProcessId=$M5BackendPid" |
    Select-Object ProcessId, ExecutablePath, CommandLine
Write-Host "Backend PID cần chọn trong Task Manager: $M5BackendPid"

k6 version
node --version
python --version
hostname
Get-NetTCPConnection -State Listen -LocalPort 5665 -ErrorAction SilentlyContinue
```

Xác nhận backend đúng phiên test riêng. Nếu cổng3000 do tiến trình khác chiếm hoặc không chắc runtime của nó, dừng chuẩn bị và nhờ agent kiểm tra; không tự kill tiến trình theo tên node.

Nếu5665 còn listener, đóng các tab dashboard cũ trong Chrome và cả tab xem trước trong ứng dụng. Chỉ bắt đầu lượt tiếp khi lệnh k6 trước đã trả về PowerShell. Không tắt firewall để sửa lỗi dashboard.

**Khi mở dashboard:** tự gõ `http://127.0.0.1:5665` vào Chrome sau khi CLI đã hiện địa chỉ dashboard. Chỉ giữ một tab live. Tránh bấm link localhost trong chat vì có thể mở thêm in-app preview giữ kết nối sau khi Chrome đóng.

### 1.4. Chỉ dùng nếu backend đã dừng

Không chạy backend gốc: database.js có DROP/seed khi import. Để giữ cả DB test cũ, mở **PowerShell A** và tạo runtime mới:

```powershell
$M5Root = 'D:\Regular_School\N4\HK1\Testing\HW04\eshop-sut-main'
Set-Location -LiteralPath $M5Root
if (Get-NetTCPConnection -State Listen -LocalPort 3000 -ErrorAction SilentlyContinue) {
    throw 'Cổng 3000 đang được dùng; không khởi động backend thứ hai.'
}
$M5VideoStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$M5BackendDir = Join-Path $M5Root "hw05-m5\runtime\video-$M5VideoStamp\backend"
New-Item -ItemType Directory -Path $M5BackendDir | Out-Null
Copy-Item -LiteralPath '.\backend\server.js','.\backend\database.js',
    '.\backend\package.json','.\backend\package-lock.json' -Destination $M5BackendDir
$env:NODE_PATH = Join-Path $M5Root 'hw05-m5\runtime\backend\node_modules'
Write-Host "Đường dẫn cần dùng ở PowerShell B: $M5BackendDir"
Set-Location -LiteralPath $M5BackendDir
node server.js
```

Để cửa sổ A chạy. Chờ thông báo server/DB seed hoàn tất. Ở cửa sổ B, thay `$M5BackendDir` bằng đúng đường dẫn vừa in, rồi chạy lại phần xác định PID của mục1.3. Không sao DB cũ sang runtime mới và không restart backend giữa các scenario.

### 1.5. Chuẩn bị sẵn các file để chuyển nhanh

Mở bằng editor hoặc File Explorer, chưa cần đưa tất cả lên hình cùng lúc:

- `hw05-m5/docs/api-contract.md` và `plans/workflow.js`.
- Ba test plan Load/Stress/Spike trong `hw05-m5/plans`.
- `hw05-m5/skills/k6-workflow-audit/SKILL.md`.
- `hw05-m5/docs/evidence-reruns.md`, `ai-audit.md`, `pipeline-proposal.md`.
- `hw05-m5/results/hardware/dxdiag-system.jpg`.
- Soak cũ: `hw05-m5/results/soak-load-20261119-143548-37e75817/view.html` và `soak-windows.png`.

Video có ba lượt chạy mới. Những số691/2890/1830 và34/69/68ms là **kết quả rerun đã có ngày19/11**, không phải số bắt buộc phải xuất hiện ở lượt quay mới.

## 2. Lịch quay dự kiến

| Video | Nội dung | Màn hình chính |
|---|---|---|
| 00:00-00:45 | Giới thiệu, phần cứng | dxdiag, phiên bản công cụ |
| 00:45-01:30 | Contract, CSV, correlation | Contract/workflow code |
| 01:30-04:30 | Load chạy trọn profile | k6 + Task Manager cùng khung |
| 04:30-08:00 | Stress chạy trọn profile | k6 + Task Manager cùng khung |
| 08:00-11:00 | Spike chạy trọn profile | k6 + Task Manager cùng khung |
| 11:00-11:50 | Soak từ bằng chứng đã có | View/timeline soak |
| 11:50-14:00 | Agent Skill áp dụng thật | Codex/tool output + Task Manager |
| 14:00-15:15 | Raw log, p95, AI audit | Verification + AI Audit |
| 15:15-16:15 | Pipeline, kết luận | Flowchart + README |

Mốc video không phải timestamp của run. Nếu agent phản hồi lâu, cứ quay dài hơn; ghi lại chapter time thật sau khi có MP4. Không mặc định demo skill vẫn nằm ở05:00 như kịch bản7phút cũ.

## 3. Kịch bản lời đọc và thao tác chi tiết

### Đoạn A - 00:00-00:45: giới thiệu và máy đo

**Thao tác:** bấm Start Recording; mở ảnh dxdiag hoặc dxdiag thật. Sau đó chuyển PowerShell hiện `hostname`, `k6 version`, `node --version`.

**Lời đọc:**

> Em chào thầy cô. Em là sinh viên có mã số23120330. Đây là video bài HW05-AI, kiểm thử hiệu năng workflow M5 của EShop bằng Grafana k6.
>
> Em thực hiện trên máy Windows có hostname PHUC, CPU Ryzen7 6800H, tám nhân và mười sáu luồng, RAM lắp đặt16GB. Backend, k6 và phần mềm quay cùng chạy trên máy này, nên em ghi nhận điều kiện đó khi đọc kết quả.
>
> Bản SUT đầu vào là archive không có thông tin Git commit. Em lưu hash mã nguồn và dùng backend sao chép với database test riêng để tránh ảnh hưởng dữ liệu có sẵn.

Chỉ bổ sung câu “hostname trùng bài trước” sau khi bạn đã kiểm tra được bằng chứng bài trước thật. Nếu chưa xác nhận, giữ lời đọc ở mức hostname hiện tại.

### Đoạn B - 00:45-01:30: phạm vi và dữ liệu

**Thao tác:** mở bảng API contract, rồi chỉ vào phần correlation trong workflow.js. Không mở CSV thực tế.

**Lời đọc:**

> M5 sử dụng cùng một luồng cho Load, Stress, Spike và Soak: đăng ký, quên mật khẩu, đặt lại mật khẩu, đăng nhập bằng mật khẩu mới, rồi xem giỏ hàng.
>
> Register đại diện nhóm Auth-heavy. Forgot và Reset tạo, cập nhật trạng thái khôi phục mật khẩu nên được chọn làm nhóm Transactional. GET Cart đại diện Read-heavy và dùng JWT vừa nhận sau Login.
>
> Dữ liệu tổng hợp được sinh thành CSV riêng cho mỗi run, nạp bằng SharedArray. Mỗi iteration lấy một dòng duy nhất bằng iterationInTest. Reset token luôn đi cùng email của iteration đó; mật khẩu mới dùng để Login; JWT chỉ giữ trong bộ nhớ để gọi Cart. Khi một bước lỗi, iteration dừng sớm nhưng vẫn ghi E2E failure.

Nếu muốn chỉ schema CSV, gõ dòng văn bản `name,email,password,newPassword` trong tài liệu hoặc mở data/README.md; không mở các dòng chứa mật khẩu.

### Đoạn C - 01:30-04:30: Load trực tiếp

**Thao tác ở PowerShell B:**

```powershell
& .\hw05-m5\scripts\run.ps1 -Profile Load -Kind rerun -Rows 20000 `
    -BackendPid $M5BackendPid -BackendDir $M5BackendDir -DashboardPort 5665
```

Khi CLI hiện `web dashboard: http://127.0.0.1:5665`, gõ địa chỉ đó vào Chrome. Đặt Chrome bên trái, Task Manager bên phải. Bắt đầu tính thời gian pha theo elapsed của k6, không theo lúc bạn mở tab.

| Elapsed workload | Điều gì đang chạy | Việc trên màn hình |
|---|---|---|
| 0-30s | Ramp0->5VU | Chỉ biểu đồ VU tăng, PID backend |
| 30-150s | Hold5VU | Giữ cùng khung; đọc request rate và CPU/Memory; có thể chụp ảnh |
| 150-165s | Ramp về0 | Chỉ tải giảm; đợi workload kết thúc |

**Lời đọc lúc bắt đầu:**

> Em bắt đầu một lượt Load mới. Wrapper tạo namespace và CSV mới, không dùng lại tài khoản của các lượt trước. Cấu hình tăng từ không lên năm VU trong ba mươi giây, giữ năm VU hai phút, sau đó hạ tải mười lăm giây. Think-time là một giây cuối iteration, timeout request là mười giây.

**Lời đọc trong vùng hold:**

> Bên trái là dashboard k6 đang cập nhật, bên phải là tiến trình backend với PID em đã đối chiếu ở cổng3000. Em theo dõi CPU và Memory của đúng tiến trình này.
>
> VU là mức đồng thời cấu hình. Request rate là tải thực tế mà máy đang tạo được. Các card trên dashboard là snapshot; throughput cả run phải tính với một cửa sổ thời gian rõ ràng. HTTP failure cũng được tách với kết quả nghiệp vụ E2E.

Không cần cố nói CPU phải cao. Nếu CPU hiển thị00, đọc “giá trị CPU đang được Task Manager làm tròn”, không đọc “backend không dùng CPU”. Không gọi Memory trên Task Manager là cùng chỉ số với RSS trong sampler.

**Khi workload đã về0:** đóng tab dashboard và các preview localhost còn mở; đợi PowerShell trả prompt. Sau đó nói:

> Lượt Load đã chạy hết cấu hình. Em giữ raw JSON từng mẫu, summary riêng, HTML dashboard và resource log trong thư mục run mới. Đây là lượt quay, không ghi đè lượt đo trước.

Nếu muốn đọc con số của lượt vừa quay, lấy từ summary của chính run đó theo mục4; không đọc lại691/34ms khi chưa kiểm tra.

### Đoạn D - 04:30-08:00: Stress trực tiếp

Chỉ chạy sau khi Load đã trả prompt và cổng5665 được giải phóng.

```powershell
& .\hw05-m5\scripts\run.ps1 -Profile Stress -Kind rerun -Rows 20000 `
    -BackendPid $M5BackendPid -BackendDir $M5BackendDir -DashboardPort 5665
```

Mở lại đúng một tab5665. Nếu dùng tab cũ còn mở, phải tải lại để không hiển thị dữ liệu Load cũ.

| Elapsed workload | Pha |
|---|---|
| 0-15s | Ramp lên5VU |
| 15-60s | Hold5VU |
| 60-75s | Ramp lên15VU |
| 75-120s | Hold15VU |
| 120-135s | Ramp lên30VU |
| 135-180s | Hold30VU |
| 180-195s | Hạ về0 |

**Lời đọc đầu run:**

> Stress giữ nguyên workflow, CSV correlation và assertions. Em tăng tải theo ba bậc năm, mười lăm và ba mươi VU. Mỗi bậc có khoảng ramp và khoảng giữ tải riêng để so sánh throughput, p95 và tỷ lệ lỗi.

**Lời đọc ở15VU:**

> Tải đã tăng sang bậc mười lăm VU. Em quan sát request rate thực tế cùng tài nguyên backend. Em không gộp cả ramp và hold rồi coi đó là kết quả riêng của một bậc tải.

**Lời đọc ở30VU, giữ nguyên hai cửa sổ:**

> Đây là bậc ba mươi VU. Em sẽ kiểm tra p95 và lỗi trong raw log sau khi chạy, thay vì chỉ đọc một card tại thời điểm chụp. Nếu các bậc vẫn pass, kết luận là chưa tìm được bậc vượt ngưỡng trong phạm vi đã thử, không phải đã tìm được công suất tối đa của hệ thống.

**Khi kết thúc:** đóng tab dashboard, chờ prompt; có thể cho thấy dòng iteration complete/interrupted. Chỉ đọc kết quả pass khi summary của lượt này xác nhận.

### Đoạn E - 08:00-11:00: Spike trực tiếp

```powershell
& .\hw05-m5\scripts\run.ps1 -Profile Spike -Kind rerun -Rows 20000 `
    -BackendPid $M5BackendPid -BackendDir $M5BackendDir -DashboardPort 5665
```

Mở dashboard5665 sau khi CLI báo địa chỉ. Giữ Task Manager cùng khung, không chuyển sang cửa sổ khác trong lúc lên đỉnh.

| Elapsed workload | Pha | Việc cần quay rõ |
|---|---|---|
| 0-15s | Ramp lên5VU | Tải nền hình thành |
| 15-60s | Baseline5VU | Request rate và CPU/Memory nền |
| 60-62s | Tăng nhanh lên40VU | Đường tải tăng dốc |
| 62-92s | Peak40VU | Giữ nguyên khung và chụp nếu cần |
| 92-94s | Hạ nhanh về5VU | Đường tải giảm |
| 94-154s | Recovery5VU | Cả request rate và latency sau đỉnh |
| 154-164s | Hạ về0 | Kết thúc |

**Lời đọc đầu run:**

> Spike bắt đầu với baseline năm VU, tăng lên bốn mươi VU trong hai giây, giữ ba mươi giây, rồi giảm về năm VU để quan sát hồi phục một phút.

**Lời đọc ở khoảng55s:**

> Em giữ nguyên khung hình. Sau đây tải sẽ tăng nhanh, đồng thời em theo dõi đúng tiến trình backend bên phải.

**Lời đọc trong peak:**

> Đây là vùng đỉnh bốn mươi VU. Request rate trên dashboard là số tại thời điểm hiện tại; kết quả peak sẽ được tổng hợp theo cửa sổ đo. Em tiếp tục ghi hình đến cả giai đoạn hạ tải và hồi phục.

**Lời đọc trong recovery:**

> Tải đã trở về năm VU. Để đánh giá hồi phục, em phải so cả throughput và độ trễ với baseline. Request rate trở về gần mức nền chưa đủ để khẳng định p95 đã hồi phục hoàn toàn.

**Khi kết thúc:** đóng tab dashboard, chờ prompt. Không dừng recording chỉ vì đã quay được đỉnh; giữ cả phần recovery. Max duration có thể cộng graceful stop, không phải thời gian workload thực tế.

### Đoạn F - 11:00-11:50: Soak đã có bằng chứng

**Thao tác:** mở `results/soak-load-20261119-143548-37e75817/view.html` hoặc `soak-windows.png`, rồi cho thấy raw/summary/resources.csv trong cùng thư mục. Đây là phần xem lại kết quả, không diễn là đang chạy soak trực tiếp.

**Lời đọc:**

> Phần này là kết quả soak đã chạy trước đó, có raw log đầy đủ. Em duy trì năm VU trong mười phút. Run hoàn tất hai nghìn tám trăm năm mươi tám E2E, với mười bốn nghìn hai trăm chín mươi HTTP request và không có lỗi HTTP hoặc nghiệp vụ.
>
> P95 E2E là sáu mươi bảy mili giây, không tính think-time. HTTP throughput theo cửa sổ wall được ghi nhận khoảng hai mươi ba phẩy bảy hai ba request mỗi giây; đỉnh RSS backend quan sát được khoảng một trăm phẩy chín sáu MiB.
>
> Đây là một mức ổn định đã kiểm chứng trên máy này, chưa phải ngưỡng tối đa. Em không kết luận memory leak hoặc bottleneck chỉ từ một đường RAM hay một lượt chạy.

### Đoạn G - 11:50-14:00: Agent Skill chạy thật trên đủ M5

**Thao tác:** mở SKILL.md, nói câu đầu, rồi chuyển Codex sang bên trái, giữ Task Manager bên phải. Mở cuộc chat đang làm bài và tự gửi prompt dưới đây. Giữ recording khi agent đọc skill, chạy smoke và kiểm tra raw. Không chỉ đọc tên skill rồi bỏ qua bước thực thi.

**Lời đọc trước khi gửi:**

> Em đã tạo một Agent Skill để tái sử dụng quy trình kiểm thử. Skill yêu cầu xác minh contract, tạo dữ liệu độc lập, smoke trước khi tải, thu raw evidence và audit phân tích AI. Em sẽ yêu cầu agent áp dụng thật ngay trên toàn bộ năm endpoint của M5.

**Prompt để tự gửi cho agent khi đang quay:**

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

Agent dùng port=-1 trong demo để không có tab dashboard giữ tiến trình. Mở phần command/tool output an toàn để thấy k6 chạy; giữ cùng Task Manager. Nếu cần, sau khi agent hoàn tất, chuyển sang PowerShell để mở summary/verification của đúng run agent vừa tạo. Không mở CSV hoặc auth response để “minh họa token”.

**Chỉ sau khi output thật xác nhận thành công, đọc:**

> Agent đã chạy một smoke mới với một VU và năm iteration. Em kiểm tra đủ cả Register, Forgot, Reset, Login bằng mật khẩu mới và GET Cart. Token được correlate trong cùng iteration, nên việc Login thành công xác minh mật khẩu mới; giỏ tài khoản mới được kiểm tra là mảng rỗng.
>
> Em xem kết quả E2E riêng với kết quả HTTP, rồi dùng script độc lập để đối chiếu p95 với summary k6. Đây là áp dụng skill trên toàn nhóm endpoint, không chỉ demo một request đơn lẻ.

Nếu run lỗi hoặc agent bị chặn, nêu đúng trạng thái và xử lý thật trước khi thu đoạn thành công. Không đọc đoạn thành công khi chưa có output xác nhận. Phần5/5 và25request chỉ đúng khi demo đi hết cả năm bước trong cả năm iteration.

### Đoạn H - 14:00-15:15: raw log và AI Audit

**Thao tác:** dùng các lệnh ở mục4 để phân tích run vừa quay hoặc mở verification của rerun đã có. Sau đó mở bảng misinterpretation trong ai-audit.md. Nói rõ bạn đang dùng run nào; nếu xem số đã có, mở evidence-reruns.md và đọc tên run.

**Lời đọc:**

> Raw JSON là dữ liệu từng mẫu của k6, còn summary là thống kê tổng hợp. Em giữ cả hai và không đổi đuôi JSON thành JTL. Quy ước nộp riêng trên Moodle vẫn cần đối chiếu hướng dẫn môn học.
>
> Em yêu cầu AI phân tích nhưng không chấp nhận số liệu chỉ vì AI trả lời. Script độc lập dùng Python statistics.quantiles để kiểm tra p95 theo endpoint và E2E, đồng thời tách mẫu số HTTP request khỏi số workflow thành công.
>
> Em ghi nhận hai sai sót thật. Thứ nhất, output ban đầu ghi dropped_iterations bằng không trong khi raw không có metric đó; cách ghi đúng phải phân biệt không quan sát với đo được không drop. Thứ hai, dùng iteration đầu làm mốc test bị lệch do ramp từ không VU. Các rerun mới đã ghi trực tiếp scenario.startTime.
>
> Với Spike rerun đã dùng để thu ảnh, throughput hồi phục gần baseline nhưng p95 E2E recovery là bảy mươi bảy mili giây, cao hơn baseline bốn mươi tám phẩy không năm mili giây. Vì vậy em chưa kết luận độ trễ hồi phục hoàn toàn, dù guardrail vẫn pass.

Hai số77 và48.05 ở trên thuộc **rerun-spike-20261119-164621-7f96e5f6**. Nếu đang trình bày run video mới, đọc số của run mới hoặc nói rõ chuyển sang bằng chứng đợt trước. Không mặc định run mới cũng có hai số này.

### Đoạn I - 15:15-16:15: pipeline và kết thúc

**Thao tác:** mở flowchart trong pipeline-proposal.md hoặc trang9 của main-report.pdf phiên bản hiện tại. Sau đó chuyển README/Git log.

**Lời đọc:**

> Cuối cùng, em đề xuất mô hình Continuous Performance Testing. Khi commit ảnh hưởng authentication, cart, database hoặc runtime, pipeline chuẩn bị runner và DB test riêng, kiểm tra contract, smoke rồi chạy profile phù hợp. Các thay đổi tài liệu có thể được bỏ qua có ghi lý do, trong khi nightly vẫn chạy kiểm tra định kỳ.
>
> Em đề xuất so p95 với baseline trong điều kiện tương đương và chỉ cảnh báo khi chênh lệch lặp lại qua các lượt chạy sạch. Ví dụ policy dự thảo là tăng cả trên hai mươi phần trăm và trên mười mili giây, xuất hiện ít nhất hai trong ba lượt. Các ngưỡng này cần hiệu chỉnh, không phải SLA đã được chứng minh.
>
> Trade-off là chi phí chạy, độ nhiễu do máy dùng chung và nguy cơ false alarm. Baseline không tự cập nhật sau một run lỗi; raw logs, cấu hình và resource metrics phải được lưu để truy vết. Đây là proposal theo yêu cầu đề, chưa phải CI đã triển khai.
>
> Bài của em sử dụng AI để thiết kế, chạy và phân tích, nhưng vẫn giữ bằng chứng thật và các giới hạn kết luận. Các file test plan, dữ liệu tổng hợp, báo cáo, audit và Git log được chuẩn bị trong hồ sơ. Em cảm ơn thầy cô.

Không nói “em đã duyệt tất cả output”, “repo đã public”, “Issue đã đăng” hoặc “hostname đã khớp bài trước” nếu các việc đó chưa thực sự hoàn tất.

## 4. Lệnh xem kết quả an toàn sau các lượt quay

Các lệnh sau chạy **sau khi cả ba profile đã kết thúc**, không render chart trong lúc Stress/Spike còn phát tải. Chọn thư mục mới nhất của từng profile, kiểm tra tên và manifest.start đúng lúc vừa quay trước khi dùng. Nếu một lệnh chạy thất bại, không tự lấy thư mục cũ thay cho lượt mới.

```powershell
$M5VideoLoad = (Get-ChildItem .\hw05-m5\results -Directory -Filter 'rerun-load-*' |
    Sort-Object Name -Descending | Select-Object -First 1).FullName
$M5VideoStress = (Get-ChildItem .\hw05-m5\results -Directory -Filter 'rerun-stress-*' |
    Sort-Object Name -Descending | Select-Object -First 1).FullName
$M5VideoSpike = (Get-ChildItem .\hw05-m5\results -Directory -Filter 'rerun-spike-*' |
    Sort-Object Name -Descending | Select-Object -First 1).FullName

foreach ($M5RunFolder in @($M5VideoLoad,$M5VideoStress,$M5VideoSpike)) {
    $M5RunManifest = Get-Content (Join-Path $M5RunFolder 'manifest.json') -Raw | ConvertFrom-Json
    if ($M5RunManifest.status -ne 'completed') { throw "Run chưa hoàn tất: $M5RunFolder" }
    Write-Host "Đang xử lý đúng run: $($M5RunManifest.run_id)"
    python .\hw05-m5\scripts\analyze.py $M5RunFolder
    python .\hw05-m5\scripts\verify-raw.py $M5RunFolder
    python .\hw05-m5\scripts\views.py $M5RunFolder
}
```

Đọc ba số cơ bản của Load mới:

```powershell
$M5LoadSummary = Get-Content (Join-Path $M5VideoLoad 'summary.json') -Raw | ConvertFrom-Json
$M5LoadSummary.metrics.m5_passed.values.count
$M5LoadSummary.metrics.http_req_failed.values.rate
$M5LoadSummary.metrics.m5_e2e_success_ms.values.'p(95)'
```

Mở ba view khác nhau bằng File Explorer: Load/view.html là bảng endpoint, Stress/view.html là chart theo bậc, Spike/view.html là timeline. Mở thêm verification.json để thấy `all_p95_match=true` nếu phép đối chiếu thực sự đạt. Metric files không chứa response auth; vẫn không mở CSV có password lên video.

Nếu xem lại bằng chứng đã có thay vì các lượt video mới, dùng đúng ba thư mục:

```text
rerun-load-20261119-163449-813f2702
rerun-stress-20261119-164026-b02a7bbd
rerun-spike-20261119-164621-7f96e5f6
```

| Bằng chứng có trước khi quay | E2E pass | HTTP n | E2E p95 | HTTP RPS thực thi |
|---|---:|---:|---:|---:|
| Load16:34 | 691 | 3455 | 34ms | 20.875 |
| Stress16:40 | 2890 | 14450 | 69ms | 74.065 |
| Spike16:46 | 1830 | 9150 | 68ms | 55.694 |

E2E p95 không chứa think-time. Bảng này không phải lời tiên đoán số liệu của run quay mới.

## 5. Xử lý trục trặc khi đang quay

| Hiện tượng | Cách làm đúng |
|---|---|
| Dashboard ERR_CONNECTION_REFUSED | Chờ CLI báo dashboard và xác nhận đúng cổng; backend3000 không tự mở dashboard5665. Không đổi firewall. |
| Biểu đồ vẫn là run trước | Tải lại đúng tab sau khi run mới bắt đầu. Kiểm tra trục thời gian hiện tại và profile. |
| K6 chạy hết nhưng chưa có summary | Đóng mọi tab live5665, kể cả in-app preview. Chờ prompt trở lại; không bấm Ctrl+C chỉ để tạo cảm giác đã hoàn tất. |
| Cổng5665 còn bận | Chưa chạy lượt tiếp trên cùng cổng; đóng preview cũ. Nếu agent dùng5666 để tiếp tục thì phải quay đúng URL5666 và ghi rõ trong run. |
| Task Manager PID thay đổi | Kiểm tra lại owner cổng3000; chọn PID mới, không chọn mọi node.exe. |
| CPU00 | Có thể do làm tròn/lấy mẫu; vẫn ghi thật. Dùng resource CSV khi phân tích; không tạo tải phụ để làm CPU cao trong ảnh. |
| Lỡ mở password/token | Dừng đoạn quay, bảo vệ file có dữ liệu lộ và quay lại phần an toàn. Không đưa secret lên YouTube. |
| Run có lỗi | Giữ raw của lượt lỗi, ghi nguyên nhân nếu có bằng chứng; lượt quay lại dùng run ID/CSV mới. Không sửa raw để thành pass. |
| OBS làm máy chậm | Hạ cấu hình quay phù hợp, test lại trước lượt mới; ghi điều kiện đo có OBS. Không coi số của hai điều kiện khác nhau là A/B tương đương. |

Theo [Grafana k6 Dashboard](https://grafana.com/docs/k6/latest/results-output/web-dashboard/), k6 có thể chờ khi còn cửa sổ dashboard mở. Wrapper đang export HTML và dùng period1s; các profile đủ dài để có biểu đồ.

## 6. Sau khi dừng recording

1. Bấm Stop Recording; mở lại video và nghe giọng ở đầu, giữa, cuối. Kiểm tra đủ ít nhất6phút và đọc được PID/CPU/Memory ở các đoạn chạy.
2. Nếu quay MKV, remux sang MP4 bằng chức năng của OBS; giữ bản gốc. Có thể cắt thao tác nhầm/đợi lâu, nhưng không ghép màn hình của hai run thành một bằng chứng đồng thời. Nếu rút gọn, ghi rõ là đoạn trích, giữ raw đủ.
3. Ghi chapter time thật sau dựng: giới thiệu, Load, Stress, Spike, Soak, **Agent Skill**, AI Audit, pipeline. Mốc Agent Skill trong SKILL.md/report phải cập nhật theo video thật, không giữ05:00 hoặc11:50 nếu thực tế khác.
4. Bạn tự upload lên YouTube Studio, chọn Visibility **Unlisted / Không công khai** và lưu. Mở URL thật bằng cửa sổ không đăng nhập để thử phát. Unlisted xem được qua link, không có nghĩa là chỉ một người được xem.
5. Gửi agent URL thật, chapter time của demo skill, và ba thư mục run dùng trong video. Agent sẽ ghép đúng video/run trong báo cáo; không tự lấy video mới làm video của các run cũ.

Tiêu đề gợi ý: `23120330 - HW05-AI - k6 Performance Testing M5`.

Mẫu mô tả để điền sau khi có video, không phải bằng chứng đã hoàn tất:

```text
MSSV: 23120330
HW05-AI - Performance Testing workflow M5 bằng k6
Workflow: Register -> Forgot -> Reset -> Login mật khẩu mới -> GET Cart
Máy đo: Windows PHUC (hostname continuity chỉ xác nhận khi có nguồn)

Chapters: điền mốc thật sau khi dựng
Load:
Stress:
Spike:
Soak (xem lại raw đã chạy10phút):
Agent Skill (đủ5endpoint):
AI Audit và pipeline:

GitHub: điền URL công khai thật sau khi đã duyệt
Run IDs video: điền từ các manifest thật
Ghi chú: kết quả có OBS cùng máy; giới hạn endurance/latency nêu trong báo cáo.
```

Hướng dẫn visibility: [YouTube Help](https://support.google.com/youtube/answer/157177). Video, URL, review cuối và điểm tự chấm vẫn do người dùng cung cấp; hướng dẫn này không cập nhật chúng thành đã hoàn tất.
