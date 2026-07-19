"""TODO 2 — Retrieval + Corrective RAG gate (lecture 6.2, slides 41-42).

Two parts:
  2a. search()     — cosine search over the chunk index; KEEP the score.
  2b. crag_gate()  — decide if the evidence is good / weak / none, using the score
                     that v2 computed and threw away.
"""

from __future__ import annotations

import numpy as np

from . import config
from .data import WikiDeps


def search(deps: WikiDeps, query: str, top_k: int = config.TOP_K) -> list[dict]:
    """Return the top_k most similar chunks to `query`.

    Returns a list of dicts, highest score first:
        {"chunk_id": int, "article_title": str, "text": str, "score": float}

    Hints:
        - Encode the query with deps.encoder.
        - Normalize query and deps.chunk_embeddings (L2, + 1e-10 to avoid /0).
        - Cosine = matrix multiply; take the top_k via np.argsort.
        - Unlike v2, DO NOT discard the score — the CRAG gate needs it.
    """
    all_embs = deps.chunk_embeddings
    
    query_emb = deps.encoder.encode(query, convert_to_numpy=True)
    query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-10)
    all_norms  = all_embs / (np.linalg.norm(all_embs, axis=1, keepdims=True) + 1e-10)
    sims       = all_norms @ query_norm
    top_idx    = np.argsort(sims)[::-1][:top_k]
    
    result = []
    for i in top_idx:
        chunk = deps.chunks[int(i)]
        result.append({
            "chunk_id": chunk["chunk_id"],
            "article_title": chunk["article_title"],
            "text": chunk["text"],
            "score": float(sims[i]),
        })
    return result


def crag_gate(
    results: list[dict],
    good_threshold: float = config.CRAG_GOOD_THRESHOLD,
    weak_threshold: float = config.CRAG_WEAK_THRESHOLD,
) -> str:
    """Classify retrieval quality from the top result's score.

    Returns one of: "good" | "weak" | "none".
        good  -> top score >= good_threshold      (answer from these docs)
        weak  -> weak_threshold <= top < good      (thin — rewrite / widen / hedge)
        none  -> top score < weak_threshold        (refuse honestly)

    This is the Corrective RAG idea: check the evidence BEFORE generating, instead
    of catching a hallucination afterwards. Calibrate the thresholds on golden.json.
    """
    if not results:
        return "none"

    if results[0]["score"] < weak_threshold:
        return "none"
    if results[0]["score"] < good_threshold:
        return "weak"
    return "good"
