---
description: Create, view, edit, list, or check off tasks in the AIM workspace
---

# Task Management & Tracker

List, view, create, edit, or check off tasks under the `.ai-context/tasks/` directory to manage and observe project progress.

Instructions:
1. If listing tasks is requested, run `aim task list` to check all tasks, assignees, and statuses.
2. If finding the next actionable task is requested, run `aim task next` to see the next task based on priority and dependencies.
3. If viewing a task is requested, run `aim task view <id>` to display its parameters, description, and acceptance criteria.
4. If creating a task is requested, run the `aim task create` command:
   - `aim task create "<title>" -d "<description>" --ac "<criteria1>" --ac "<criteria2>" -p [low|medium|high|urgent] -a [assignee] --parent [parent_id] --depends-on [dep_id]`
   - Make sure acceptance criteria follow EARS syntax (*WHEN/THEN*, *WHILE*, etc.).
5. If editing a task's status, assignee, or check/uncheck AC is requested, run the `aim task edit` command:
   - `aim task edit <id> -s [todo|in-progress|in-review|blocked|done]`
   - `aim task edit <id> -a [assignee]`
   - Mark AC index as completed (1-based): `aim task edit <id> --check-ac <index>`
   - Add/remove dependency: `aim task edit <id> --add-dep <dep_id>` or `--remove-dep <dep_id>`
   - Link spec/plan: `aim task edit <id> --spec [path]` or `--plan [path]`
6. Ensure task progress is updated in the conversation's `task.md` checklist in the brain folder.
