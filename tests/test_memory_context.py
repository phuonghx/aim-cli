"""Tests for typed-memory importance + ranked recall (get_memory_context)."""
import datetime

from aim import aim_cli, core


def _set(mem_id, **fields):
    """Mutate a memory in the project store directly (test seam)."""
    store = core._load_store("project")
    for m in store:
        if m["id"] == mem_id:
            m.update(fields)
    aim_cli.save_json(aim_cli.MEMORIES_PATH, store)


FIXED = "2026-01-01T00:00:00"


def _now():
    return datetime.datetime.fromisoformat(FIXED)


def test_importance_stored_and_clamped(workspace):
    a, _ = core.add_memory("alpha", "general", importance=8)
    b, _ = core.add_memory("beta", "general", importance=99)
    c, _ = core.add_memory("gamma", "general", importance=0)
    d, _ = core.add_memory("delta", "general")
    assert a["importance"] == 8
    assert b["importance"] == 10          # clamped high
    assert c["importance"] == 1           # clamped low
    assert d["importance"] == core.DEFAULT_IMPORTANCE


def test_rank_by_importance(workspace):
    lo, _ = core.add_memory("low one", "general", importance=1)
    hi, _ = core.add_memory("high one", "general", importance=10)
    _set(lo["id"], reviewedAt=FIXED)
    _set(hi["id"], reviewedAt=FIXED)
    ranked = core.rank_memories(now=_now())
    assert ranked[0]["id"] == hi["id"]


def test_rank_category_weight(workspace):
    g, _ = core.add_memory("general note", "general", importance=5)
    c, _ = core.add_memory("a correction", "correction", importance=5)
    _set(g["id"], reviewedAt=FIXED)
    _set(c["id"], reviewedAt=FIXED)
    ranked = core.rank_memories(now=_now())
    assert ranked[0]["id"] == c["id"]     # correction outranks general


def test_rank_query_relevance(workspace):
    core.add_memory("uses repository pattern for the database", "general")
    target, _ = core.add_memory("auth uses JWT tokens", "general")
    ranked = core.rank_memories(query="JWT auth")
    assert ranked[0]["id"] == target["id"]


def test_rank_excludes_archived(workspace):
    a, _ = core.add_memory("active mem", "general")
    arch, _ = core.add_memory("archived mem", "general")
    _set(arch["id"], status="archived")
    ids = [m["id"] for m in core.rank_memories()]
    assert a["id"] in ids and arch["id"] not in ids


def test_get_memory_context_empty(workspace):
    assert core.get_memory_context() == ""


def test_get_memory_context_block(workspace):
    core.add_memory("use the fetch wrapper in `src/lib/http.ts`", "decision", importance=9)
    ctx = core.get_memory_context(query="http")
    assert "Relevant project memory" in ctx
    assert "fetch wrapper" in ctx
    assert "[decision]" in ctx


def test_get_memory_context_respects_budget(workspace):
    for i in range(20):
        core.add_memory(f"memory number {i} " + "x" * 100, "general")
    ctx = core.get_memory_context(max_chars=300)
    assert len(ctx) <= 500          # roughly bounded by the budget
    assert "more" in ctx            # truncation notice present
