import os

from aim import aim_cli, core


def _write_task(workspace, tid, title="Task", status="todo", spec="", notes=None):
    meta = {
        "id": tid, "title": title, "status": status, "priority": "medium",
        "assignee": "unassigned", "parent": None, "labels": [],
        "spec": spec, "plan": "", "description": "", "ac": [],
    }
    content = aim_cli.render_task_content(meta)
    if notes:
        content = content.replace("## Notes\n", f"## Notes\n{notes}\n")
    path = os.path.join(str(workspace), ".ai-context", "tasks", f"task-{tid}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------- Phase 0: memory model ----------

def test_extract_refs():
    refs = core.extract_refs(
        "Auth lives in `aim/auth.py`; see @task-3 and @doc/api/auth.md. "
        "Plain prose with no path. Also src/lib/http.ts matters."
    )
    assert "aim/auth.py" in refs
    assert "@task-3" in refs
    assert "@doc/api/auth.md" in refs
    assert "src/lib/http.ts" in refs
    # no false positive on bare words
    assert "prose" not in refs


def test_add_memory_has_new_fields(workspace, monkeypatch):
    monkeypatch.setattr(core, "current_author", lambda: "alice")
    mem, _ = core.add_memory("Use `src/lib/http.ts` not axios", "decision")
    assert mem["author"] == "alice"
    assert mem["status"] == "active"
    assert mem["createdAt"] == mem["reviewedAt"]
    assert "src/lib/http.ts" in mem["refs"]


def test_memory_edit_delete_review(workspace):
    mem, _ = core.add_memory("first", "general")
    mid = mem["id"]

    updated = core.update_memory(mid, content="now mentions `aim/core.py`")
    assert "aim/core.py" in updated["refs"]

    before = core.review_memory(mid)["reviewedAt"]
    assert before is not None

    assert core.delete_memory(mid) is True
    assert core.delete_memory(mid) is False
    assert core.get_task is not None  # sanity
    assert all(m["id"] != mid for m in core.load_memories())


def test_global_layer_separate_store_shared_ids(workspace):
    p, _ = core.add_memory("project mem", "general", layer="project")
    g, _ = core.add_memory("global mem", "general", layer="global")
    assert p["id"] == 1 and g["id"] == 2          # ids unique across stores
    # global store written outside the project .ai-context
    assert os.path.exists(aim_cli.GLOBAL_MEMORIES_PATH)
    mems = {m["id"]: m["layer"] for m in core.load_memories()}
    assert mems == {1: "project", 2: "global"}


def test_record_correction(workspace):
    mem, _ = core.record_correction(
        "used axios directly", "use the fetch wrapper in `src/lib/http.ts`")
    assert mem["category"] == "correction"
    assert "src/lib/http.ts" in mem["refs"]
    assert "axios" in mem["content"]


# ---------- Phase 1: aim doctor ----------

def test_doctor_clean_workspace(workspace):
    findings = core.run_diagnostics()
    assert findings == []


def test_doctor_flags_broken_ref(workspace):
    _write_task(workspace, 1, "t", notes="See @doc/missing.md\n")
    findings = core.run_diagnostics()
    assert any(f["kind"] == "broken-ref" and f["severity"] == "high" for f in findings)


def test_doctor_flags_stale_memory_via_git(workspace, monkeypatch):
    # a real file the memory references
    src = os.path.join(str(workspace), "auth.py")
    with open(src, "w", encoding="utf-8") as f:
        f.write("# auth\n")
    core.add_memory("Auth rules live in `auth.py`", "decision")
    # git seam reports the file changed a lot since review
    monkeypatch.setattr(core, "git_commits_since", lambda path, since: 42)

    findings = core.run_diagnostics()
    stale = [f for f in findings if f["kind"] == "stale-memory"]
    assert stale and stale[0]["severity"] == "medium"
    assert "42 commits" in stale[0]["message"]
    assert stale[0]["fix"].startswith("aim memory review")


def test_doctor_no_stale_when_git_unavailable(workspace, monkeypatch):
    src = os.path.join(str(workspace), "auth.py")
    with open(src, "w", encoding="utf-8") as f:
        f.write("# auth\n")
    core.add_memory("Auth rules live in `auth.py`", "decision")
    monkeypatch.setattr(core, "git_commits_since", lambda path, since: None)
    assert not any(f["kind"] == "stale-memory" for f in core.run_diagnostics())


def test_doctor_flags_duplicate_and_mismatched_ids(workspace):
    tasks_dir = os.path.join(str(workspace), ".ai-context", "tasks")
    # filename says 5 but header says 6 -> mismatch
    meta = {"id": 6, "title": "x", "status": "todo", "priority": "medium",
            "assignee": "unassigned", "parent": None, "labels": [],
            "spec": "", "plan": "", "description": "", "ac": []}
    with open(os.path.join(tasks_dir, "task-5.md"), "w", encoding="utf-8") as f:
        f.write(aim_cli.render_task_content(meta))
    findings = core.run_diagnostics()
    assert any(f["kind"] == "id-mismatch" for f in findings)


def test_doctor_mine_filters_by_author(workspace, monkeypatch):
    monkeypatch.setattr(core, "git_commits_since", lambda path, since: 99)
    src = os.path.join(str(workspace), "f.py")
    open(src, "w").close()
    core.add_memory("touches `f.py`", "x", author="alice")
    core.add_memory("touches `f.py`", "x", author="bob")

    mine = core.run_diagnostics(author="alice")
    stale = [f for f in mine if f["kind"] == "stale-memory"]
    assert len(stale) == 1  # only alice's


def test_doctor_unreviewed_memory(workspace, monkeypatch):
    mem, _ = core.add_memory("old decision", "decision")
    # backdate reviewedAt by editing the store directly
    store = core._load_store("project")
    store[0]["reviewedAt"] = "2020-01-01T00:00:00"
    aim_cli.save_json(aim_cli.MEMORIES_PATH, store)
    findings = core.run_diagnostics()
    assert any(f["kind"] == "unreviewed-memory" for f in findings)
