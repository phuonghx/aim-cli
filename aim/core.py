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
import getpass
import json
import os
import re
import subprocess
import time


def _cli():
    try:
        from aim import aim_cli
    except ImportError:
        import aim_cli
    return aim_cli


def current_author():
    """Best-effort identity for attributing memories: `git config user.name`,
    falling back to the OS user. Never raises."""
    name = _git(["config", "user.name"])
    if name:
        return name.strip()
    try:
        return getpass.getuser()
    except Exception:
        return os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"


def _git(args):
    """Run a git command in the workspace root. Returns stdout (str) on
    success, or None if git is unavailable / not a repo / the command fails.
    Isolated as a seam so diagnostics are unit-testable without real git."""
    cli = _cli()
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cli.ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def git_commits_since(path, since_iso):
    """Count commits touching `path` since `since_iso`. Returns an int, or
    None when git can't answer (no repo / git missing / path untracked)."""
    out = _git(["log", "--since", since_iso, "--oneline", "--", path])
    if out is None:
        return None
    return len([line for line in out.splitlines() if line.strip()])


# Extract references from free text: @task-N, @doc/path, and source file
# paths (either backtick-quoted or bare tokens that contain a slash and a
# file extension). Used to link memories to the code they describe.
_REF_PATTERNS = [
    re.compile(r"@task-\d+"),
    re.compile(r"@doc/[\w\-/]+(?:\.md)?"),
    re.compile(r"`([^`]+)`"),                       # backtick-quoted paths
    re.compile(r"(?<![\w`])([\w][\w./-]*/[\w./-]*\.[A-Za-z0-9]{1,6})"),  # bare a/b.ext
]


def extract_refs(text):
    """Return a deduped, order-preserving list of references found in text."""
    if not text:
        return []
    seen, refs = set(), []

    def add(value):
        value = value.strip()
        if value and value not in seen:
            seen.add(value)
            refs.append(value)

    for m in _REF_PATTERNS[0].findall(text):
        add(m)
    for m in _REF_PATTERNS[1].findall(text):
        add(m)
    # backtick group: keep contents that look like a path or a filename
    # (a directory slash, or a bare name with a file extension).
    for m in _REF_PATTERNS[2].findall(text):
        m = m.strip()
        if " " in m:
            continue
        if "/" in m or re.match(r"^[\w.\-]+\.[A-Za-z0-9]{1,6}$", m):
            add(m)
    for m in _REF_PATTERNS[3].findall(text):
        add(m)
    return refs


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


PRIORITY_ORDER = {"urgent": 3, "high": 2, "medium": 1, "low": 0}
ACTIONABLE_BLOCKED = {"done", "blocked"}


def create_task(title, description="", priority="medium", status="todo",
                assignee="unassigned", parent=None, labels=None, spec="",
                plan="", ac=None, depends_on=None):
    """Create a task with a race-safe ID. Returns the task meta."""
    cli = _cli()
    meta = {
        "id": cli.next_task_id(),
        "title": title,
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "parent": int(parent) if parent else None,
        "dependsOn": [int(d) for d in (depends_on or [])],
        "labels": labels or [],
        "spec": spec,
        "plan": plan,
        "description": description,
        "ac": [{"index": i + 1, "checked": False, "text": item}
               for i, item in enumerate(ac or [])],
    }
    cli.create_task_file(meta)
    return meta


def create_tasks(specs):
    """Batch-create tasks (used by the PRD-decomposition MCP flow). Each spec
    is {title, description?, priority?, ac?, labels?, key?, dependsOn?}, where
    dependsOn may reference existing task ids (int) OR a `key` string of an
    earlier task in this same batch. Two passes so within-batch deps resolve.
    Returns the created task metas."""
    cli = _cli()
    created, key_to_id = [], {}
    for s in specs:
        meta = create_task(
            s["title"],
            description=s.get("description", ""),
            priority=s.get("priority", "medium"),
            labels=s.get("labels"),
            ac=s.get("ac"),
        )
        created.append(meta)
        if s.get("key"):
            key_to_id[s["key"]] = meta["id"]

    for s, meta in zip(specs, created):
        deps = []
        for d in (s.get("dependsOn") or []):
            if isinstance(d, bool):
                continue
            if isinstance(d, int):
                deps.append(d)
            elif isinstance(d, str):
                if d in key_to_id:
                    deps.append(key_to_id[d])
                elif d.isdigit():
                    deps.append(int(d))
        if deps:
            full = get_task(meta["id"])
            full["dependsOn"] = deps
            cli.write_task_file(full)
            meta["dependsOn"] = deps
    return created


def next_task():
    """Return the next actionable task: highest priority (then lowest id) among
    not-done, not-blocked tasks whose dependencies are all done. None if none."""
    tasks, _errors = load_tasks()
    done = {t["id"] for t in tasks if t.get("status", "").lower() == "done"}
    candidates = [
        t for t in tasks
        if t.get("status", "todo").lower() not in ACTIONABLE_BLOCKED
        and all(d in done for d in t.get("dependsOn", []))
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda t: (-PRIORITY_ORDER.get(t.get("priority", "medium").lower(), 1), t["id"]))
    return candidates[0]


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
def _memory_store_path(layer):
    cli = _cli()
    return cli.GLOBAL_MEMORIES_PATH if layer == "global" else cli.MEMORIES_PATH


def _load_store(layer):
    cli = _cli()
    return cli.load_json(_memory_store_path(layer), [])


def load_memories():
    """All memories the current workspace sees: project store + the shared
    global store, each tagged with its `layer`. IDs are unique across both."""
    project = _load_store("project")
    for m in project:
        m.setdefault("layer", "project")
    glob = _load_store("global")
    for m in glob:
        m["layer"] = "global"
    return project + glob


def _next_memory_id():
    return max((m.get("id", 0) for m in load_memories()), default=0) + 1


def add_memory(content, category="general", layer="project", author=None, refs=None):
    """Append a memory atomically. Returns (new_mem, full memories list).
    IDs are allocated across both stores so project/global never collide."""
    cli = _cli()
    layer = layer or "project"
    now = datetime.datetime.now().isoformat()
    new_mem = {
        "id": _next_memory_id(),
        "content": content,
        "category": category or "general",
        "layer": layer,
        "author": author if author is not None else current_author(),
        "createdAt": now,
        "reviewedAt": now,
        "status": "active",
        "refs": refs if refs is not None else extract_refs(content),
    }
    store = _load_store(layer)
    store.append(new_mem)
    cli.save_json(_memory_store_path(layer), store)
    return new_mem, load_memories()


def _find_memory(mem_id):
    """Return (layer, store list, index) for a memory id, or (None, None, None)."""
    mem_id = int(mem_id)
    for layer in ("project", "global"):
        store = _load_store(layer)
        for i, m in enumerate(store):
            if m.get("id") == mem_id:
                return layer, store, i
    return None, None, None


def update_memory(mem_id, content=None, category=None, layer=None):
    """Edit a memory in place. Re-extracts refs when content changes.
    Returns the updated memory, or None if not found.
    Changing `layer` moves the memory between stores, keeping its id."""
    cli = _cli()
    cur_layer, store, idx = _find_memory(mem_id)
    if store is None:
        return None
    mem = store[idx]
    if content is not None:
        mem["content"] = content
        mem["refs"] = extract_refs(content)
    if category is not None:
        mem["category"] = category
    if layer is not None and layer != cur_layer:
        store.pop(idx)
        cli.save_json(_memory_store_path(cur_layer), store)
        mem["layer"] = layer
        dest = _load_store(layer)
        dest.append(mem)
        cli.save_json(_memory_store_path(layer), dest)
    else:
        cli.save_json(_memory_store_path(cur_layer), store)
    return mem


def delete_memory(mem_id):
    """Remove a memory. Returns True if something was deleted."""
    cli = _cli()
    layer, store, idx = _find_memory(mem_id)
    if store is None:
        return False
    store.pop(idx)
    cli.save_json(_memory_store_path(layer), store)
    return True


def review_memory(mem_id):
    """Mark a memory as freshly verified (resets the staleness clock).
    Returns the memory, or None if not found."""
    cli = _cli()
    layer, store, idx = _find_memory(mem_id)
    if store is None:
        return None
    store[idx]["reviewedAt"] = datetime.datetime.now().isoformat()
    store[idx]["status"] = "active"
    cli.save_json(_memory_store_path(layer), store)
    return store[idx]


def record_correction(what_was_wrong, correct_approach, refs=None, layer="project"):
    """Capture a mid-session correction as a memory so the lesson survives
    across sessions and tools. Returns (new_mem, memories)."""
    content = f"Avoid: {what_was_wrong}\nInstead: {correct_approach}"
    merged = list(refs or [])
    for r in extract_refs(content):
        if r not in merged:
            merged.append(r)
    return add_memory(content, category="correction", layer=layer, refs=merged)


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


def _all_searchables():
    """Every searchable item as (result_dict, text) for semantic ranking."""
    cli = _cli()
    items = []
    if os.path.exists(cli.TASKS_DIR):
        for filename in sorted(os.listdir(cli.TASKS_DIR)):
            if filename.startswith("task-") and filename.endswith(".md"):
                try:
                    meta = cli.parse_task_file(os.path.join(cli.TASKS_DIR, filename))
                except (ValueError, OSError):
                    continue
                text = f"{meta['title']}\n{meta.get('description', '')}"
                items.append(({"type": "task", "id": meta["id"], "ref": f"@task-{meta['id']}",
                               "title": meta["title"], "snippet": meta.get("description", "")[:120]}, text))
    for rel, full_path in doc_files():
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        fallback = os.path.basename(rel).replace(".md", "").replace("-", " ").title()
        title = doc_title(content, fallback)
        items.append(({"type": "doc", "path": rel, "ref": f"@doc/{rel}",
                       "title": title, "snippet": content[:120]}, f"{title}\n{content}"))
    for mem in load_memories():
        items.append(({"type": "memory", "id": mem.get("id"),
                       "ref": f"Memory #{mem.get('id')}",
                       "title": f"Memory ({mem.get('category', 'general')})",
                       "snippet": mem.get("content", "")}, mem.get("content", "")))
    return items


def semantic_search(query, top_k=10):
    """Embeddings-backed search (optional [semantic] extra). Returns ranked
    results (each with a `score`), or None if the extra is unavailable."""
    try:
        from aim import semantic
    except ImportError:
        import semantic
    items = _all_searchables()
    ranked = semantic.rank(query, [(res["ref"], text) for res, text in items])
    if ranked is None:
        return None
    by_ref = {res["ref"]: res for res, _t in items}
    out = []
    for ref, score in ranked[:top_k]:
        res = dict(by_ref[ref])
        res["score"] = round(score, 3)
        out.append(res)
    return out


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


# ==========================================
# GitHub sync — `aim github` (Issues / Projects via the gh CLI)
# ==========================================
def _gh(args, input_text=None):
    """Run a gh CLI command in the workspace root. Returns stdout on success;
    raises RuntimeError (with stderr) on failure or if gh is unavailable.
    Isolated as a seam so the sync logic is unit-testable without real gh."""
    cli = _cli()
    try:
        result = subprocess.run(
            ["gh", *args], cwd=cli.ROOT_DIR, capture_output=True,
            text=True, input=input_text, timeout=60,
        )
    except (FileNotFoundError, OSError) as e:
        raise RuntimeError("GitHub CLI (gh) is not installed or not on PATH.") from e
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"gh command failed: {e}") from e
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "gh command failed").strip())
    return result.stdout


def github_available():
    """True if gh is installed and authenticated."""
    try:
        _gh(["auth", "status"])
        return True
    except RuntimeError:
        return False


def repo_slug():
    """owner/repo for the current workspace, via gh."""
    return _gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).strip()


_ISSUE_NUM_RE = re.compile(r"/issues/(\d+)\s*$")


def parse_issue_number(url):
    m = _ISSUE_NUM_RE.search((url or "").strip())
    return int(m.group(1)) if m else None


def task_to_issue_body(task):
    """Render an AIM task as a GitHub issue body, ending with a hidden marker
    that ties the issue back to the AIM task id."""
    lines = []
    if task.get("description"):
        lines.append(task["description"].strip())
        lines.append("")
    if task.get("ac"):
        lines.append("### Acceptance Criteria")
        for ac in task["ac"]:
            box = "x" if ac.get("checked") else " "
            lines.append(f"- [{box}] {ac['text']}")
        lines.append("")
    if task.get("dependsOn"):
        lines.append("**Depends on:** " + ", ".join(f"AIM task-{d}" for d in task["dependsOn"]))
        lines.append("")
    lines.append("---")
    lines.append(f"_Synced from AIM · task-{task['id']} · do not edit this marker_")
    lines.append(f"<!-- aim-task:{task['id']} -->")
    return "\n".join(lines).strip()


def _issue_title(task):
    return f"[AIM-{task['id']}] {task['title']}"


def push_task(task_id, project=None):
    """Create or update a GitHub issue for one AIM task (idempotent via the
    stored githubIssue number). Maps done->closed, else open. Optionally adds
    the issue to a Project v2. Returns {taskId, issue, action, status}."""
    cli = _cli()
    task = get_task(task_id)
    if task is None:
        raise RuntimeError(f"Task {task_id} not found.")

    title = _issue_title(task)
    body = task_to_issue_body(task)
    issue = task.get("githubIssue")
    status = task.get("status", "todo").lower()

    if issue:
        _gh(["issue", "edit", str(issue), "--title", title, "--body", body])
        action = "updated"
    else:
        out = _gh(["issue", "create", "--title", title, "--body", body])
        url = out.strip().splitlines()[-1] if out.strip() else ""
        issue = parse_issue_number(url)
        if issue is None:
            raise RuntimeError(f"Could not parse issue number from gh output: {out!r}")
        task["githubIssue"] = issue
        cli.write_task_file(task)
        action = "created"

    # Reflect AIM status on the issue: done -> closed, otherwise open.
    try:
        if status == "done":
            _gh(["issue", "close", str(issue)])
        else:
            _gh(["issue", "reopen", str(issue)])
    except RuntimeError:
        pass  # already in that state, or not permitted — non-fatal

    if project:
        try:
            slug = repo_slug()
            owner = slug.split("/")[0]
            issue_url = f"https://github.com/{slug}/issues/{issue}"
            _gh(["project", "item-add", str(project), "--owner", owner, "--url", issue_url])
        except RuntimeError:
            pass  # project linking is best-effort

    return {"taskId": task["id"], "issue": issue, "action": action, "status": status}


def push_all(project=None):
    """Push every task to GitHub. Returns a list of per-task results."""
    tasks, _errors = load_tasks()
    return [push_task(t["id"], project=project) for t in tasks]


def github_status():
    """Per-task linkage view: {taskId, title, status, issue}."""
    tasks, _errors = load_tasks()
    return [{"taskId": t["id"], "title": t["title"],
             "status": t.get("status", "todo"), "issue": t.get("githubIssue")}
            for t in tasks]


def create_project(title):
    """Create a GitHub Project (v2) owned by the repo owner. Returns the parsed
    JSON (number, url, ...)."""
    owner = repo_slug().split("/")[0]
    out = _gh(["project", "create", "--owner", owner, "--title", title, "--format", "json"])
    return json.loads(out)


# ---- Two-way sync: pull GitHub issue changes back into AIM (issue #7) ----
ISSUE_TITLE_PREFIX = re.compile(r"^\[AIM-\d+\]\s*")


def _read_issue(issue):
    return json.loads(_gh(["issue", "view", str(issue), "--json", "number,title,state"]))


def issue_to_updates(task, issue_data):
    """Compute the AIM-side changes a GitHub issue implies. Conflict policy:
    GitHub is canonical for state (open/closed) and the issue title; AIM stays
    canonical for acceptance criteria, dependencies, and spec links (untouched)."""
    changes = {}
    new_title = ISSUE_TITLE_PREFIX.sub("", issue_data.get("title", "")).strip()
    if new_title and new_title != task.get("title"):
        changes["title"] = new_title
    state = (issue_data.get("state") or "").upper()
    current = task.get("status", "todo").lower()
    if state == "CLOSED" and current != "done":
        changes["status"] = "done"
    elif state == "OPEN" and current == "done":
        changes["status"] = "todo"
    return changes


def pull_task(task_id, dry_run=False):
    """Reconcile one task from its linked GitHub issue. Returns
    {taskId, issue, changes}. With dry_run, computes changes without writing
    (this is also how drift is detected)."""
    cli = _cli()
    task = get_task(task_id)
    if task is None:
        raise RuntimeError(f"Task {task_id} not found.")
    issue = task.get("githubIssue")
    if not issue:
        return {"taskId": task["id"], "issue": None, "changes": {}}
    changes = issue_to_updates(task, _read_issue(issue))
    if changes and not dry_run:
        task.update(changes)
        cli.write_task_file(task)
    return {"taskId": task["id"], "issue": issue, "changes": changes}


def pull_all(dry_run=False):
    """Reconcile every linked task from GitHub. Returns per-task results."""
    tasks, _errors = load_tasks()
    return [pull_task(t["id"], dry_run=dry_run) for t in tasks if t.get("githubIssue")]


# AIM status -> GitHub Project (v2) "Status" single-select option name.
STATUS_TO_PROJECT_OPTION = {
    "todo": "Todo",
    "in-progress": "In Progress",
    "in-review": "In Progress",
    "blocked": "Todo",
    "done": "Done",
}


def sync_project_status(project):
    """Set each linked card's Project (v2) Status field to match its AIM task
    status (issue #8). Fetches project metadata once. Returns the number of
    cards updated. Best-effort: no-op if the project has no Status field."""
    owner = repo_slug().split("/")[0]
    proj = json.loads(_gh(["project", "view", str(project), "--owner", owner, "--format", "json"]))
    fields = json.loads(_gh(["project", "field-list", str(project), "--owner", owner, "--format", "json"]))["fields"]
    status_field = next((f for f in fields if f.get("name") == "Status"), None)
    if not status_field:
        return 0
    option_by_name = {o["name"]: o["id"] for o in status_field.get("options", [])}
    items = json.loads(_gh(["project", "item-list", str(project), "--owner", owner, "--format", "json"]))["items"]
    item_by_issue = {it["content"]["number"]: it["id"]
                     for it in items if it.get("content") and it["content"].get("number")}

    tasks, _errors = load_tasks()
    updated = 0
    for t in tasks:
        issue = t.get("githubIssue")
        if not issue or issue not in item_by_issue:
            continue
        option_name = STATUS_TO_PROJECT_OPTION.get(t.get("status", "todo").lower(), "Todo")
        option_id = option_by_name.get(option_name)
        if not option_id:
            continue
        try:
            _gh(["project", "item-edit", "--id", item_by_issue[issue],
                 "--project-id", proj["id"], "--field-id", status_field["id"],
                 "--single-select-option-id", option_id])
            updated += 1
        except RuntimeError:
            pass
    return updated


# ==========================================
# Task renumber — `aim task renumber` (issue #10)
# ==========================================
def renumber_task(old_id, new_id):
    """Rename task <old_id> to <new_id> and rewrite every reference to it
    (@task-N in any task/doc, plus dependsOn/parent pointers). Resolves the
    duplicate/mismatched-id findings from `aim doctor`. Returns a summary."""
    cli = _cli()
    old_id, new_id = int(old_id), int(new_id)
    if old_id == new_id:
        raise ValueError("Old and new ids are the same.")
    old_path = os.path.join(cli.TASKS_DIR, f"task-{old_id}.md")
    new_path = os.path.join(cli.TASKS_DIR, f"task-{new_id}.md")
    if not os.path.exists(old_path):
        raise ValueError(f"Task {old_id} does not exist.")
    if os.path.exists(new_path):
        raise ValueError(f"Task {new_id} already exists — pick a free id.")

    meta = cli.parse_task_file(old_path)
    meta["id"] = new_id
    cli.write_task_file(meta)          # writes task-<new_id>.md
    os.remove(old_path)

    ref_re = re.compile(rf"@task-{old_id}\b")
    files_updated = 0

    # Rewrite references in every task file (meta-level + prose text).
    for filename in os.listdir(cli.TASKS_DIR):
        if not (filename.startswith("task-") and filename.endswith(".md")):
            continue
        path = os.path.join(cli.TASKS_DIR, filename)
        try:
            m = cli.parse_task_file(path)
        except (ValueError, OSError):
            continue
        changed = False
        if m.get("parent") == old_id:
            m["parent"] = new_id
            changed = True
        if old_id in m.get("dependsOn", []):
            m["dependsOn"] = [new_id if d == old_id else d for d in m["dependsOn"]]
            changed = True
        for field in ("description", "notes"):
            if m.get(field) and ref_re.search(m[field]):
                m[field] = ref_re.sub(f"@task-{new_id}", m[field])
                changed = True
        for sec in m.get("extraSections", []):
            if ref_re.search(sec.get("body", "")):
                sec["body"] = ref_re.sub(f"@task-{new_id}", sec["body"])
                changed = True
        if changed:
            cli.write_task_file(m)
            files_updated += 1

    # Rewrite @task references in docs (raw text).
    for _rel, full_path in doc_files():
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        if ref_re.search(content):
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(ref_re.sub(f"@task-{new_id}", content))
            files_updated += 1

    return {"old": old_id, "new": new_id, "filesUpdated": files_updated}


# ==========================================
# Spec-driven development — `aim spec`
# ==========================================
def tasks_without_spec():
    """IDs of tasks that have no linked spec document."""
    tasks, _errors = load_tasks()
    return [t["id"] for t in tasks if not (t.get("spec") or "").strip()]


def spec_coverage():
    """Spec-link coverage across tasks: {total, withSpec, withoutSpec[ids]}."""
    tasks, _errors = load_tasks()
    without = [t["id"] for t in tasks if not (t.get("spec") or "").strip()]
    return {"total": len(tasks), "withSpec": len(tasks) - len(without), "withoutSpec": without}


def import_spec(spec_dir, name=None):
    """Import a spec-kit feature directory (spec.md, optional plan.md) into AIM:
    copy them into .ai-context/docs/specs|plans and create an umbrella task
    linked to the spec. Returns a summary. Agents expand the task into subtasks
    (e.g. via the decompose_prd MCP prompt)."""
    cli = _cli()
    if not os.path.isdir(spec_dir):
        raise ValueError(f"Not a directory: {spec_dir}")
    name = name or os.path.basename(os.path.normpath(spec_dir))
    slug = re.sub(r"[^\w]+", "-", name).strip("-").lower() or "spec"

    files = {f.lower(): f for f in os.listdir(spec_dir)}
    if "spec.md" not in files:
        raise ValueError(f"No spec.md found in {spec_dir}")

    def _read(fn):
        with open(os.path.join(spec_dir, fn), "r", encoding="utf-8") as f:
            return f.read()

    result = {"name": name}

    spec_content = _read(files["spec.md"])
    specs_dir = os.path.join(cli.DOCS_DIR, "specs")
    os.makedirs(specs_dir, exist_ok=True)
    spec_rel = f"specs/{slug}.md"
    with open(os.path.join(cli.DOCS_DIR, spec_rel), "w", encoding="utf-8") as f:
        f.write(spec_content)
    result["specDoc"] = spec_rel
    spec_link = f"@doc/{spec_rel}"

    plan_link = ""
    if "plan.md" in files:
        plans_dir = os.path.join(cli.DOCS_DIR, "plans")
        os.makedirs(plans_dir, exist_ok=True)
        plan_rel = f"plans/{slug}.md"
        with open(os.path.join(cli.DOCS_DIR, plan_rel), "w", encoding="utf-8") as f:
            f.write(_read(files["plan.md"]))
        result["planDoc"] = plan_rel
        plan_link = f"@doc/{plan_rel}"

    title = doc_title(spec_content, name)
    meta = create_task(
        f"Implement: {title}",
        description=f"Umbrella task imported from spec-kit directory: {spec_dir}",
        spec=spec_link,
        plan=plan_link,
    )
    result["taskId"] = meta["id"]
    return result


# ==========================================
# Ingest — `aim ingest` (reverse-sync)
# ==========================================
# Extra hand-written rule files to scan beyond the sync targets.
INGEST_EXTRA_SOURCES = [".clinerules", ".rules", ".aider.conf.yml"]


def _ingest_candidates():
    """Relative paths of known rule files to scan, deduped, order-preserving."""
    try:
        from aim.sync import SYNC_TARGETS
    except ImportError:
        from sync import SYNC_TARGETS
    paths = [rel for _label, rel, _gen in SYNC_TARGETS] + INGEST_EXTRA_SOURCES
    seen, out = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def strip_aim_block(text):
    """Return the user-authored part of a rule file: everything outside the
    AIM:BEGIN/END managed block, minus any leading YAML/MDC frontmatter.
    This is what makes ingest safe to re-run — AIM never re-imports its own
    generated output."""
    try:
        from aim.sync import AIM_BEGIN, AIM_END
    except ImportError:
        from sync import AIM_BEGIN, AIM_END
    if AIM_BEGIN in text and AIM_END in text:
        text = text.split(AIM_BEGIN, 1)[0] + text.split(AIM_END, 1)[1]
    # Drop a single leading frontmatter block (e.g. Cursor .mdc header).
    text = re.sub(r"^\s*---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    return text.strip()


def _ingest_slug(source):
    return re.sub(r"[^\w]+", "-", source).strip("-").lower()


def ingest_sources():
    """Scan known rule files and return the user-authored content found in
    each: [{source, content, lines}]. Files that are entirely AIM-generated
    (or absent/empty) are skipped."""
    cli = _cli()
    results = []
    for rel in _ingest_candidates():
        path = os.path.join(cli.ROOT_DIR, rel)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        content = strip_aim_block(raw)
        if content:
            results.append({"source": rel, "content": content,
                            "lines": len(content.splitlines())})
    return results


def imported_dir():
    return os.path.join(_cli().AI_CONTEXT_DIR, "imported")


def apply_ingest(sources=None):
    """Persist collected user content into .ai-context/imported/<slug>.md
    (atomic, one file per source). `aim sync` then re-emits them into every
    client file. Idempotent: re-running rewrites the same content. Returns
    the list of written relative paths."""
    cli = _cli()
    if sources is None:
        sources = ingest_sources()
    out_dir = imported_dir()
    if sources and not os.path.exists(out_dir):
        os.makedirs(out_dir)
    written = []
    for s in sources:
        dest = os.path.join(out_dir, f"{_ingest_slug(s['source'])}.md")
        tmp = f"{dest}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(s["content"].strip() + "\n")
        os.replace(tmp, dest)
        written.append(os.path.relpath(dest, cli.ROOT_DIR).replace("\\", "/"))
    return written


def ingest_emit_payload():
    """For the LLM-inversion path (`aim ingest --emit`): return raw collected
    content plus an instruction for the connected agent to restructure it into
    config.json fields. Keeps AIM zero-dependency (the agent does the parsing)."""
    sources = ingest_sources()
    instruction = (
        "Restructure the rule snippets below into the AIM config at "
        ".ai-context/config.json: merge coding rules into `conventions`, hard "
        "constraints into `constraints`, and tool-specific rules into "
        "`customRules.<client>`. Deduplicate. Then run `aim sync`."
    )
    return {"instruction": instruction, "sources": sources}


# ==========================================
# Diagnostics — `aim doctor`
# ==========================================
SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "info": 0}

# A referenced file is "probably stale" once it has changed this many commits
# since the memory was last reviewed. Tunable; the validation gate is about
# finding a value with good signal/noise on real repos.
STALE_COMMIT_THRESHOLD = 5
UNREVIEWED_DAYS = 90
IDLE_TASK_DAYS = 14


def _parse_iso(value):
    try:
        return datetime.datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _task_last_updated(meta, path):
    """Best-effort 'last touched' time for a task: the '- Last updated:' stamp
    in Notes, else the file mtime."""
    notes = meta.get("notes", "")
    m = re.search(r"Last updated:\s*([0-9:\- ]+)", notes)
    if m:
        try:
            return datetime.datetime.strptime(m.group(1).strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(path))
    except OSError:
        return None


def run_diagnostics(author=None):
    """Inspect the workspace for context-drift signals. Pure data: returns a
    list of findings {severity, kind, message, fix}. `author` (if given)
    filters memory findings to that author (team `--mine` mode)."""
    cli = _cli()
    findings = []
    now = datetime.datetime.now()

    def add(severity, kind, message, fix=None):
        findings.append({"severity": severity, "kind": kind,
                         "message": message, "fix": fix})

    # 1. Broken references
    for err in validate_references():
        ref = f"@task-{err['ref']}" if err["kind"] == "task" else f"@doc/{err['ref']}"
        add("high", "broken-ref",
            f"Broken {err['kind']} link in {err['source']}: {ref} does not exist.")

    # 2. Duplicate / mismatched task IDs (cross-branch merge artifacts)
    seen_ids = {}
    if os.path.exists(cli.TASKS_DIR):
        for filename in sorted(os.listdir(cli.TASKS_DIR)):
            fm = re.match(r"task-(\d+)\.md", filename)
            if not fm:
                continue
            file_id = int(fm.group(1))
            try:
                meta = cli.parse_task_file(os.path.join(cli.TASKS_DIR, filename))
            except (ValueError, OSError):
                continue
            if meta["id"] != file_id:
                add("high", "id-mismatch",
                    f"{filename} declares id {meta['id']} but the filename says {file_id}.",
                    f"aim task renumber {meta['id']} {file_id}")
            seen_ids.setdefault(meta["id"], []).append(filename)
        for tid, files in seen_ids.items():
            if len(files) > 1:
                add("high", "id-duplicate",
                    f"Task id {tid} is claimed by multiple files: {', '.join(files)}.")

    # 3. Stale memories vs. code, and 4. unreviewed memories
    for mem in load_memories():
        if author is not None and mem.get("author") != author:
            continue
        reviewed = mem.get("reviewedAt") or mem.get("createdAt")
        reviewed_dt = _parse_iso(reviewed)
        label = f"Memory #{mem.get('id')} \"{mem.get('content', '')[:48].splitlines()[0]}\""
        for ref in mem.get("refs", []):
            abs_path = os.path.join(cli.ROOT_DIR, ref)
            if not os.path.isfile(abs_path):
                continue
            n = git_commits_since(ref, reviewed)
            if n is not None and n >= STALE_COMMIT_THRESHOLD:
                add("medium", "stale-memory",
                    f"{label} references `{ref}`, which changed {n} commits "
                    f"since last review ({reviewed[:10] if reviewed else '?'}). "
                    f"May be outdated.",
                    f"aim memory review {mem.get('id')}")
        if reviewed_dt and (now - reviewed_dt).days > UNREVIEWED_DAYS:
            add("low", "unreviewed-memory",
                f"{label} has not been reviewed in {(now - reviewed_dt).days} days.",
                f"aim memory review {mem.get('id')}")

    # 5/6. Task health: done-but-spec-changed, and idle in-progress
    tasks, _errs = load_tasks()
    doc_index = {rel: full for rel, full in doc_files()}
    for meta in tasks:
        path = os.path.join(cli.TASKS_DIR, f"task-{meta['id']}.md")
        updated = _task_last_updated(meta, path)
        status = meta.get("status", "todo").lower()
        spec = (meta.get("spec") or "").replace("@doc/", "").strip()
        if status == "done" and spec and updated:
            spec_full = doc_index.get(spec) or doc_index.get(spec + ".md")
            if spec_full:
                n = git_commits_since(os.path.relpath(spec_full, cli.ROOT_DIR),
                                      updated.isoformat())
                if n:
                    add("medium", "spec-drift",
                        f"TASK-{meta['id']} is done but its spec changed {n} commits "
                        f"after the task was last updated — implementation may be out of date.")
        if status == "in-progress" and updated and (now - updated).days > IDLE_TASK_DAYS:
            add("low", "idle-task",
                f"TASK-{meta['id']} has been in-progress with no update for "
                f"{(now - updated).days} days.")

    # 7. Orphans (info) and 8. spec coverage (info)
    referenced = set()
    for _rel, full in doc_files():
        try:
            with open(full, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        referenced.update(int(x) for x in TASK_REF_RE.findall(content))
    for meta in tasks:
        content = cli.render_task_content(meta) if hasattr(cli, "render_task_content") else ""
        referenced.update(int(x) for x in TASK_REF_RE.findall(content))
    no_spec = [m["id"] for m in tasks if not (m.get("spec") or "").strip()]
    if no_spec and tasks:
        add("info", "spec-coverage",
            f"{len(no_spec)}/{len(tasks)} tasks have no spec link "
            f"({len(tasks) - len(no_spec)}/{len(tasks)} covered).")

    # 9. Similar memories (optional [semantic] extra): highly-similar pairs are
    # likely duplicates or contradictions worth a human review.
    try:
        from aim import semantic
    except ImportError:
        import semantic
    if semantic.available():
        mems = [(m["id"], m.get("content", "")) for m in load_memories() if m.get("content")]
        pairs = semantic.similar_pairs(mems) if len(mems) > 1 else None
        for a, b, score in (pairs or []):
            add("low", "similar-memory",
                f"Memories #{a} and #{b} are very similar (score {score}) — "
                f"possible duplicate or contradiction; review/merge.",
                f"aim memory view {a}; aim memory view {b}")

    findings.sort(key=lambda f: -SEVERITY_ORDER.get(f["severity"], 0))
    return findings
