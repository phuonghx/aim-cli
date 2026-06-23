"""Optional semantic backend for AIM.

Enabled by `pip install aim-cli[semantic]` (sentence-transformers). The core
package stays zero-dependency: every function here degrades gracefully when the
extra is absent — `available()` returns False and callers fall back to their
deterministic (substring / git-based) behaviour.

Embeddings are computed lazily and the model is cached. Cosine similarity is
pure-Python so the comparison logic is unit-testable without numpy or torch
(tests monkeypatch `embed`).
"""
import functools
import math

# A small, fast, widely-available sentence-embedding model.
MODEL_NAME = "all-MiniLM-L6-v2"


@functools.lru_cache(maxsize=1)
def available():
    """True when the optional [semantic] extra is installed and importable."""
    try:
        import sentence_transformers  # noqa: F401
        return True
    except Exception:
        return False


@functools.lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def _encode(texts):
    # Returns one vector per input text (numpy array; iterable of floats).
    return _model().encode(list(texts), normalize_embeddings=True)


def embed(texts):
    """Embed a list of texts → list of vectors, or None if unavailable/failed."""
    if not texts or not available():
        return None
    try:
        return list(_encode(texts))
    except Exception:
        return None


def cosine(a, b):
    """Cosine similarity of two vectors (pure Python; works on lists or numpy)."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / ((na * nb) or 1.0)


def rank(query, items):
    """Rank items by semantic similarity to query.
    items: list of (key, text). Returns [(key, score)] desc, or None if
    the extra is unavailable."""
    vecs = embed([query] + [text for _key, text in items])
    if vecs is None:
        return None
    query_vec, item_vecs = vecs[0], vecs[1:]
    scored = [(key, cosine(query_vec, v)) for (key, _t), v in zip(items, item_vecs)]
    scored.sort(key=lambda kv: -kv[1])
    return scored


def similar_pairs(items, threshold=0.82):
    """Find highly-similar pairs among items (possible duplicates/contradictions).
    items: list of (id, text). Returns [(id_a, id_b, score)], or None if
    the extra is unavailable."""
    vecs = embed([text for _id, text in items])
    if vecs is None:
        return None
    ids = [i for i, _t in items]
    pairs = []
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            score = cosine(vecs[a], vecs[b])
            if score >= threshold:
                pairs.append((ids[a], ids[b], round(score, 3)))
    return pairs
