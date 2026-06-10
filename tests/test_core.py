import os

from aim import core


def _write_task(workspace, tid, title="Task", assignee="unassigned", parent=None,
                description="", status="todo"):
    from aim import aim_cli
    meta = {
        "id": tid, "title": title, "status": status, "priority": "medium",
        "assignee": assignee, "parent": parent, "labels": [],
        "spec": "", "plan": "", "description": description, "ac": []
    }
    path = os.path.join(str(workspace), ".ai-context", "tasks", f"task-{tid}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(aim_cli.render_task_content(meta))
    return meta


def test_load_tasks_sorted_and_reports_malformed(workspace):
    _write_task(workspace, 2, "hai")
    _write_task(workspace, 10, "mười")
    _write_task(workspace, 1, "một")
    bad = os.path.join(str(workspace), ".ai-context", "tasks", "task-99.md")
    with open(bad, "w", encoding="utf-8") as f:
        f.write("not a task\n")

    tasks, errors = core.load_tasks()
    assert [t["id"] for t in tasks] == [1, 2, 10]
    assert len(errors) == 1 and "task-99.md" in errors[0]


def test_get_task_rejects_traversal_ids(workspace):
    _write_task(workspace, 1)
    assert core.get_task(1) is not None
    assert core.get_task("1") is not None
    assert core.get_task("../../etc/passwd") is None
    assert core.get_task(42) is None


def test_create_task_allocates_ids(workspace):
    t1 = core.create_task("đầu tiên", ac=["AC 1"])
    t2 = core.create_task("thứ hai", parent=t1["id"])
    assert t1["id"] == 1
    assert t2["id"] == 2
    assert t2["parent"] == 1
    reread = core.get_task(1)
    assert reread["title"] == "đầu tiên"
    assert len(reread["ac"]) == 1


def test_search_workspace_types(workspace):
    _write_task(workspace, 1, "Tối ưu SEO", description="meta tags cho trang chủ")
    docs_dir = os.path.join(str(workspace), ".ai-context", "docs")
    with open(os.path.join(docs_dir, "seo-guide.md"), "w", encoding="utf-8") as f:
        f.write("# SEO Guide\nHướng dẫn SEO chi tiết.\n")
    core.add_memory("Luôn kiểm tra SEO trước khi release", "decision", "project")

    results = core.search_workspace("seo")
    types = sorted(r["type"] for r in results)
    assert types == ["doc", "memory", "task"]
    task_result = next(r for r in results if r["type"] == "task")
    assert task_result["ref"] == "@task-1"
    assert task_result["title"] == "Tối ưu SEO"
    mem_result = next(r for r in results if r["type"] == "memory")
    assert mem_result["category"] == "decision"

    assert core.search_workspace("") == []
    assert core.search_workspace("khongtontai") == []


def test_validate_references_structured(workspace):
    _write_task(workspace, 1, description="xem @task-2 và @doc/missing.md")
    errors = core.validate_references()
    kinds = sorted(e["kind"] for e in errors)
    assert kinds == ["doc", "task"]
    task_err = next(e for e in errors if e["kind"] == "task")
    assert task_err["ref"] == "2"
    assert task_err["source"] == "task file task-1.md"


def test_add_memory_and_load(workspace):
    new_mem, memories = core.add_memory("ghi nhớ một", "pattern", None)
    assert new_mem["id"] == 1
    assert new_mem["layer"] == "project"
    new_mem2, memories = core.add_memory("ghi nhớ hai")
    assert new_mem2["id"] == 2
    assert len(core.load_memories()) == 2


def test_rename_user_propagate(workspace):
    _write_task(workspace, 1, assignee="alice")
    _write_task(workspace, 2, assignee="bob")
    _write_task(workspace, 3, assignee="alice")

    updated, errors = core.rename_user_propagate("alice", "charlie")
    assert updated == 2
    assert errors == []
    assert core.get_task(1)["assignee"] == "charlie"
    assert core.get_task(2)["assignee"] == "bob"


def test_collect_status_shape(workspace):
    _write_task(workspace, 1, status="in-progress")
    _write_task(workspace, 2, status="blocked")
    core.add_memory("note")

    status = core.collect_status()
    assert len(status["tasks"]) == 2
    assert status["statusCounts"]["in-progress"] == 1
    assert status["statusCounts"]["blocked"] == 1  # dynamic statuses tracked too
    assert status["docsCount"] == 0
    assert len(status["memories"]) == 1
    assert status["activeTimer"] is None
    assert "CLAUDE.md" in status["syncStatuses"]
    assert "AGENTS.md" in status["syncStatuses"]
    assert status["allSynced"] is False
