import json
import os

import pytest

from aim import aim_cli
from aim import sync


def test_format_duration():
    assert aim_cli.format_duration(0) == "0s"
    assert aim_cli.format_duration(59) == "59s"
    assert aim_cli.format_duration(60) == "1m 0s"
    assert aim_cli.format_duration(3661) == "1h 1m 1s"
    # Negative durations (clock skew) clamp to zero instead of garbage
    assert aim_cli.format_duration(-50) == "0s"


def test_case_helpers():
    assert aim_cli.kebab_case("MyComponent") == "my-component"
    assert aim_cli.camel_case("my component") == "myComponent"
    assert aim_cli.pascal_case("my-component") == "MyComponent"
    assert aim_cli.snake_case("MyComponent") == "my_component"


def test_render_template_string():
    out = aim_cli.render_template_string(
        "{{pascalCase name}}.{{ext}} // {{kebabCase name}}",
        {"name": "user profile", "ext": "ts"})
    assert out == "UserProfile.ts // user-profile"


def test_save_json_atomic_and_load_json_backs_up_corrupt(tmp_path, capsys):
    target = tmp_path / "store.json"
    aim_cli.save_json(str(target), {"a": 1})
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 1}
    # no stray temp files left behind
    assert [p.name for p in tmp_path.iterdir()] == ["store.json"]

    # Corrupt file: returns default AND keeps a backup instead of losing data
    target.write_text("{truncated", encoding="utf-8")
    result = aim_cli.load_json(str(target), [])
    assert result == []
    backups = [p for p in tmp_path.iterdir() if "corrupt" in p.name]
    assert backups, "corrupt store must be backed up"
    assert backups[0].read_text(encoding="utf-8") == "{truncated"


def test_parse_yaml_list_items_do_not_merge():
    cfg = aim_cli.parse_yaml(
        "name: demo\n"
        "prompts:\n"
        "  - name: first\n"
        "    type: text\n"
        "    message: \"First?\"\n"
        "  - name: second\n"
        "    type: text\n"
        "actions:\n"
        "  - type: add\n"
        "    template: \"a.hbs\"\n"
        "    path: \"a.ts\"\n"
        "  - type: add\n"
        "    template: \"b.hbs\"\n"
        "    path: \"b.ts\"\n"
    )
    assert len(cfg["prompts"]) == 2
    assert cfg["prompts"][0]["name"] == "first"
    assert cfg["prompts"][0]["message"] == "First?"
    assert cfg["prompts"][1]["name"] == "second"
    assert len(cfg["actions"]) == 2
    assert cfg["actions"][0]["template"] == "a.hbs"
    assert cfg["actions"][1]["template"] == "b.hbs"


def test_parse_yaml_keeps_hash_inside_values():
    cfg = aim_cli.parse_yaml('name: demo\ndescription: "color #fff is fine"  # trailing comment\n')
    assert cfg["description"] == "color #fff is fine"


def test_validate_regex_no_false_positive_on_prose(workspace, capsys):
    docs_dir = os.path.join(str(workspace), ".ai-context", "docs")
    with open(os.path.join(docs_dir, "guide.md"), "w", encoding="utf-8") as f:
        f.write("# Guide\nSee @doc/guide.md and read it.\nPlain prose with spaces after.\n")

    class Args:
        pass

    aim_cli.cmd_validate(Args())
    out = capsys.readouterr().out
    assert "Broken doc link" not in out
    assert "All references are healthy" in out


def test_validate_detects_real_broken_links(workspace, capsys):
    docs_dir = os.path.join(str(workspace), ".ai-context", "docs")
    with open(os.path.join(docs_dir, "guide.md"), "w", encoding="utf-8") as f:
        f.write("# Guide\nBroken: @doc/missing.md and @task-99\n")

    class Args:
        pass

    with pytest.raises(SystemExit) as exc:
        aim_cli.cmd_validate(Args())
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "@task-99" in out
    assert "missing.md" in out


def test_sync_write_managed_file_preserves_user_content(tmp_path):
    target = tmp_path / "CLAUDE.md"
    target.write_text("# Ghi chú của tôi\nkhông được xóa\n", encoding="utf-8")

    sync.write_managed_file(str(target), "GENERATED v1")
    content = target.read_text(encoding="utf-8")
    assert "Ghi chú của tôi" in content
    assert "GENERATED v1" in content
    assert (tmp_path / "CLAUDE.md.bak").exists()

    # Re-sync replaces only the managed block, idempotently
    sync.write_managed_file(str(target), "GENERATED v2")
    content = target.read_text(encoding="utf-8")
    assert "Ghi chú của tôi" in content
    assert "GENERATED v2" in content
    assert "GENERATED v1" not in content
    assert content.count(sync.AIM_BEGIN) == 1
