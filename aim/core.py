"""Shared service layer for the AIM workspace.

This module unifies the workspace logic that was previously duplicated
between the CLI (aim_cli.py), the dashboard server (browser_server.py),
and now the MCP server (mcp_server.py). Functions here return plain data;
each frontend is responsible for its own formatting, so CLI text output
and dashboard JSON shapes stay stable.

Path resolution is delegated to aim_cli's module globals at call time
(via _cli()), so tests can keep monkeypatching aim_cli.TASKS_DIR etc.
"""
import datetime
import os
import re
import time


def _cli():
    try:
        from aim import aim_cli
    except ImportError:
        import aim_cli
    return aim_cli


# ==========================================
# Tasks
# ==========================================
def load_tasks():
    """Parse every task file. Returns (tasks sorted by id, parse error strings)."""
    cli = _cli()
    tasks, errors = [], []
    if os.path.exists(cli.TASKS_DIR):
        for filename in sorted(os.listdir(cli.TASKS_DIR)):
            if filename.startswith("task-") and filename.endswith(".md"):
                try:
                    tasks.append(cli.parse_task_file(os.path.join(cli.TASKS_DIR, filename)))
                except (ValueError, OSError) as e:
                    errors.append(f"{filename}: {e}")
    tasks.sort(key=lambda t: t["id"])
    return tasks, errors


def get_task(task_id):
    """Return the parsed task or None if it does not exist / id is invalid."""
    cli = _cli()
    tid = str(task_id).strip()
    if not tid.isdigit():
        return None
    path = os.path.join(cli.TASKS_DIR, f"task-{int(tid)}.md")
    if not os.path.exists(path):
        return None
    return cli.parse_task_file(path)


def create_task(title, description="", priority="medium", status="todo",
                assignee="unassigned", parent=None, labels=None, spec="",
                plan="", ac=None):
    """Create a task with a race-safe ID. Returns the task meta."""
    cli = _cli()
    meta = {
        "id": cli.next_task_id(),
        "title": title,
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "parent": int(parent) if parent else None,
        "labels": labels or [],
        "spec": spec,
        "plan": plan,
        "description": description,
        "ac": [{"index": i + 1, "checked": False, "text": item}
               for i, item in enumerate(ac or [])],
    }
    cli.create_task_file(meta)
    return meta


# ==========================================
# Docs
# ==========================================
def doc_files():
    """Yield (relative posix path, absolute path) for every markdown doc."""
    cli = _cli()
    if not os.path.exists(cli.DOCS_DIR):
        return
    for root, _dirs, files in os.walk(cli.DOCS_DIR):
        for file in sorted(files):
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                rel = os.path.relpath(full_path, cli.DOCS_DIR).replace("\\", "/")
                yield rel, full_path


def doc_title(content, fallback):
    for line in content.split("\n"):
        if line.startswith("# "):
            return line.replace("# ", "").strip()
    return fallback


def load_docs():
    """Return [{path, title, content}] for every doc."""
    docs = []
    for rel, full_path in doc_files():
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        fallback = os.path.basename(rel).replace(".md", "").replace("-", " ").title()
        docs.append({"path": rel, "title": doc_title(content, fallback), "content": content})
    return docs


# ==========================================
# Memories
# ==========================================
def load_memories():
    cli = _cli()
    return cli.load_json(cli.MEMORIES_PATH, [])


def add_memory(content, category="general", layer="project"):
    """Append a memory atomically. Returns (new_mem, full memories list)."""
    cli = _cli()
    memories = load_memories()
    new_mem = {
        "id": max((m.get("id", 0) for m in memories), default=0) + 1,
        "content": content,
        "category": category or "general",
        "layer": layer or "project",
        "createdAt": datetime.datetime.now().isoformat(),
    }
    memories.append(new_mem)
    cli.save_json(cli.MEMORIES_PATH, memories)
    return new_mem, memories


# ==========================================
# Reference validation
# ==========================================
TASK_REF_RE = re.compile(r"@task-(\d+)")
DOC_REF_RE = re.compile(r"@doc/([\w\-/]+(?:\.md)?)")


def validate_references():
    """Scan tasks and docs for broken @task-N / @doc/path references.

    Returns a list of structured errors:
    {"kind": "task"|"doc", "ref": str, "source": str}
    where source matches the CLI's historical phrasing
    ("task file task-3.md" / "doc @doc/guide.md").
    """
    cli = _cli()

    task_ids = set()
    if os.path.exists(cli.TASKS_DIR):
        for filename in os.listdir(cli.TASKS_DIR):
            m = re.match(r"task-(\d+)\.md", filename)
            if m:
                task_ids.add(int(m.group(1)))

    doc_paths = {rel for rel, _ in doc_files()}

    errors = []

    def check_content(content, source):
        for ref in TASK_REF_RE.findall(content):
            if int(ref) not in task_ids:
                errors.append({"kind": "task", "ref": ref, "source": source})
        for ref in DOC_REF_RE.findall(content):
            clean_ref = ref.strip()
            if not clean_ref.endswith(".md"):
                clean_ref += ".md"
            if clean_ref not in doc_paths:
                errors.append({"kind": "doc", "ref": ref, "source": source})

    if os.path.exists(cli.TASKS_DIR):
        for filename in sorted(os.listdir(cli.TASKS_DIR)):
            if filename.endswith(".md"):
                try:
                    with open(os.path.join(cli.TASKS_DIR, filename), "r", encoding="utf-8") as f:
                        check_content(f.read(), f"task file {filename}")
                except OSError:
                    pass
    for rel, full_path in doc_files():
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                check_content(f.read(), f"doc @doc/{rel}")
        except OSError:
            pass

    return errors


# ==========================================
# Search
# ==========================================
def search_workspace(query, context=40):
    """Case-insensitive substring search across tasks, docs, and memories.

    Returns a list of result dicts. Task/doc results carry
    type/id/path/ref/title/snippet; memory results carry
    type/id/category/content/ref/title/snippet.
    """
    cli = _cli()
    query = query.lower().strip()
    results = []
    if not query:
        return results

    snippet_re = re.compile(f"(?i).{{0,{context}}}{re.escape(query)}.{{0,{context}}}")

    if os.path.exists(cli.TASKS_DIR):
        for filename in sorted(os.listdir(cli.TASKS_DIR)):
            if filename.endswith(".md"):
                path = os.path.join(cli.TASKS_DIR, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if query in content.lower():
                        meta = cli.parse_task_file(path)
                        snippet = " | ".join(snippet_re.findall(content)[:2])
                        results.append({
                            "type": "task",
                            "id": meta["id"],
                            "ref": f"@task-{meta['id']}",
                            "title": meta["title"],
                            "snippet": snippet,
                        })
                except (ValueError, OSError):
                    continue

    for rel, full_path in doc_files():
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        if query in content.lower():
            fallback = os.path.basename(rel).replace(".md", "").replace("-", " ").title()
            snippet = " | ".join(snippet_re.findall(content)[:2])
            results.append({
                "type": "doc",
                "path": rel,
                "ref": f"@doc/{rel}",
                "title": doc_title(content, fallback),
                "snippet": snippet,
            })

    for mem in load_memories():
        if query in mem.get("content", "").lower():
            results.append({
                "type": "memory",
                "id": mem.get("id"),
                "category": mem.get("category", "general"),
                "content": mem.get("content", ""),
                "ref": f"Memory #{mem.get('id')}",
                "title": f"Memory ({mem.get('category', 'general')})",
                "snippet": mem.get("content", ""),
            })

    return results


# ==========================================
# Users
# ==========================================
def rename_user_propagate(old_username, new_username):
    """Update the assignee on every task owned by old_username.

    Returns (updated_count, error strings). Does NOT touch users.json -
    callers validate and persist the user list themselves.
    """
    cli = _cli()
    updated = 0
    errors = []
    if os.path.exists(cli.TASKS_DIR):
        for filename in sorted(os.listdir(cli.TASKS_DIR)):
            if filename.startswith("task-") and filename.endswith(".md"):
                path = os.path.join(cli.TASKS_DIR, filename)
                try:
                    meta = cli.parse_task_file(path)
                    if meta.get("assignee", "").strip().lower() == old_username:
                        meta["assignee"] = new_username
                        cli.write_task_file(meta)
                        updated += 1
                except Exception as e:
                    errors.append(f"{filename}: {e}")
    return updated, errors


# ==========================================
# Status aggregation
# ==========================================
def collect_status():
    """Aggregate the full workspace status used by `aim status`,
    /api/status, and MCP consumers."""
    cli = _cli()

    project_name = "My Project"
    tech_stack = []
    if os.path.exists(cli.CONFIG_PATH):
        try:
            cfg = cli.load_json(cli.CONFIG_PATH, {})
            project_name = cfg.get("projectName", project_name)
            tech_stack = cfg.get("techStack", [])
        except Exception:
            pass

    tasks, task_errors = load_tasks()
    status_counts = {"todo": 0, "in-progress": 0, "in-review": 0, "done": 0}
    for t in tasks:
        st = t.get("status", "todo").lower()
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = status_counts.get(st, 0) + 1

    doc_count = sum(1 for _ in doc_files())
    memories = load_memories()

    logs = cli.load_json(cli.TIME_LOG_PATH, [])
    total_duration = sum(entry.get("duration", 0) for entry in logs)

    active_timer = None
    if os.path.exists(cli.TIMER_STATE_PATH):
        try:
            timer_state = cli.load_json(cli.TIMER_STATE_PATH, None)
            if timer_state:
                elapsed = int(time.time() - timer_state["startedAt"])
                active_timer = {
                    "taskId": timer_state["taskId"],
                    "title": timer_state["title"],
                    "startedAt": timer_state["startedAt"],
                    "elapsed": elapsed,
                }
        except Exception:
            pass

    try:
        from aim.sync import SYNC_TARGETS
    except ImportError:
        from sync import SYNC_TARGETS
    sync_statuses = {}
    all_synced = True
    for label, rel_path, _generator in SYNC_TARGETS:
        exists = os.path.exists(os.path.join(cli.ROOT_DIR, rel_path))
        sync_statuses[label] = "OK" if exists else "Missing"
        if not exists:
            all_synced = False

    return {
        "projectName": project_name,
        "techStack": tech_stack,
        "projectRoot": cli.ROOT_DIR,
        "tasks": tasks,
        "taskErrors": task_errors,
        "statusCounts": status_counts,
        "docsCount": doc_count,
        "memories": memories,
        "timeLogs": logs,
        "totalTimeSpent": total_duration,
        "activeTimer": active_timer,
        "syncStatuses": sync_statuses,
        "allSynced": all_synced,
    }
