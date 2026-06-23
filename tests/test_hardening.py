"""Regression tests for hardening fixes:
- empty/whitespace memory content is rejected (and never crashes `doctor`)
- `doc view` / template `run` refuse to escape their base directory
- GitHub issue body tolerates acceptance criteria missing a `text` key
"""
import os

import pytest

from aim import aim_cli, core


# ---------- empty memory content ----------

def test_add_memory_rejects_empty(workspace):
    with pytest.raises(ValueError):
        core.add_memory("", "general")
    with pytest.raises(ValueError):
        core.add_memory("   \n\t ", "general")
    assert core.load_memories() == []


def test_add_memory_strips_whitespace(workspace):
    mem, _ = core.add_memory("  spaced out  ", "general")
    assert mem["content"] == "spaced out"


def test_update_memory_rejects_empty(workspace):
    mem, _ = core.add_memory("real content", "general")
    with pytest.raises(ValueError):
        core.update_memory(mem["id"], content="   ")
    # original content is preserved
    current = {m["id"]: m for m in core.load_memories()}[mem["id"]]
    assert current["content"] == "real content"


def test_doctor_survives_legacy_empty_memory(workspace, monkeypatch):
    """A memory with empty content already on disk (legacy data) must not
    crash run_diagnostics — previously raised IndexError on .splitlines()[0]."""
    monkeypatch.setattr(core, "current_author", lambda: "alice")
    # Inject an empty-content memory directly (bypassing the new guard) to
    # simulate a store written by an older AIM version.
    store = [{
        "id": 1, "content": "", "category": "general", "layer": "project",
        "author": "alice", "createdAt": "2020-01-01T00:00:00",
        "reviewedAt": "2020-01-01T00:00:00", "status": "active", "refs": [],
    }]
    aim_cli.save_json(aim_cli.MEMORIES_PATH, store)
    findings = core.run_diagnostics()  # must not raise
    assert isinstance(findings, list)


# ---------- path containment ----------

def test_doc_view_blocks_traversal(workspace, capsys):
    # secret .md outside the docs dir, at the workspace root
    secret = os.path.join(str(workspace), "secret.md")
    with open(secret, "w", encoding="utf-8") as f:
        f.write("TOP SECRET")

    class Args:
        doc_action = "view"
        path = "../../secret"
    with pytest.raises(SystemExit):
        aim_cli.cmd_doc(Args())
    out = capsys.readouterr().out
    assert "TOP SECRET" not in out
    assert "Refusing to read outside" in out


def test_is_within_helper(workspace):
    base = aim_cli.DOCS_DIR
    assert aim_cli._is_within(base, os.path.join(base, "a", "b.md"))
    assert aim_cli._is_within(base, base)
    assert not aim_cli._is_within(base, os.path.join(base, "..", "..", "escape.md"))


# ---------- github body tolerance ----------

def test_task_to_issue_body_tolerates_ac_without_text():
    task = {
        "id": 1, "title": "t", "description": "desc",
        "ac": [{"checked": False}, {"text": "real one", "checked": True}],
        "dependsOn": [],
    }
    body = core.task_to_issue_body(task)  # must not raise KeyError
    assert "real one" in body
    assert "task-1" in body
