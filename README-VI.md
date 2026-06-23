# Bộ Công Cụ Đồng Bộ AI Agent — AIM 🎯

**AIM** (AI Memory / Mind) là bộ công cụ đồng bộ cấu hình, phím tắt lệnh (slash commands), quản lý tác vụ (tasks) và tài liệu (docs) dành cho các trợ lý AI thông minh bao gồm **Claude Code**, **Antigravity**, và **Codex (Cursor / Windsurf / GitHub Copilot)**.

AIM đóng vai trò như một bộ nhớ tập trung, tự động biên dịch một file cấu hình duy nhất (`.ai-context/config.json`) thành các file hướng dẫn tương thích với từng AI client (`CLAUDE.md`, `ANTIGRAVITY.md`, `.cursorrules`, `.github/copilot-instructions.md`), đồng thời cài đặt toàn bộ 20 agent chuyên biệt, 45 skill và 13 workflow từ AIM.

---

## 🏗️ Cấu Trúc Thư Mục

```plaintext
aim-cli/
├── .github/
│   └── workflows/
│       └── release.yml           # Quy trình đóng gói và release tự động của GitHub Actions
├── aim/                          # Thư mục module chứa code chính
│   ├── templates/                # Toàn bộ agent, skill và workflow của AIM
│   ├── skills/                   
│   ├── __init__.py
│   ├── aim_cli.py                # Bộ lõi thực thi các lệnh CLI của AIM
│   ├── browser_server.py         # Máy chủ web Dashboard
│   └── sync.py                   # Kịch bản đồng bộ shims độc lập
├── .gitignore
├── install.ps1                   # Kịch bản cài đặt một dòng cho Windows PowerShell
├── install.sh                    # Kịch bản cài đặt một dòng cho macOS/Linux Bash
├── MANIFEST.in                   # File manifest khai báo file đính kèm khi đóng gói
├── setup.py                      # Kịch bản cài đặt package
├── setup.bat                     # File chạy nhanh trên Windows để kích hoạt cài đặt
├── aim.bat                       # File wrapper cho Windows (chạy lệnh aim trực tiếp)
├── aim.sh                        # File wrapper cho Bash (Unix)
└── README.md                     # Tài liệu hướng dẫn tiếng Anh
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Tạo

Để khởi tạo AIM trong dự án của bạn:

### Trên Windows
Bạn chỉ cần click đúp vào file `setup.bat` hoặc chạy lệnh trong PowerShell/CMD:
```powershell
.\setup.bat
```

Sau khi chạy xong, bộ cài sẽ tự động tạo:
- `aim.bat`: Cho phép bạn gõ trực tiếp `aim <lệnh>` trong CMD hoặc PowerShell.
- `aim.sh`: Cho phép bạn gõ `aim` trên môi trường Unix/Linux/macOS.

### Cài một dòng (one-line install)

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/phuonghx/aim-cli/main/install.ps1 | iex
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/phuonghx/aim-cli/main/install.sh | bash
```

Sau khi cài, chạy `aim init` trong thư mục dự án để bắt đầu. Mặc định, `aim init` sẽ chạy ở chế độ tương tác (interactive) để bạn:
- Chọn các AI Agent đích cần kích hoạt (Claude, Cursor, Windsurf, Antigravity, v.v.).
- Chọn chiến lược theo dõi tệp qua Git (`track-all`, `ignore-all`, hoặc `rules-only`).
- Chọn có tạo các slash command `/aim-<skill>` cho các agent tương ứng hay không.

Bạn cũng có thể truyền các tham số để bỏ qua giao diện tương tác (rất hữu ích cho CI hoặc scripts):
```bash
aim init --all-agents --git-ignore
```

Việc chạy lại `aim init` trên một dự án đã khởi tạo sẽ chỉ cập nhật tệp cấu hình `config.json` mà không ghi đè các skill/agent bạn đã tuỳ chỉnh. Sử dụng `aim init --force` nếu bạn muốn cài đặt lại toàn bộ các template từ đầu (một bản sao lưu đóng dấu thời gian `.bak` sẽ được giữ lại).

### Khắc phục lỗi `'aim' is not recognized` / `command not found`

Lỗi này gần như luôn do pip cài file thực thi `aim` vào thư mục **Scripts**
(Windows) hoặc **bin** (macOS/Linux) chưa nằm trong `PATH`. Ngay khi cài, pip
thường in cảnh báo: `WARNING: The script aim is installed in '...' which is not on PATH`.

Bộ cài một dòng nay đã **tự phát hiện** và **hỏi bạn có muốn thêm vào PATH không**
(gõ `Y` để đồng ý), sau đó nhắc bạn mở terminal mới. Nếu vẫn lỗi, sửa thủ công:

**Windows (PowerShell)** — tìm thư mục Scripts rồi thêm vào PATH của user:
```powershell
# Xem thư mục chứa console scripts (kiểm tra cả 2 dòng xem dòng nào có aim.exe):
python -c "import sysconfig; print(sysconfig.get_paths('nt_user')['scripts']); print(sysconfig.get_paths('nt')['scripts'])"

# Thêm đúng thư mục (thay đường dẫn) vào PATH user, rồi mở lại terminal:
$d = "C:\Users\<ban>\AppData\Roaming\Python\Python3XX\Scripts"
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User').TrimEnd(';') + ';' + $d, 'User')
```
> Lưu ý: câu lỗi `'aim' is not recognized as an internal or external command` là
> của **cmd.exe**. Nếu bạn cài bằng PowerShell thì cũng nên chạy `aim` trong PowerShell.

**macOS / Linux** — thêm thư mục bin vào file khởi động của shell:
```bash
# Xem thư mục chứa console scripts (thường là ~/.local/bin):
python3 -c "import sysconfig; print(sysconfig.get_paths('posix_user')['scripts'])"

echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc   # hoặc ~/.bashrc
source ~/.zshrc
```

**Cách chạy tạm không cần sửa PATH (mọi hệ điều hành):**
```bash
python -m aim.aim_cli init
```

---

## 🔄 Đồng Bộ Hóa Hướng Dẫn (Sync)

Khi bạn thay đổi công nghệ sử dụng, lệnh build/test, hoặc thêm quy tắc lập trình mới trong tệp `.ai-context/config.json`, hãy đồng bộ lại ra các AI Client bằng lệnh:

```bash
aim sync
# hoặc: python aim/sync.py
```

Lệnh này sẽ tự động cập nhật các file:
* **Claude Code**: file `CLAUDE.md` (chứa lệnh build, test, quy tắc phong cách viết code và tối ưu hóa).
* **Antigravity**: file `ANTIGRAVITY.md` (chứa quy tắc lập kế hoạch Planning Mode, tra cứu Knowledge Items và kiểm chứng code).
* **Codex (Cursor / Windsurf)**: file `.cursorrules` và `.windsurfrules` (chứa quy tắc UI/UX, cách thiết kế giao diện hiện đại và các quy tắc đặc thù).
* **GitHub Copilot**: file `.github/copilot-instructions.md` (chứa ngữ cảnh dự án và ràng buộc công nghệ).

---

## 🛠️ Danh Sách Các Lệnh CLI

### 1. Quản Lý Tác Vụ & Cấu Trúc Nhánh (Task & Subtask Management)
Giao tác vụ cho AI lập kế hoạch, theo dõi tiến độ, tạo cấu trúc cây nhiệm vụ (subtasks) và quản lý tags nhãn.

```bash
# Tạo một task mới (hỗ trợ parent task ID, labels nhãn, spec và plan)
aim task create "Tên tác vụ" -d "Mô tả chi tiết" --ac "Tiêu chí 1" -p high -a "alice" --parent 1 -l bug -l seo --spec "@doc/sdd/seo.md"

# Liệt kê danh sách task (hiển thị dưới dạng cây phân cấp thụt lề cùng nhãn)
aim task list

# Xem chi tiết một task
aim task view <id>

# Cập nhật trạng thái, thêm/xóa nhãn, cập nhật spec/plan
aim task edit <id> -s in-progress --parent 2 --add-label frontend --remove-label bug -d "Mô tả mới"
aim task edit <id> --check-ac 1     # Đánh dấu tiêu chí nghiệm thu số 1 là xong (1-based)
```

### 1.5. Quản Lý Thành Viên (User Management)
Quản lý danh sách thành viên dự án và tự động cập nhật khi giao việc.

```bash
# Liệt kê danh sách thành viên
aim user list

# Thêm thành viên mới
aim user add <username>

# Đổi tên thành viên (tự động đồng bộ các task đang giao cho thành viên cũ)
aim user rename <old_username> <new_username>

# Xóa thành viên (ngoại trừ các thành viên hệ thống mặc định)
aim user remove <username>
```

### 1.6. Trạng Thái Dự Án & Bảng Kanban ASCII
Kiểm tra thống kê sức khỏe dự án và xem trực quan các task dưới dạng bảng Kanban ASCII ngay trong terminal.

```bash
# Xem báo cáo tóm tắt trạng thái dự án (thông số về tasks, docs, memories, time tracking và sync health)
aim status

# Hiển thị các task sắp xếp theo bảng Kanban ASCII (cột: TODO, IN-PROGRESS, IN-REVIEW, DONE)
aim board
```

### 1.7. Theo Dõi Thời Gian Làm Việc (Time Tracking)
Theo dõi thời gian chính xác bạn làm việc cho các task cụ thể trực tiếp từ CLI.

```bash
# Bắt đầu tính giờ cho một task
aim time start <task_id>

# Xem trạng thái bộ đếm giờ hiện tại đang chạy
aim time status

# Dừng bộ đếm giờ hiện tại và ghi chú (tùy chọn)
aim time stop -n "Đã triển khai tính năng X"

# Xem nhật ký thời gian của một task cụ thể
aim time log <task_id>

# Xuất báo cáo tổng hợp thời gian làm việc toàn dự án
aim time report
```

### 1.8. Mẫu Sinh Code (Code Generation Templates)
Khởi tạo, xem và thực thi các mẫu tạo mã nguồn tái sử dụng với các biến động và bộ chuyển đổi kiểu chữ (casing helpers):

```bash
# Liệt kê tất cả các mẫu hiện có
aim template list

# Tạo khung mẫu mới (tạo thư mục cấu hình trong .ai-context/templates/<tên_mẫu>/)
aim template create <tên_mẫu>

# Xem nội dung cấu hình của một mẫu cụ thể
aim template view <tên_mẫu>

# Thực thi mẫu sinh code (sẽ hỏi các biến còn thiếu nếu chưa truyền)
aim template run <tên_mẫu>

# Thực thi với các biến được định nghĩa sẵn
aim template run <tên_mẫu> -v name="MyComponent"

# Chạy thử (dry-run) để xem trước các tệp sẽ được tạo mà không ghi xuống đĩa
aim template run <tên_mẫu> --dry-run -v name="MyComponent"
```

### 2. Quản Lý Tài Liệu (Structured Documentation)
Tạo, duyệt và đọc các tài liệu hướng dẫn nằm trong `.ai-context/docs/`.

```bash
# Tạo một doc mới
aim doc create "Thiết Kế API" -f "architecture" -d "Hướng dẫn thiết kế API JWT"

# Liệt kê tài liệu
aim doc list

# Đọc nội dung tài liệu
aim doc view architecture/thiet-ke-api
```

### 3. Bộ Nhớ Bền Vững (Persistent Memory)
Lưu lại các quyết định thiết kế, quy chuẩn code để AI tự động nhớ và tái sử dụng qua các phiên chat.

```bash
# Thêm một quyết định hoặc quy chuẩn vào bộ nhớ dự án
aim memory add "Sử dụng repository pattern cho các giao dịch database" -c decision -l project

# Liệt kê bộ nhớ
aim memory list
```

### 4. Tìm Kiếm Cục Bộ (Search)
Tìm kiếm nhanh chóng theo từ khóa hoặc regex trên toàn bộ tasks, tài liệu và bộ nhớ:

```bash
aim search "api"
```

### 5. Kiểm Tra Liên Kết (Validate)
Quét toàn bộ tài liệu và tác vụ để phát hiện các liên kết bị lỗi (ví dụ `@task-X` hoặc `@doc/path` trỏ tới đối tượng không tồn tại):

```bash
aim validate
```

---

## 💻 Giao Diện Web Dashboard (`aim browser`)

Khởi chạy máy chủ Web Dashboard cục bộ để theo dõi trực quan và tương tác với toàn bộ bộ não dự án:
```bash
aim browser
```

### Các Tính Năng Cao Cấp Trên Giao Diện Web:
1. **🔮 Tổng Quan Dashboard**: Xem tiến độ hoàn thành task, biểu đồ thời gian hoạt động, nhật ký chấm công và các quyết định dự án gần đây.
2. **📋 Kanban Task Board**:
   * Bảng công việc kéo thả chia theo các trạng thái (Todo, In Progress, In Review, Done).
   * Thẻ task hiển thị đầy đủ thông tin: nhãn (tags), liên kết Parent task, và số lượng subtasks con hoàn thành.
   * Popup chi tiết task cho phép chỉnh sửa tiêu đề (inline), mô tả (textarea), nhãn tags, liên kết Spec/Plan tài liệu, và quản lý cây subtasks trực quan (click mở subtask, thêm nhanh subtask).
3. **👥 Users Management**: Giao diện đăng ký, sửa tên (rename), và xóa thành viên dự án. Đổi tên thành viên tự động lan truyền và cập nhật tất cả task tương ứng.
4. **🕸️ Knowledge Graph**: Đồ thị lực hướng (force-directed graph) biểu diễn mối tương quan và liên kết chéo giữa các Tasks và Tài liệu.
5. **🔍 Command Palette (Search)**: Nhấn tổ hợp phím `Ctrl + K` (hoặc `Cmd + K`) để mở thanh tìm kiếm nhanh mọi lúc mọi nơi trên Dashboard.
