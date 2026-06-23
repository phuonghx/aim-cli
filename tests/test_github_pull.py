from aim import aim_cli, core


def _link(title, issue, status="todo"):
    t = core.create_task(title, status=status)
    full = core.get_task(t["id"])
    full["githubIssue"] = issue
    aim_cli.write_task_file(full)
    return t["id"]


def test_issue_to_updates_state_and_title():
    task = {"title": "Old title", "status": "todo"}
    # closed issue -> done
    assert core.issue_to_updates(task, {"title": "[AIM-1] Old title", "state": "CLOSED"}) == {"status": "done"}
    # title change (prefix stripped)
    assert core.issue_to_updates(task, {"title": "[AIM-1] New title", "state": "OPEN"}) == {"title": "New title"}
    # reopened while AIM says done -> back to todo
    done = {"title": "X", "status": "done"}
    assert core.issue_to_updates(done, {"title": "[AIM-1] X", "state": "OPEN"}) == {"status": "todo"}
    # no change
    assert core.issue_to_updates(task, {"title": "[AIM-1] Old title", "state": "OPEN"}) == {}


def test_pull_task_applies_changes(workspace, monkeypatch):
    tid = _link("Old title", 7, status="todo")
    monkeypatch.setattr(core, "_read_issue",
                        lambda issue: {"number": 7, "title": "[AIM-1] Renamed via GitHub", "state": "CLOSED"})
    res = core.pull_task(tid)
    assert res["changes"] == {"title": "Renamed via GitHub", "status": "done"}
    reread = core.get_task(tid)
    assert reread["title"] == "Renamed via GitHub"
    assert reread["status"] == "done"


def test_pull_task_dry_run_does_not_write(workspace, monkeypatch):
    tid = _link("Stay", 8, status="todo")
    monkeypatch.setattr(core, "_read_issue",
                        lambda issue: {"number": 8, "title": "[AIM-1] Stay", "state": "CLOSED"})
    res = core.pull_task(tid, dry_run=True)
    assert res["changes"] == {"status": "done"}
    assert core.get_task(tid)["status"] == "todo"   # unchanged on disk


def test_pull_all_only_linked(workspace, monkeypatch):
    _link("linked", 9, status="todo")
    core.create_task("unlinked")  # no githubIssue
    monkeypatch.setattr(core, "_read_issue",
                        lambda issue: {"number": issue, "title": "[AIM-1] linked", "state": "CLOSED"})
    results = core.pull_all()
    assert len(results) == 1            # only the linked task
    assert results[0]["changes"] == {"status": "done"}


def test_pull_preserves_ac_and_deps(workspace, monkeypatch):
    # AIM stays canonical for AC/deps; pull must not touch them.
    t = core.create_task("keep", ac=["criterion"], depends_on=None)
    full = core.get_task(t["id"])
    full["githubIssue"] = 5
    aim_cli.write_task_file(full)
    monkeypatch.setattr(core, "_read_issue",
                        lambda issue: {"number": 5, "title": "[AIM-1] keep", "state": "CLOSED"})
    core.pull_task(t["id"])
    reread = core.get_task(t["id"])
    assert reread["status"] == "done"
    assert len(reread["ac"]) == 1 and reread["ac"][0]["text"] == "criterion"
