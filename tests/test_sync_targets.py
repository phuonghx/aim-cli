import os

from aim import sync

CONFIG = {
    "projectName": "Demo",
    "projectDescription": "Một dự án thử nghiệm",
    "techStack": ["Python"],
    "conventions": ["PEP8"],
    "constraints": ["Không hardcode secrets"],
    "commands": {"build": "", "test": "pytest", "lint": "ruff check .", "format": ""},
}


def test_sync_targets_include_modern_formats():
    labels = [label for label, _rel, _gen in sync.SYNC_TARGETS]
    assert "AGENTS.md" in labels
    assert "GEMINI.md" in labels
    assert ".cursor/rules/aim.mdc" in labels
    # legacy formats kept for backwards compatibility
    assert ".cursorrules" in labels
    assert "CLAUDE.md" in labels


def test_generate_agents_md_content():
    content = sync.generate_agents_md(CONFIG)
    assert "# AGENTS.md" in content
    assert "Demo" in content
    assert "pytest" in content
    assert "PEP8" in content
    assert "Không hardcode secrets" in content


def test_generate_gemini_md_content():
    content = sync.generate_gemini_md(CONFIG)
    assert "GEMINI.md" in content
    assert "ruff check ." in content


def test_mdc_new_file_has_frontmatter_at_top(tmp_path):
    target = tmp_path / "aim.mdc"
    sync.write_managed_file(str(target), "RULES BODY",
                            header_if_new=sync.CURSOR_MDC_FRONTMATTER)
    content = target.read_text(encoding="utf-8")
    # Cursor requires the frontmatter to be the very first bytes of the file
    assert content.startswith("---\n")
    assert "alwaysApply: true" in content
    assert sync.AIM_BEGIN in content
    assert "RULES BODY" in content

    # Re-sync: frontmatter (outside markers) is preserved, body replaced
    sync.write_managed_file(str(target), "RULES BODY v2",
                            header_if_new=sync.CURSOR_MDC_FRONTMATTER)
    content = target.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert content.count("alwaysApply: true") == 1
    assert "RULES BODY v2" in content
    assert "RULES BODY\n" not in content


def test_full_sync_writes_all_targets(workspace, monkeypatch, capsys):
    import json
    config_path = os.path.join(str(workspace), ".ai-context", "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f)
    monkeypatch.chdir(str(workspace))

    sync.main()

    for _label, rel_path, _gen in sync.SYNC_TARGETS:
        target = os.path.join(str(workspace), rel_path)
        assert os.path.exists(target), rel_path
        with open(target, "r", encoding="utf-8") as f:
            assert sync.AIM_BEGIN in f.read()
