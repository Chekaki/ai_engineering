# /// script
# requires-python = ">=3.11"
# dependencies = ["sentence-transformers", "numpy", "httpx"]
# ///
"""Bake-off: raw query embedding vs HyDE vs decompose on the golden set.
    uv run experiments/rewrite_bakeoff.py
"""

import sys
from pathlib import Path

HW_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW_DIR))            # -> `import rag...`
sys.path.insert(0, str(HW_DIR / "eval"))

from sentence_transformers import SentenceTransformer

import harness
from rag import config, data, indexing, retrieval
from rag.query_transform import decompose, hyde


def fan_out(deps, subqueries):
    """Quota merge, copied from _fan_out_search in rag/agent.py."""
    per_sub = [retrieval.search(deps, sq, config.TOP_K) for sq in subqueries]
    ranked, seen = [], set()
    quota = max(1, config.TOP_K // len(subqueries))
    for res in per_sub:
        taken = 0
        for r in res:
            if r["chunk_id"] in seen:
                continue
            ranked.append(r)
            seen.add(r["chunk_id"])
            taken += 1
            if taken >= quota:
                break
    rest = sorted(
        (r for res in per_sub for r in res if r["chunk_id"] not in seen),
        key=lambda r: r["score"], reverse=True,
    )
    for r in rest:
        if len(ranked) >= config.TOP_K:
            break
        ranked.append(r)
        seen.add(r["chunk_id"])
    return sorted(ranked, key=lambda r: r["score"], reverse=True)[:config.TOP_K]


def evaluate(deps, golden, transform=None):
    """Search every golden query, optionally through a transform first."""
    rows = []
    for q in golden:
        probe = transform(q["query"]) if transform else q["query"]
        if isinstance(probe, list):
            results = fan_out(deps, probe) if len(probe) > 1 else retrieval.search(deps, probe[0], config.TOP_K)
            probe = " | ".join(probe)
        else:
            results = retrieval.search(deps, probe, config.TOP_K)
        titles = [r["article_title"] for r in results]
        rows.append({
            "type": q["type"],
            "query": q["query"],
            "probe": probe,
            "top": results[0]["score"] if results else 0.0,
            "gate": retrieval.crag_gate(results),
            "recall": harness.recall_at_k(titles, q.get("expected_titles", [])),
            "rr": harness.reciprocal_rank(titles, q.get("expected_titles", [])),
        })
    return rows


def summarize(label, rows):
    single = [r for r in rows if r["type"] == "single"]
    multi = [r for r in rows if r["type"] == "multihop"]
    noev = [r for r in rows if r["type"] == "no_evidence"]
    rec_s = sum(r["recall"] for r in single) / len(single)
    rec_m = sum(r["recall"] for r in multi) / len(multi)
    mrr = sum(r["rr"] for r in single) / len(single)
    refusal = sum(1 for r in noev if r["gate"] != "good") / len(noev)
    print(f"{label:<6}{rec_s:>12.3f}{rec_m:>12.3f}{mrr:>8.3f}{refusal:>14.3f}")


def print_diffs(label, raw, other):
    print(f"\nPer-query changes, raw vs {label} (where recall or CRAG gate moved):")
    for a, b in zip(raw, other):
        if abs(a["recall"] - b["recall"]) > 1e-9 or a["gate"] != b["gate"]:
            print(f"  [{a['type']}] {a['query'][:55]}")
            print(f"    raw   : top={a['top']:.3f}  gate={a['gate']:<5}  recall={a['recall']:.2f}")
            print(f"    {label:<6}: top={b['top']:.3f}  gate={b['gate']:<5}  recall={b['recall']:.2f}")


def print_probes(hyd):
    print("\nWhat HyDE invented for the no-evidence queries:")
    for r in hyd:
        if r["type"] == "no_evidence":
            print(f"  Q: {r['query']}")
            print(f"  H: {r['probe'][:220]}\n")


def main():
    encoder = SentenceTransformer(config.ENCODER_NAME)
    deps = data.build_deps(data.load_corpus(), encoder=encoder)
    print(f"Building index at chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP} ...")
    indexing.build_index(deps, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    print(f"  {len(deps.chunks)} chunks")

    golden = harness.load_golden()
    raw = evaluate(deps, golden)
    print("Calling hyde() for 21 queries (~30s, ~21 LLM calls) ...")
    hyd = evaluate(deps, golden, transform=hyde)
    print("Calling decompose() for 21 queries (~21 LLM calls) ...")
    dec = evaluate(deps, golden, transform=decompose)

    print(f"\n{'':<6}{'rec(single)':>12}{'rec(multi)':>12}{'MRR':>8}{'refusal_acc':>14}")
    print("-" * 52)
    summarize("raw", raw)
    summarize("hyde", hyd)
    summarize("decomp", dec)

    print_diffs("hyde", raw, hyd)
    print_diffs("decomp", raw, dec)
    print_probes(hyd)

    print("\nHow decompose split the queries (only where it split):")
    for r in dec:
        if " | " in r["probe"]:
            print(f"  [{r['type']}] {r['query'][:55]}")
            print(f"      -> {r['probe']}")


if __name__ == "__main__":
    main()