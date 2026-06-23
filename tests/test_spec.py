import os

import pytest

from aim import core


def test_tasks_without_spec_and_coverage(workspace):
    core.create_task("no spec one")                          # 1
    core.create_task("has spec", spec="@doc/specs/x.md")     # 2
    core.create_task("no spec two")                          # 3

    assert core.tasks_without_spec() == [1, 3]
    cov = core.spec_coverage()
    assert cov == {"total": 3, "withSpec": 1, "withoutSpec": [1, 3]}


def _make_speckit_dir(tmp_path, with_plan=True):
    d = tmp_path / "feature-auth"
    d.mkdir()
    (d / "spec.md").write_text("# User Authentication\nSpec body.\n", encoding="utf-8")
    if with_plan:
        (d / "plan.md").write_text("# Plan\nImplementation plan.\n", encoding="utf-8")
    return d


def test_import_spec_creates_docs_and_task(workspace, tmp_path):
    d = _make_speckit_dir(tmp_path)
    result = core.import_spec(str(d))

    assert result["specDoc"] == "specs/feature-auth.md"
    assert result["planDoc"] == "plans/feature-auth.md"

    docs_dir = os.path.join(str(workspace), ".ai-context", "docs")
    assert os.path.isfile(os.path.join(docs_dir, "specs", "feature-auth.md"))
    assert os.path.isfile(os.path.join(docs_dir, "plans", "feature-auth.md"))

    task = core.get_task(result["taskId"])
    assert task["title"] == "Implement: User Authentication"   # H1 from spec
    assert task["spec"] == "@doc/specs/feature-auth.md"
    assert task["plan"] == "@doc/plans/feature-auth.md"


def test_import_spec_without_plan(workspace, tmp_path):
    d = _make_speckit_dir(tmp_path, with_plan=False)
    result = core.import_spec(str(d))
    assert "planDoc" not in result
    assert core.get_task(result["taskId"])["plan"] == ""


def test_import_spec_requires_spec_md(workspace, tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    with pytest.raises(ValueError):
        core.import_spec(str(d))


def test_imported_spec_passes_validate(workspace, tmp_path):
    # The umbrella task's @doc spec link must resolve (no broken-ref error).
    d = _make_speckit_dir(tmp_path)
    core.import_spec(str(d))
    assert core.validate_references() == []


def test_require_spec_validation(workspace, tmp_path):
    core.create_task("loose task")  # no spec
    d = _make_speckit_dir(tmp_path)
    core.import_spec(str(d))         # creates a task WITH a spec
    missing = core.tasks_without_spec()
    assert 1 in missing             # the loose task
    # the imported umbrella task has a spec, so it is not in the missing list
    assert len(missing) == 1
