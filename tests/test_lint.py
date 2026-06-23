"""Tests for `aim lint` — SKILL.md conventions validator."""
from aim import core


def _skill(tmp_path, folder, frontmatter, body="\n# Title\n\nbody\n"):
    d = tmp_path / "skills" / folder
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(frontmatter + body, encoding="utf-8")
    return str(d / "SKILL.md")


def test_lint_clean_skill(tmp_path):
    _skill(tmp_path, "good-skill",
           "---\nname: good-skill\ndescription: Does a thing. Use when you need the thing.\n---\n")
    assert core.lint_skills(str(tmp_path)) == []


def test_lint_missing_description(tmp_path):
    _skill(tmp_path, "bad-skill", "---\nname: bad-skill\n---\n")
    findings = core.lint_skills(str(tmp_path))
    assert any(f["level"] == "error" and "description" in f["message"] for f in findings)


def test_lint_name_folder_mismatch(tmp_path):
    _skill(tmp_path, "folder-name",
           "---\nname: other-name\ndescription: Use when testing.\n---\n")
    findings = core.lint_skills(str(tmp_path))
    assert any(f["level"] == "warning" and "does not match folder" in f["message"] for f in findings)


def test_lint_bad_name_format(tmp_path):
    _skill(tmp_path, "Bad_Name",
           "---\nname: Bad_Name\ndescription: Use when testing.\n---\n")
    findings = core.lint_skills(str(tmp_path))
    assert any(f["level"] == "error" and "lowercase-hyphen" in f["message"] for f in findings)


def test_lint_flags_when_to_use(tmp_path):
    _skill(tmp_path, "legacy",
           '---\nname: legacy\ndescription: Does a thing, used when needed.\nwhen_to_use: "Use when X"\n---\n')
    findings = core.lint_skills(str(tmp_path))
    assert any(f["level"] == "info" and "when_to_use" in f["message"] for f in findings)


def test_lint_missing_frontmatter(tmp_path):
    d = tmp_path / "skills" / "nofm"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("# no frontmatter here\n", encoding="utf-8")
    findings = core.lint_skills(str(tmp_path))
    assert any(f["level"] == "error" and "frontmatter" in f["message"] for f in findings)


def test_lint_tolerates_utf8_bom(tmp_path):
    """A leading UTF-8 BOM must not hide valid frontmatter."""
    d = tmp_path / "skills" / "bom-skill"
    d.mkdir(parents=True)
    fm = "---\nname: bom-skill\ndescription: Does X. Use when Y.\n---\n# Title\n"
    (d / "SKILL.md").write_text(fm, encoding="utf-8-sig")  # writes a BOM
    findings = core.lint_skills(str(tmp_path))
    assert not any("frontmatter" in f["message"] for f in findings)


def test_normalize_folds_when_to_use(tmp_path):
    d = tmp_path / "skills" / "foo"
    d.mkdir(parents=True)
    fm = ('---\nname: foo\ndescription: Does a thing.\n'
          'when_to_use: "Use when you need the thing"\n'
          'allowed-tools: Read\n---\n# Foo\n')
    p = d / "SKILL.md"
    p.write_text(fm, encoding="utf-8")

    results = core.normalize_skills(str(tmp_path))
    assert any(r["status"] == "fixed" for r in results)

    text = p.read_text(encoding="utf-8")
    fields, ok = core._read_skill_frontmatter(text)
    assert ok
    assert "when_to_use" not in fields
    assert "need the thing" in fields["description"]
    assert fields["name"] == "foo"                 # other fields preserved
    assert "allowed-tools: Read" in text           # preserved

    # idempotent: a second run folds nothing more
    results2 = core.normalize_skills(str(tmp_path))
    assert all(r["status"] != "fixed" for r in results2)
    # and lint no longer flags when_to_use
    assert not any("when_to_use" in f["message"] for f in core.lint_skills(str(tmp_path)))


def test_normalize_unchanged_without_when_to_use(tmp_path):
    d = tmp_path / "skills" / "bar"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        "---\nname: bar\ndescription: Does X. Use when Y.\n---\n# Bar\n", encoding="utf-8")
    results = core.normalize_skills(str(tmp_path))
    assert all(r["status"] == "unchanged" for r in results)
