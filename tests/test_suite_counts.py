"""Guard the dynamically-counted agent/skill/workflow totals that get written
into the generated instruction files (CLAUDE.md, AGENTS.md, ...). Previously the
count was hardcoded ("45 skills") and drifted from the real bundle."""
import os

from aim import sync


def test_suite_counts_are_positive():
    agents, skills, workflows = sync._suite_counts()
    assert agents > 0 and skills > 0 and workflows > 0


def test_index_quotes_the_real_counts():
    agents, skills, workflows = sync._suite_counts()
    assert f"{skills} skills" in sync.SKILLS_INDEX_MD
    assert f"{agents} specialist personas" in sync.SKILLS_INDEX_MD
    assert f"{workflows} workflows" in sync.SKILLS_INDEX_MD


def test_skill_count_matches_bundled_dir():
    base = os.path.join(os.path.dirname(sync.__file__), "templates", "aim-agents", "skills")
    actual = sum(1 for e in os.listdir(base) if os.path.isdir(os.path.join(base, e)))
    _agents, skills, _workflows = sync._suite_counts()
    assert skills == actual
