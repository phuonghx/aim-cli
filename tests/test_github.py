from aim import aim_cli, core


# ---------- task model: githubIssue round-trip ----------

def test_github_issue_roundtrip(workspace):
    t = core.create_task("syncable")
    full = core.get_task(t["id"])
    full["githubIssue"] = 42
    aim_cli.write_task_file(full)
    reread = core.get_task(t["id"])
    assert reread["githubIssue"] == 42
    with open(f"{aim_cli.TASKS_DIR}/task-{t['id']}.md", encoding="utf-8") as f:
        assert "**GitHub Issue:** #42" in f.read()


# ---------- pure helpers ----------

def test_parse_issue_number():
    assert core.parse_issue_number("https://github.com/o/r/issues/57\n") == 57
    assert core.parse_issue_number("nope") is None


def test_task_to_issue_body():
    task = {"id": 3, "title": "X", "description": "Do the thing",
            "ac": [{"text": "works", "checked": True}, {"text": "tested", "checked": False}],
            "dependsOn": [1, 2]}
    body = core.task_to_issue_body(task)
    assert "Do the thing" in body
    assert "- [x] works" in body
    assert "- [ ] tested" in body
    assert "AIM task-1" in body
    assert "<!-- aim-task:3 -->" in body


# ---------- push_task with a mocked gh seam ----------

def test_push_task_creates_and_stores_issue(workspace, monkeypatch):
    core.create_task("first")  # id 1
    calls = []

    def fake_gh(args, input_text=None):
        calls.append(args)
        if args[:2] == ["issue", "create"]:
            return "https://github.com/phuonghx/aim-cli/issues/101\n"
        return ""

    monkeypatch.setattr(core, "_gh", fake_gh)
    result = core.push_task(1)
    assert result["action"] == "created"
    assert result["issue"] == 101
    # stored back into the task file
    assert core.get_task(1)["githubIssue"] == 101
    # opened (status not done -> reopen attempted)
    assert any(a[:2] == ["issue", "reopen"] for a in calls)


def test_push_task_updates_when_linked_and_closes_done(workspace, monkeypatch):
    core.create_task("done task", status="done")  # id 1
    full = core.get_task(1)
    full["githubIssue"] = 55
    aim_cli.write_task_file(full)
    calls = []
    monkeypatch.setattr(core, "_gh", lambda args, input_text=None: calls.append(args) or "")

    result = core.push_task(1)
    assert result["action"] == "updated"
    assert result["issue"] == 55
    assert any(a == ["issue", "edit", "55", "--title", core._issue_title(core.get_task(1)),
                     "--body", core.task_to_issue_body(core.get_task(1))] for a in calls)
    assert any(a[:3] == ["issue", "close", "55"] for a in calls)  # done -> closed


def test_github_status(workspace, monkeypatch):
    core.create_task("a")
    b = core.create_task("b")
    full = core.get_task(b["id"])
    full["githubIssue"] = 7
    aim_cli.write_task_file(full)
    rows = {r["taskId"]: r for r in core.github_status()}
    assert rows[1]["issue"] is None
    assert rows[2]["issue"] == 7


def test_create_project_parses_json(workspace, monkeypatch):
    def fake_gh(args, input_text=None):
        if args[:2] == ["repo", "view"]:
            return "phuonghx/aim-cli\n"
        if args[:2] == ["project", "create"]:
            return '{"number": 9, "url": "https://github.com/users/phuonghx/projects/9"}'
        return ""
    monkeypatch.setattr(core, "_gh", fake_gh)
    data = core.create_project("AIM Roadmap")
    assert data["number"] == 9
