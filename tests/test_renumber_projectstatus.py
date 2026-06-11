import json
import os

import pytest

from aim import aim_cli, core


# ---------- issue #10: aim task renumber ----------

def test_renumber_moves_file_and_updates_header(workspace):
    core.create_task("alpha")  # 1
    res = core.renumber_task(1, 50)
    assert res["new"] == 50
    assert not os.path.exists(f"{aim_cli.TASKS_DIR}/task-1.md")
    moved = core.get_task(50)
    assert moved["id"] == 50 and moved["title"] == "alpha"


def test_renumber_rewrites_refs_deps_parent_and_docs(workspace):
    core.create_task("base")                       # 1
    core.create_task("child", parent=1)            # 2  parent=1
    core.create_task("dependent", depends_on=[1])  # 3  dependsOn=[1]
    # a task whose description references @task-1
    core.create_task("mentions", description="see @task-1 for context")  # 4
    # a doc that references @task-1 and @task-10 (must not clobber task-10)
    docs = os.path.join(str(workspace), ".ai-context", "docs")
    with open(os.path.join(docs, "notes.md"), "w", encoding="utf-8") as f:
        f.write("Depends on @task-1 and also @task-10 unrelated.\n")

    res = core.renumber_task(1, 99)
    assert res["filesUpdated"] >= 4

    assert core.get_task(2)["parent"] == 99
    assert core.get_task(3)["dependsOn"] == [99]
    assert "@task-99" in core.get_task(4)["description"]
    with open(os.path.join(docs, "notes.md"), encoding="utf-8") as f:
        doc = f.read()
    assert "@task-99" in doc
    assert "@task-10 unrelated" in doc        # word boundary respected


def test_renumber_rejects_taken_or_missing(workspace):
    core.create_task("a")  # 1
    core.create_task("b")  # 2
    with pytest.raises(ValueError):
        core.renumber_task(1, 2)        # target taken
    with pytest.raises(ValueError):
        core.renumber_task(7, 8)        # source missing
    with pytest.raises(ValueError):
        core.renumber_task(1, 1)        # same id


# ---------- issue #8: sync Project Status field ----------

def test_sync_project_status_maps_status_to_option(workspace, monkeypatch):
    # two tasks linked to issues, different statuses
    def _link(title, issue, status="todo"):
        t = core.create_task(title, status=status)
        full = core.get_task(t["id"])
        full["githubIssue"] = issue
        aim_cli.write_task_file(full)

    _link("todo task", 7)                 # 1 -> issue 7, todo
    _link("done task", 8, status="done")  # 2 -> issue 8, done

    edits = []

    def fake_gh(args, input_text=None):
        if args[:2] == ["repo", "view"]:
            return "phuonghx/aim-cli\n"
        if args[:2] == ["project", "view"]:
            return json.dumps({"id": "PROJ"})
        if args[:2] == ["project", "field-list"]:
            return json.dumps({"fields": [
                {"name": "Title"},
                {"name": "Status", "id": "FLD", "options": [
                    {"name": "Todo", "id": "OPT_TODO"},
                    {"name": "In Progress", "id": "OPT_IP"},
                    {"name": "Done", "id": "OPT_DONE"},
                ]},
            ]})
        if args[:2] == ["project", "item-list"]:
            return json.dumps({"items": [
                {"id": "ITEM7", "content": {"number": 7}},
                {"id": "ITEM8", "content": {"number": 8}},
            ]})
        if args[:2] == ["project", "item-edit"]:
            edits.append(args)
            return ""
        return ""

    monkeypatch.setattr(core, "_gh", fake_gh)
    n = core.sync_project_status(3)
    assert n == 2
    # task1 (todo) -> Todo option, task2 (done) -> Done option
    def opt_for(item):
        for e in edits:
            if "--id" in e and e[e.index("--id") + 1] == item:
                return e[e.index("--single-select-option-id") + 1]
    assert opt_for("ITEM7") == "OPT_TODO"
    assert opt_for("ITEM8") == "OPT_DONE"


def test_sync_project_status_noop_without_status_field(workspace, monkeypatch):
    def fake_gh(args, input_text=None):
        if args[:2] == ["repo", "view"]:
            return "phuonghx/aim-cli\n"
        if args[:2] == ["project", "view"]:
            return json.dumps({"id": "PROJ"})
        if args[:2] == ["project", "field-list"]:
            return json.dumps({"fields": [{"name": "Title"}]})  # no Status
        return json.dumps({"items": []})
    monkeypatch.setattr(core, "_gh", fake_gh)
    assert core.sync_project_status(3) == 0
