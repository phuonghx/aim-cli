import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aim import aim_cli  # noqa: E402


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Point every module-level path global at a throwaway workspace."""
    root = tmp_path
    ai_context = root / ".ai-context"
    tasks = ai_context / "tasks"
    docs = ai_context / "docs"
    templates = ai_context / "templates"
    for d in (ai_context, tasks, docs, templates):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(aim_cli, "ROOT_DIR", str(root))
    monkeypatch.setattr(aim_cli, "AI_CONTEXT_DIR", str(ai_context))
    monkeypatch.setattr(aim_cli, "TASKS_DIR", str(tasks))
    monkeypatch.setattr(aim_cli, "DOCS_DIR", str(docs))
    monkeypatch.setattr(aim_cli, "TEMPLATES_DIR", str(templates))
    monkeypatch.setattr(aim_cli, "MEMORIES_PATH", str(ai_context / "memories.json"))
    monkeypatch.setattr(aim_cli, "CONFIG_PATH", str(ai_context / "config.json"))
    monkeypatch.setattr(aim_cli, "TIMER_STATE_PATH", str(ai_context / "timer_state.json"))
    monkeypatch.setattr(aim_cli, "TIME_LOG_PATH", str(ai_context / "time_log.json"))
    monkeypatch.setattr(aim_cli, "USERS_PATH", str(ai_context / "users.json"))
    # Keep the global memory store inside the tmp workspace so tests never
    # read or write the real ~/.aim/ store.
    global_dir = root / "global-aim"
    monkeypatch.setattr(aim_cli, "GLOBAL_AIM_DIR", str(global_dir))
    monkeypatch.setattr(aim_cli, "GLOBAL_MEMORIES_PATH", str(global_dir / "memories.json"))
    return root
