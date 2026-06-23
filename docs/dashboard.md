# AIM Web Dashboard User Guide 🔮

The **AIM Web Dashboard** is a premium, dark-glassmorphism web application that offers a visual interface to manage your project memory, tasks, and documentation. This guide explains all dashboard components, layouts, and operations.

---

## 🚀 Launching the Dashboard

To start the local dashboard server, run the following command in your terminal:
```bash
aim browser
```
By default, this will launch a server at `http://localhost:6420` (or another available port) and open the URL in your web browser.

---

## 🔮 Tab 1: Dashboard Overview
The **Dashboard** tab provides a high-level visual summary of your project health:
1. **Task Statistics:** Interactive circle progress charts demonstrating completed vs active tasks.
2. **Recent Activity Log:** Feed displaying recently completed items, created docs, or logged times.
3. **Project Metrics:** Quick summaries showing the total count of documents, memories, and accumulated tracked hours.

---

## 📋 Tab 2: Kanban Board
The **Kanban Board** provides a drag-and-drop workspace representing the progress of all active tasks.

### Board Columns
Tasks are arranged into four columns based on their active status:
* **TODO:** Planned tasks.
* **IN PROGRESS:** Tasks currently being worked on.
* **IN REVIEW:** Completed implementations awaiting peer review or testing.
* **DONE:** Fully verified tasks.

### Kanban Card Details
Each card in the board is designed with rich typography and indicators:
* **Task ID & Title:** Clickable link that triggers the Task Details modal.
* **Assignee:** Avatar showing the assigned team member (e.g. `👤 charlotte`).
* **Tags/Labels:** Visual badge tags (e.g. `bug`, `frontend`, `seo`).
* **Parent Task Indicator:** Shows `↱ TASK-X` if the task is a subtask, linking back to its parent.
* **Subtask Completion Ratio:** Shows `↳ Subtasks: D/N` (e.g. `↳ Subtasks: 1/3`) indicating how many child tasks are completed.

---

## 📋 Task Details Modal Overhaul
Clicking any Kanban card opens the **Task Details Modal**, offering an interactive workspace to view and edit details:

1. **Inline Title Editing:** Click directly on the title text at the top of the modal to edit the task title inline. It saves automatically when you click away or press enter.
2. **Description Textarea:** A spacious markdown textarea allowing you to update descriptions dynamically.
3. **Dropdown Selectors:** 
   * **Status Selector:** Modify status instantly.
   * **Priority Selector:** Change priority level.
   * **Assignee Selector:** Choose a user from the dropdown list.
   * **Parent Task Selector:** Link this task to a parent by choosing from a list of active tasks.
4. **Labels Manager:** 
   * Add labels on the fly using the input form.
   * Click the close icon (`×`) on any tag badge to instantly delete it from the task.
5. **Spec & Plan Cross-References:** Direct text inputs to link design specifications (`--spec`) or implementation plans (`--plan`).
6. **Subtask Hierarchy Panel:**
   * Lists all direct child subtasks with their title and status badge.
   * Click on any child subtask in the list to jump directly to its modal.
   * **Quick Add Subtask:** An inline form at the bottom of the list lets you type a title and press Enter to instantly register a new child task.

---

## 👥 Tab 3: Users Management
The **Users** tab hosts a dedicated database interface for project members:
1. **Register User:** A sidebar card allowing you to type a username and register a new developer.
2. **User List:** A table showing all registered users.
3. **Rename Operation (Edit):** Click the "Edit" button next to any user. It prompts you for a new username. Upon submission:
   * The user is renamed in the local database.
   * **Propagation:** All tasks assigned to the old username automatically propagate the update to the new username.
4. **Delete Operation:** Delete custom users. System default users (`developer`, `unassigned`) are protected.

---

## 🕸️ Tab 4: Knowledge Graph
The **Knowledge Graph** visualizes project files and their cross-links inside a Force-Directed Graph:
* **Nodes:** Represent **Tasks** (orange nodes) and **Documents** (blue nodes).
* **Links:** Represent relationships, including:
  * Task parent-child hierarchy links.
  * Task-to-Doc specifications (`--spec`) or plans (`--plan`) link lines.
  * Document references (e.g., a doc mentioning `@task-X` or `@doc/path`).
* **Interaction:** Hover over any node to highlight its connections and display details. Drag nodes around to rearrange the visual layout dynamically.

---

## 🔍 Tab 5: Command Palette (Search Overlay)
AIM implements an instant-search Command Palette:
* **Trigger:** Click the Search Icon on the top Navbar, or press the keyboard shortcut **`Ctrl + K`** (or **`Cmd + K`** on Mac) from anywhere on the dashboard.
* **Interface:** An overlay box pops up. Start typing to query all tasks, docs, and memories in real time.
* **Results:** Shows ranked matches labeled with categories (Task 📋, Doc 📚, Memory 🧠) and matching snippets.
* **Navigation:** Click on any result to close the palette, jump to the correct tab, and open the item's details instantly.
