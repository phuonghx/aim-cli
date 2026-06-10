# AIM CLI Reference Guide 🛠️

This document provides a comprehensive command-line reference for **AIM** (AI Memory/Mind). It covers every subcommand, available flags, and real-world command examples.

---

## Table of Contents
1. [Core Lifecycle Commands](#1-core-lifecycle-commands)
   * [`aim init`](#aim-init)
   * [`aim sync`](#aim-sync)
2. [Task Management](#2-task-management)
   * [`aim task create`](#aim-task-create)
   * [`aim task list`](#aim-task-list)
   * [`aim task view`](#aim-task-view)
   * [`aim task edit`](#aim-task-edit)
3. [User & Team Management](#3-user--team-management)
   * [`aim user list`](#aim-user-list)
   * [`aim user add`](#aim-user-add)
   * [`aim user rename`](#aim-user-rename)
   * [`aim user remove`](#aim-user-remove)
4. [Structured Documentation](#4-structured-documentation)
   * [`aim doc create`](#aim-doc-create)
   * [`aim doc list`](#aim-doc-list)
   * [`aim doc view`](#aim-doc-view)
5. [Persistent Memory](#5-persistent-memory)
   * [`aim memory add`](#aim-memory-add)
   * [`aim memory list`](#aim-memory-list)
6. [Global Command Suite](#6-global-command-suite)
   * [`aim search`](#aim-search)
   * [`aim validate`](#aim-validate)
   * [`aim status`](#aim-status)
   * [`aim board`](#aim-board)
7. [Time Tracking](#7-time-tracking)
   * [`aim time start`](#aim-time-start)
   * [`aim time status`](#aim-time-status)
   * [`aim time stop`](#aim-time-stop)
   * [`aim time log`](#aim-time-log)
   * [`aim time report`](#aim-time-report)
8. [Code Generation Templates](#8-code-generation-templates)
   * [`aim template create`](#aim-template-create)
   * [`aim template list`](#aim-template-list)
   * [`aim template view`](#aim-template-view)
   * [`aim template run`](#aim-template-run)

---

## 1. Core Lifecycle Commands

### `aim init`
Initialize AIM in the project root directory. Creates `.ai-context/` directory, default templates, specialist agents, and shims configuration files.
* **Usage:** `aim init`
* **Example:**
  ```bash
  aim init
  ```

### `aim sync`
Compile and synchronize `.ai-context/config.json` into client-specific instruction files (`CLAUDE.md`, `ANTIGRAVITY.md`, `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`).
* **Usage:** `aim sync`
* **Example:**
  ```bash
  aim sync
  ```

---

## 2. Task Management

### `aim task create`
Create a new task with optional parent relationships, tags, and cross-reference links.
* **Arguments:**
  * `title` (Required): Short title of the task.
* **Options:**
  * `-d`, `--desc`: Detailed description of the task.
  * `--ac`: Acceptance criteria item (repeatable for multiple ACs).
  * `-p`, `--priority`: Task priority (`low`, `medium`, `high`, `urgent`). Default: `medium`.
  * `-a`, `--assignee`: Project username to assign this task. Default: `unassigned`.
  * `--parent`: Parent task ID (creates subtask relationship).
  * `-l`, `--label`: Categorization tag/label (repeatable for multiple labels).
  * `--spec`: Linked specification doc path (e.g. `@doc/sdd/auth.md`).
  * `--plan`: Linked implementation plan doc path (e.g. `@doc/plans/auth-plan.md`).
* **Example:**
  ```bash
  aim task create "Set up JWT Authentication" \
    -d "Implement secure login/signup using JWT tokens" \
    --ac "Verify passwords with bcrypt" \
    --ac "Generate 24h expiration JWT tokens" \
    -p high \
    -a "charlotte" \
    -l backend -l security \
    --spec "@doc/auth-sdd"
  ```

### `aim task list`
Display all active tasks rendered in an indented tree view according to parent-child subtask relationships.
* **Usage:** `aim task list`
* **Example:**
  ```bash
  aim task list
  ```

### `aim task view`
View the full markdown content of a specific task.
* **Arguments:**
  * `id` (Required): The integer ID of the task.
* **Example:**
  ```bash
  aim task view 1
  ```

### `aim task edit`
Update task properties, mark acceptance criteria, or manage labels.
* **Arguments:**
  * `id` (Required): The integer ID of the task to edit.
* **Options:**
  * `-s`, `--status`: Update status (`todo`, `in-progress`, `in-review`, `done`, `blocked`).
  * `-a`, `--assignee`: Change task assignee.
  * `--add-ac`: Add a new acceptance criteria item.
  * `--check-ac`: Mark an AC index as completed (1-based index).
  * `--parent`: Update parent task ID (set to `0` to detach and make a root task).
  * `--add-label`: Add a new label tag.
  * `--remove-label`: Remove an existing label tag.
  * `--spec`: Update linked specification document path.
  * `--plan`: Update linked plan document path.
  * `-d`, `--desc`: Update detailed task description.
* **Example:**
  ```bash
  aim task edit 1 -s "in-progress" --check-ac 1 --add-label "refactor"
  ```

---

## 3. User & Team Management

### `aim user list`
List all registered project team members.
* **Usage:** `aim user list`
* **Example:**
  ```bash
  aim user list
  ```

### `aim user add`
Register a new user in the database.
* **Arguments:**
  * `username` (Required): Unique username to add.
* **Example:**
  ```bash
  aim user add alice
  ```

### `aim user rename`
Rename an existing user. Automatically propagates name updates to the `assignee` field in all active task files.
* **Arguments:**
  * `old_username` (Required): Existing username.
  * `new_username` (Required): New username to set.
* **Example:**
  ```bash
  aim user rename charlie charlotte
  ```

### `aim user remove`
Remove a user from the database. Note that system default users (`developer`, `unassigned`) are protected.
* **Arguments:**
  * `username` (Required): Username to delete.
* **Example:**
  ```bash
  aim user remove alice
  ```

---

## 4. Structured Documentation

### `aim doc create`
Create a new markdown document inside `.ai-context/docs/`.
* **Arguments:**
  * `title` (Required): Title of the documentation file.
* **Options:**
  * `-f`, `--folder`: Subdirectory folder to organize the file (e.g. `architecture`, `guides`).
  * `-d`, `--desc`: Brief description of the documentation.
* **Example:**
  ```bash
  aim doc create "Database Indexing Guidelines" -f "architecture" -d "Rules for database migrations"
  ```

### `aim doc list`
Recursively list all document files in the project.
* **Usage:** `aim doc list`
* **Example:**
  ```bash
  aim doc list
  ```

### `aim doc view`
Read the content of a document file.
* **Arguments:**
  * `path` (Required): Path to the doc (e.g. `architecture/api-auth` or `@doc/architecture/api-auth`).
* **Example:**
  ```bash
  aim doc view architecture/api-auth
  ```

---

## 5. Persistent Memory

### `aim memory add`
Save a reusable pattern, rule, or architectural decision.
* **Arguments:**
  * `content` (Required): The memory text to remember.
* **Options:**
  * `-c`, `--category`: Categorization keyword (e.g. `decision`, `convention`, `guideline`). Default: `general`.
  * `-l`, `--layer`: Memory scope (`project` or `global`). Default: `project`.
* **Example:**
  ```bash
  aim memory add "Prefer React Functional Components and Hooks over Class Components" -c convention -l project
  ```

### `aim memory list`
List all recorded project memories.
* **Usage:** `aim memory list`
* **Example:**
  ```bash
  aim memory list
  ```

---

## 6. Global Command Suite

### `aim search`
Perform regex and case-insensitive matching across all tasks, docs, and memories.
* **Arguments:**
  * `query` (Required): The search keyword.
* **Example:**
  ```bash
  aim search "jwt"
  ```

### `aim validate`
Scan tasks and documents for broken mentions (e.g. `@task-999` or `@doc/missing` pointing to non-existent files).
* **Usage:** `aim validate`
* **Example:**
  ```bash
  aim validate
  ```

### `aim status`
Show the project statistics summary report, including task breakdown, time spent, active timers, and configuration sync status.
* **Usage:** `aim status`
* **Example:**
  ```bash
  aim status
  ```

### `aim board`
Display a lightweight, text-based ASCII Kanban board arrangement of all active tasks in the terminal.
* **Usage:** `aim board`
* **Example:**
  ```bash
  aim board
  ```

---

## 7. Time Tracking

### `aim time start`
Start a time tracking session for a specific task. Only one active timer can run at a time.
* **Arguments:**
  * `id` (Required): Task ID to track.
* **Example:**
  ```bash
  aim time start 1
  ```

### `aim time status`
Show details of the current active timer session.
* **Usage:** `aim time status`
* **Example:**
  ```bash
  aim time status
  ```

### `aim time stop`
Stop the active timer and log the duration.
* **Options:**
  * `-n`, `--note`: Optional comment describing the work session.
* **Example:**
  ```bash
  aim time stop -n "Finished styling navbar components"
  ```

### `aim time log`
Print all log entries recorded for a specific task.
* **Arguments:**
  * `id` (Required): The integer task ID.
* **Example:**
  ```bash
  aim time log 1
  ```

### `aim time report`
Generate a report displaying total accumulated work hours per task.
* **Usage:** `aim time report`
* **Example:**
  ```bash
  aim time report
  ```

---

## 8. Code Generation Templates

### `aim template create`
Create a new directory structure for code-generation templates under `.ai-context/templates/<name>/`.
* **Arguments:**
  * `name` (Required): Name of the template.
* **Example:**
  ```bash
  aim template create react-component
  ```

### `aim template list`
List all templates configured in the workspace.
* **Usage:** `aim template list`
* **Example:**
  ```bash
  aim template list
  ```

### `aim template view`
Inspect the configurations and prompt variables of a template.
* **Arguments:**
  * `name` (Required): Name of the template.
* **Example:**
  ```bash
  aim template view react-component
  ```

### `aim template run`
Execute a template to generate source files. Prompts interactively for missing variables.
* **Arguments:**
  * `name` (Required): Name of the template.
* **Options:**
  * `--dry-run`: Preview files and path calculations without writing to disk.
  * `-v`, `--var`: Variables in `key=value` format (repeatable).
* **Example:**
  ```bash
  aim template run react-component --dry-run -v name="CustomCard"
  ```
