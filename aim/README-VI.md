# Bộ Công Cụ Đồng Bộ AI Agent — AIM 🎯

**AIM** (AI Memory / Mind) là bộ công cụ đồng bộ cấu hình, phím tắt lệnh (slash commands), quản lý tác vụ (tasks) và tài liệu (docs) dành cho các trợ lý AI thông minh bao gồm **Claude Code**, **Antigravity**, và **Codex (Cursor / Windsurf / GitHub Copilot)**.

AIM đóng vai trò như một bộ nhớ tập trung, tự động biên dịch một file cấu hình duy nhất (`.ai-context/config.json`) thành các file hướng dẫn tương thích với từng AI client (`CLAUDE.md`, `ANTIGRAVITY.md`, `.cursorrules`, `.github/copilot-instructions.md`), đồng thời cài đặt toàn bộ 20 agent chuyên biệt, 45 skill và 13 workflow từ AIM.

---

## 🏗️ Cấu Trúc Thư Mục

```plaintext
aim/
├── templates/
│   ├── config.json.template      # Khung cấu hình mặc định ban đầu
│   ├── aim-agents/               # Toàn bộ agent, skill và workflow của AIM
│   └── commands/                 # Các lệnh Slash Command cho Claude Code
│       ├── commit.md             # Hỗ trợ viết commit message chuẩn Conventional Commits
│       ├── pr.md                 # Hướng dẫn kiểm tra và tạo nội dung Pull Request
│       ├── optimize.md           # Phân tích tối ưu hóa hiệu năng và bộ nhớ
│       ├── review.md             # Quy trình đánh giá chất lượng và bảo mật code
│       ├── test.md               # Tự động mở rộng phạm vi viết Unit Test
│       └── docs.md               # Tạo chú thích mã nguồn và tài liệu API
├── setup.py                      # Kịch bản khởi tạo (ủy quyền cho aim_cli.py init)
├── setup.bat                     # File chạy nhanh trên Windows để kích hoạt setup.py
├── sync.py                       # Kịch bản đồng bộ shims độc lập
├── aim_cli.py                    # Bộ lõi thực thi các lệnh CLI của AIM
└── README.md                     # Tài liệu hướng dẫn tiếng Anh
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Tạo

Để khởi tạo AIM trong dự án của bạn:

### Trên Windows
Bạn chỉ cần click đúp vào file `setup.bat` hoặc chạy lệnh trong PowerShell/CMD:
```powershell
.\aim\setup.bat
```

Sau khi chạy xong, bộ cài sẽ tự động tạo:
- `aim.bat`: Cho phép bạn gõ trực tiếp `aim <lệnh>` trong CMD hoặc PowerShell.
- `aim.sh`: Cho phép bạn gõ `aim` trên môi trường Unix/Linux/macOS.

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

### 1. Quản Lý Tác Vụ (Task Management)
Giao tác vụ cho AI lập kế hoạch, theo dõi tiến độ và đánh dấu các tiêu chí nghiệm thu (acceptance criteria) đã hoàn thành.

```bash
# Tạo một task mới
aim task create "Tên tác vụ" -d "Mô tả chi tiết" --ac "Tiêu chí nghiệm thu 1" --ac "Tiêu chí nghiệm thu 2" -p high -a "tên-người-nhận"

# Liệt kê danh sách task
aim task list

# Xem chi tiết một task
aim task view <id>

# Cập nhật trạng thái hoặc đánh dấu hoàn thành tiêu chí nghiệm thu (AC)
aim task edit <id> -s in-progress
aim task edit <id> --check-ac 1     # Đánh dấu tiêu chí nghiệm thu số 1 là xong (1-based)
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
