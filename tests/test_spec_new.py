"""Tests for `aim spec new` — scaffolding requirements/design/tasks with EARS."""
import os

import pytest

from aim import aim_cli, core


def _spec_path(slug, fname):
    return os.path.join(aim_cli.DOCS_DIR, "specs", slug, fname)


def test_create_spec_scaffolds_files_and_task(workspace):
    result = core.create_spec("User Auth Flow")
    assert result["slug"] == "user-auth-flow"
    for fname in ("requirements.md", "design.md", "tasks.md"):
        assert os.path.isfile(_spec_path("user-auth-flow", fname))

    with open(_spec_path("user-auth-flow", "requirements.md"), encoding="utf-8") as f:
        req = f.read()
    assert "THE SYSTEM SHALL" in req      # EARS notation present
    assert "User Auth Flow" in req

    assert result["taskId"] is not None
    task = core.get_task(result["taskId"])
    assert task["spec"] == "@doc/specs/user-auth-flow/requirements.md"


def test_create_spec_no_task(workspace):
    result = core.create_spec("No Task Spec", with_task=False)
    assert result["taskId"] is None
    assert os.path.isfile(_spec_path("no-task-spec", "design.md"))


def test_create_spec_rejects_duplicate(workspace):
    core.create_spec("dup")
    with pytest.raises(ValueError):
        core.create_spec("dup")


def test_create_spec_rejects_empty(workspace):
    with pytest.raises(ValueError):
        core.create_spec("   ")


def test_new_spec_is_covered(workspace):
    core.create_spec("Covered Feature")
    cov = core.spec_coverage()
    assert cov["withSpec"] >= 1
