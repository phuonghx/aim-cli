import os

from aim import core, sync


def _write(workspace, rel, content):
    path = os.path.join(str(workspace), rel)
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(rel) else None
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_strip_aim_block_removes_managed_and_frontmatter():
    text = (
        "---\ndescription: x\n---\n\n"
        "# My rules\nUser content here.\n\n"
        f"{sync.AIM_BEGIN}\ngenerated stuff\n{sync.AIM_END}\n"
    )
    out = core.strip_aim_block(text)
    assert "User content here." in out
    assert "generated stuff" not in out
    assert "description: x" not in out


def test_ingest_collects_user_content(workspace):
    _write(workspace, "CLAUDE.md", "# Style\nUse tabs, not spaces.\n")
    _write(workspace, ".cursorrules", "Prefer composition over inheritance.\n")
    sources = {s["source"]: s for s in core.ingest_sources()}
    assert "CLAUDE.md" in sources
    assert "tabs" in sources["CLAUDE.md"]["content"]
    assert ".cursorrules" in sources


def test_ingest_skips_aim_generated_content(workspace):
    # A file that is purely AIM output (only the managed block) imports nothing.
    _write(workspace, "CLAUDE.md",
           f"{sync.AIM_BEGIN}\ngenerated only\n{sync.AIM_END}\n")
    assert core.ingest_sources() == []


def test_apply_ingest_writes_imported_files(workspace):
    _write(workspace, "CLAUDE.md", "# Style\nUse tabs.\n")
    written = core.apply_ingest()
    assert any("imported/claude-md.md" in w for w in written)
    imported = os.path.join(str(workspace), ".ai-context", "imported", "claude-md.md")
    assert os.path.isfile(imported)
    with open(imported, encoding="utf-8") as f:
        assert "Use tabs." in f.read()


def test_ingest_then_sync_then_ingest_is_idempotent(workspace, monkeypatch):
    # Need a config for sync.
    import json
    cfg = {"projectName": "T", "techStack": ["Python"], "conventions": [],
           "constraints": [], "commands": {"build": "", "test": "", "lint": "", "format": ""}}
    _write(workspace, ".ai-context/config.json", json.dumps(cfg))
    _write(workspace, "CLAUDE.md", "# Style\nUse tabs, not spaces.\n")
    monkeypatch.chdir(str(workspace))

    # 1. ingest
    core.apply_ingest()
    imported_path = os.path.join(str(workspace), ".ai-context", "imported", "claude-md.md")
    first = open(imported_path, encoding="utf-8").read()

    # 2. sync — imported content re-emitted into CLAUDE.md inside AIM markers
    sync.main()
    claude = open(os.path.join(str(workspace), "CLAUDE.md"), encoding="utf-8").read()
    assert "Imported Project Rules" in claude
    assert "Use tabs, not spaces." in claude

    # 3. ingest again — synced content is inside markers, so it is NOT
    #    re-imported; imported/ content is unchanged (idempotent).
    core.apply_ingest()
    second = open(imported_path, encoding="utf-8").read()
    assert first == second
    # exactly one copy of the rule survives in AIM's source of truth
    assert second.count("Use tabs, not spaces.") == 1


def test_imported_rules_section_empty_when_no_imports(workspace):
    assert sync.imported_rules_section(str(workspace)) == ""
