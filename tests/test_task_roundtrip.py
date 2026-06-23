import os

from aim import aim_cli

SAMPLE_TASK = """# Task 7: Tối ưu SEO trang chủ

**Status:** in-progress
**Priority:** high
**Assignee:** alice
**Time Spent:** 120 seconds
**Parent Task:** none
**Labels:** seo, frontend
**Spec:** none
**Plan:** none

## Description
Mô tả nhiều dòng.

Checklist nằm trong description, KHÔNG phải AC:
- [ ] mục checklist trong mô tả

### Tiểu mục
Nội dung tiểu mục không được cắt mất.

## Acceptance Criteria
- [x] AC một
- [/] AC đang làm dở
- [ ] AC chưa làm

## Custom Section
Người dùng tự thêm, phải được giữ nguyên.

## Notes
- Ghi chú quan trọng của người dùng
- Last updated: 2026-01-01 00:00:00
"""


def write_sample(workspace):
    path = os.path.join(str(workspace), ".ai-context", "tasks", "task-7.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(SAMPLE_TASK)
    return path


def test_parse_scopes_ac_to_section(workspace):
    path = write_sample(workspace)
    meta = aim_cli.parse_task_file(path)
    assert meta["id"] == 7
    assert meta["title"] == "Tối ưu SEO trang chủ"
    # Only the 3 checkboxes inside ## Acceptance Criteria, never the one in Description
    assert len(meta["ac"]) == 3
    assert meta["ac"][0]["checked"] is True
    assert meta["ac"][1]["checked"] is False
    assert meta["ac"][1]["state"] == "/"
    assert meta["ac"][2]["checked"] is False


def test_parse_description_keeps_subheadings(workspace):
    path = write_sample(workspace)
    meta = aim_cli.parse_task_file(path)
    assert "Tiểu mục" in meta["description"]
    assert "mục checklist trong mô tả" in meta["description"]


def test_roundtrip_preserves_notes_and_unknown_sections(workspace):
    path = write_sample(workspace)
    meta = aim_cli.parse_task_file(path)
    aim_cli.write_task_file(meta)
    reparsed = aim_cli.parse_task_file(path)

    assert "Ghi chú quan trọng của người dùng" in reparsed["notes"]
    headers = [s["header"] for s in reparsed["extraSections"]]
    assert "Custom Section" in headers
    # In-progress AC state survives the round-trip
    assert reparsed["ac"][1]["state"] == "/"
    # Description checkbox did not migrate into ACs
    assert len(reparsed["ac"]) == 3
    assert reparsed["description"] == meta["description"]


def test_roundtrip_is_fixed_point(workspace):
    path = write_sample(workspace)
    meta1 = aim_cli.parse_task_file(path)
    aim_cli.write_task_file(meta1)
    meta2 = aim_cli.parse_task_file(path)
    aim_cli.write_task_file(meta2)
    meta3 = aim_cli.parse_task_file(path)
    for key in ("id", "title", "status", "priority", "assignee", "labels",
                "description", "notes", "extraSections"):
        assert meta2[key] == meta3[key], key
    assert [(a["state"], a["text"]) for a in meta2["ac"]] == \
           [(a["state"], a["text"]) for a in meta3["ac"]]


def test_malformed_task_file_raises(workspace):
    path = os.path.join(str(workspace), ".ai-context", "tasks", "task-9.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("just some text, not a task\n")
    try:
        aim_cli.parse_task_file(path)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_create_task_file_skips_existing_id(workspace):
    write_sample(workspace)
    meta = {
        "id": 7, "title": "đụng id", "status": "todo", "priority": "medium",
        "assignee": "unassigned", "parent": None, "labels": [],
        "spec": "", "plan": "", "description": "", "ac": []
    }
    allocated = aim_cli.create_task_file(meta)
    assert allocated == 8
    assert os.path.exists(os.path.join(str(workspace), ".ai-context", "tasks", "task-8.md"))
    # original task untouched
    original = aim_cli.parse_task_file(
        os.path.join(str(workspace), ".ai-context", "tasks", "task-7.md"))
    assert original["title"] == "Tối ưu SEO trang chủ"


def test_detect_parent_cycle(workspace):
    tasks_dir = os.path.join(str(workspace), ".ai-context", "tasks")
    for tid, parent in ((1, None), (2, 1), (3, 2)):
        meta = {
            "id": tid, "title": f"t{tid}", "status": "todo", "priority": "medium",
            "assignee": "unassigned", "parent": parent, "labels": [],
            "spec": "", "plan": "", "description": "", "ac": []
        }
        with open(os.path.join(tasks_dir, f"task-{tid}.md"), "w", encoding="utf-8") as f:
            f.write(aim_cli.render_task_content(meta))

    assert aim_cli.detect_parent_cycle(1, 1) is True       # self-parent
    assert aim_cli.detect_parent_cycle(1, 3) is True       # 1 -> 3 -> 2 -> 1
    assert aim_cli.detect_parent_cycle(3, 1) is False      # already its ancestor, no cycle
    assert aim_cli.detect_parent_cycle(2, None) is False
