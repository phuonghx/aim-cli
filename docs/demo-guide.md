# AeroMap: AIM Interactive Demo Guide 🚀 / Hướng Dẫn Chạy Demo AIM

Welcome to the **AeroMap** demo workspace! This guide walks you through using the AIM CLI and Web Dashboard using our pre-seeded Google Maps alternative project roadmap.

Chào mừng bạn đến với workspace demo **AeroMap**! Hướng dẫn này sẽ giúp bạn trải nghiệm toàn bộ tính năng của AIM CLI và Web Dashboard thông qua danh sách công việc của dự án bản đồ AeroMap được cấu hình sẵn.

---

## 🛠️ CLI Demo Walkthrough / Trải Nghiệm Qua CLI

Open your terminal in the `aim-cli` project root and execute the following commands:

Mở terminal tại thư mục gốc của dự án `aim-cli` và thực hiện các lệnh sau:

### 1. Check Project Summary / Kiểm Tra Trạng Thái Dự Án
Run the status command to view the seeded statistics (6 tasks, 3 docs, 3 memories, and registered users):

Chạy lệnh status để xem thống kê tóm tắt (6 tasks, 3 docs, 3 memories và các thành viên được đăng ký):

```bash
python aim/aim_cli.py status
```

### 2. View Tasks Tree Hierarchy / Xem Cấu Trúc Cây Tác Vụ
Display all active tasks rendered in an indented tree view showing labels and parent-child relationships:

Liệt kê toàn bộ công việc dưới dạng cây phân cấp hiển thị các nhãn (labels) và quan hệ cha-con (subtasks):

```bash
python aim/aim_cli.py task list
```

### 3. Display Terminal Kanban Board / Xem Bảng Kanban ASCII
Print a lightweight Kanban board directly in your command line:

Hiển thị bảng Kanban ASCII trực tiếp trên terminal của bạn:

```bash
python aim/aim_cli.py board
```

### 4. Run Template Code Generation / Chạy Mẫu Sinh Mã Nguồn
Execute a dry-run of the `map-component` template to preview the React component generation:

Chạy thử (dry-run) mẫu template `map-component` để xem trước file React component được tạo ra:

```bash
python aim/aim_cli.py template run map-component --dry-run -v name="MainMap"
```

---

## 💻 Web Dashboard Walkthrough / Trải Nghiệm Qua Web Dashboard

If the dashboard server is already running, open your browser and navigate to:

Nếu server dashboard đã khởi chạy, hãy mở trình duyệt và truy cập:

👉 **[http://localhost:6423/](http://localhost:6423/)** or **[http://localhost:6420/](http://localhost:6420/)** (depending on active port)

### Try these interactive actions on the Dashboard:
1. **Interactive Kanban Board**: Drag and drop task cards (e.g., move `TASK-6` from *In Review* to *Done*).
2. **Task Details & Subtasks**: Click on a task card (e.g. `TASK-3`) to edit its description inline, change its assignee using the dropdown menu, manage its labels, or add a subtask on the fly.
3. **Knowledge Graph**: Go to the **Knowledge Graph** tab to explore visual node links between tasks and documents (e.g., `TASK-3` connected to `@doc/api/routing-api.md`).
4. **Users Management**: Go to the **👥 Users** tab to register a new team member, or rename/delete existing users.
5. **Command Palette**: Press `Ctrl + K` (or `Cmd + K`) anywhere on the screen to trigger the global search popup and find files or tasks instantly.

---

### Hãy thử các tính năng tương tác sau trên giao diện Web:
1. **Bảng Kanban kéo thả**: Kéo thả các thẻ công việc qua lại các cột trạng thái (ví dụ di chuyển `TASK-6` từ cột *In Review* sang *Done*).
2. **Chi tiết tác vụ & Cây nhiệm vụ phụ**: Click vào thẻ công việc (ví dụ `TASK-3`) để chỉnh sửa mô tả trực tiếp, đổi người thực hiện bằng dropdown menu, chỉnh sửa nhãn hoặc thêm nhanh nhiệm vụ con (subtask).
3. **Đồ thị tri thức (Knowledge Graph)**: Chọn tab **Knowledge Graph** để xem các mối liên kết trực quan giữa tasks và docs (ví dụ `TASK-3` liên kết tới `@doc/api/routing-api.md`).
4. **Quản lý thành viên**: Chọn tab **👥 Users** để thêm thành viên mới, đổi tên hoặc xóa các thành viên hiện tại.
5. **Thanh tìm kiếm nhanh**: Nhấn tổ hợp `Ctrl + K` (hoặc `Cmd + K`) ở bất kỳ đâu để hiển thị popup tìm kiếm thông tin nhanh chóng.
