from aim import core, semantic


# ---------- pure logic (no extra installed) ----------

def test_available_is_boolean():
    # In CI the extra is absent; just assert it answers without raising.
    assert isinstance(semantic.available(), bool)


def test_cosine_pure_python():
    assert semantic.cosine([1, 0], [1, 0]) == 1.0
    assert semantic.cosine([1, 0], [0, 1]) == 0.0
    assert round(semantic.cosine([1, 1], [1, 0]), 3) == 0.707


def test_rank_with_mocked_embeddings(monkeypatch):
    # query closest to item "b"
    vecs = {
        "q": [1.0, 0.0],
        "a": [0.0, 1.0],
        "b": [0.9, 0.1],
        "c": [0.5, 0.5],
    }
    monkeypatch.setattr(semantic, "embed",
                        lambda texts: [vecs[t] for t in texts])
    ranked = semantic.rank("q", [("a", "a"), ("b", "b"), ("c", "c")])
    assert ranked[0][0] == "b"           # highest similarity first
    assert [k for k, _ in ranked] == ["b", "c", "a"]


def test_rank_none_when_unavailable(monkeypatch):
    monkeypatch.setattr(semantic, "embed", lambda texts: None)
    assert semantic.rank("q", [("a", "a")]) is None


def test_similar_pairs(monkeypatch):
    vecs = {"x": [1.0, 0.0], "y": [0.99, 0.01], "z": [0.0, 1.0]}
    monkeypatch.setattr(semantic, "embed", lambda texts: [vecs[t] for t in texts])
    pairs = semantic.similar_pairs([(1, "x"), (2, "y"), (3, "z")], threshold=0.9)
    assert pairs == [(1, 2, pairs[0][2])] and pairs[0][2] >= 0.9


# ---------- integration via core (mock embed) ----------

def test_semantic_search_via_core(workspace, monkeypatch):
    core.create_task("Set up authentication with JWT")   # 1
    core.create_task("Write the billing invoice module")  # 2

    # query vector closest to task 1's vector
    def fake_embed(texts):
        out = []
        for t in texts:
            tl = t.lower()
            if "auth" in tl or "jwt" in tl or "login" in tl:
                out.append([1.0, 0.0])
            else:
                out.append([0.0, 1.0])
        return out

    monkeypatch.setattr(semantic, "available", lambda: True)
    monkeypatch.setattr(semantic, "embed", fake_embed)

    results = core.semantic_search("login token", top_k=5)
    assert results is not None
    assert results[0]["type"] == "task" and results[0]["id"] == 1
    assert "score" in results[0]


def test_semantic_search_none_when_unavailable(workspace, monkeypatch):
    core.create_task("anything")
    monkeypatch.setattr(semantic, "embed", lambda texts: None)
    assert core.semantic_search("q") is None


def test_doctor_similar_memory_check(workspace, monkeypatch):
    core.add_memory("Always use the repository pattern for DB access")
    core.add_memory("Use the repository pattern when accessing the database")
    core.add_memory("Frontend uses Tailwind")

    monkeypatch.setattr(semantic, "available", lambda: True)

    def fake_embed(texts):
        # first two are near-identical, third is orthogonal
        mapping = []
        for t in texts:
            if "repository pattern" in t.lower():
                mapping.append([1.0, 0.0])
            else:
                mapping.append([0.0, 1.0])
        return mapping

    monkeypatch.setattr(semantic, "embed", fake_embed)
    findings = core.run_diagnostics()
    sim = [f for f in findings if f["kind"] == "similar-memory"]
    assert sim and "possible duplicate" in sim[0]["message"]


def test_doctor_skips_similar_memory_when_unavailable(workspace, monkeypatch):
    core.add_memory("a")
    core.add_memory("b")
    monkeypatch.setattr(semantic, "available", lambda: False)
    assert not any(f["kind"] == "similar-memory" for f in core.run_diagnostics())
