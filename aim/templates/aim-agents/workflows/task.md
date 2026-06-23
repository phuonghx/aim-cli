---
description: Manage and write tasks. Use this to create, edit, view, list, or check off tasks in the AIM workspace.
---

# /aim-task - Task Management & Tracker

List, view, create, edit, or check off tasks under the `.ai-context/tasks/` directory to manage and observe project progress.

---

## 🔴 CRITICAL RULES

1. **Structured Format** - Keep tasks in separate files (`task-N.md`). Do not manually edit the files unless using the CLI or ensuring strict metadata compliance.
2. **EARS Acceptance Criteria** - Define acceptance criteria clearly using EARS notation (Easy Approach to Requirements Syntax: *WHEN/THEN*, *WHILE*, etc.).
3. **No Duplicate IDs** - Use `aim task create` to allocate a safe, next available ID, or `aim task renumber` to fix clashes.
4. **Dependency Tracking** - Link parent tasks and prerequisite tasks correctly to form a clean dependency graph.

---

## Task

Manage tasks based on the user's request:

1. **List / Select Task**:
   - Run `aim task list` to check all tasks, assignees, and statuses.
   - Run `aim task next` to see the next actionable task based on priority and satisfied dependencies.
2. **View Details**:
   - Run `aim task view <id>` to display a task's parameters, description, and acceptance criteria.
3. **Create Task**:
   - Run `aim task create "<title>" -d "<description>" --ac "<criteria1>" --ac "<criteria2>" -p [low|medium|high|urgent] -a [assignee] --parent [parent_id] --depends-on [dep_id]`
4. **Edit Task**:
   - Run `aim task edit <id>` to update properties:
     - Change status: `-s [todo|in-progress|in-review|blocked|done]`
     - Assignee: `-a [username]`
     - Mark acceptance criteria index as done (1-based): `--check-ac <index>`
     - Add/remove dependency: `--add-dep <dep_id>` or `--remove-dep <dep_id>`
     - Link spec/plan: `--spec [path]` or `--plan [path]`
5. **Keep Tracker Updated**:
   - Make sure to update the `task.md` file in the brain conversation directory to reflect task progress.

---

## Expected Output

| Output | Command / Action |
|--------|------------------|
| Task File | Created or modified `.ai-context/tasks/task-{id}.md` file with correct metadata, description, and AC list. |
| Progress Log | Updated task status showing in `aim task list` and `aim task next`. |

---

## Usage

```bash
/aim-task list
/aim-task next
/aim-task view 42
/aim-task create "Implement Stripe Checkout" -d "Integrate payment gateway" --ac "User can pay with card"
/aim-task edit 42 -s in-progress -a developer
/aim-task edit 42 --check-ac 1 -s in-review
```
