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

    findings.sort(key=lambda f: -SEVERITY_ORDER.get(f["severity"], 0))
    return findings
