from __future__ import annotations

import uuid
from typing import Any

SCHEMA_VERSION = "1.0.0"


def op_classify_extract(data):
    text = str(data.get("text", ""))
    labels = [label for label, words in data.get("labels", {}).items() if any(w.casefold() in text.casefold() for w in words)]
    extracted = {name: text[start:end] for name, (start, end) in data.get("spans", {}).items()}
    return {"labels": labels, "extracted": extracted}
def op_embed_similarity(data):
    import math
    from collections import Counter
    left, right = Counter(str(data.get("left", "")).casefold().split()), Counter(str(data.get("right", "")).casefold().split())
    dot = sum(left[k] * right[k] for k in left)
    norm = math.sqrt(sum(v*v for v in left.values()) * sum(v*v for v in right.values()))
    return {"cosine_similarity": dot / norm if norm else 0.0, "dimensions": len(set(left) | set(right))}
def op_retrieve_rag(data):
    query = set(str(data.get("query", "")).casefold().split())
    scored = []
    for doc in data.get("documents", []):
        tokens = set(str(doc.get("text", "")).casefold().split())
        scored.append((len(query & tokens), doc))
    hits = [doc for score, doc in sorted(scored, key=lambda x: x[0], reverse=True) if score > 0]
    limit = int(data.get("limit", 3))
    return {"hits": hits[:limit], "context": "\n".join(str(x.get("text", "")) for x in hits[:limit])}


OPERATIONS = {
    "classify-extract": op_classify_extract,
    "embed-similarity": op_embed_similarity,
    "retrieve-rag": op_retrieve_rag
}


def dispatch(envelope: dict[str, Any]) -> dict[str, Any]:
    module = envelope.get("module")
    if module not in OPERATIONS:
        raise ValueError(f"unknown module: {module}")
    run_id = str(envelope.get("run_id") or uuid.uuid4())
    output = OPERATIONS[module](envelope.get("input") or {})
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "module": module,
        "output": output,
        "lineage": {"run_id": run_id, "module": module},
    }
