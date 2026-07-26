# /// script
# requires-python = ">=3.11"
# dependencies = ["sentence-transformers", "numpy"]
# ///
"""Calibrate CRAG_GOOD_THRESHOLD / CRAG_WEAK_THRESHOLD on the golden set.

Pure retrieval (no LLM / no API key). Run from the 5-rag directory:

    uv run experiments/crag_calibration.py

Prints three things:
  A. every golden query with its top score, sorted high to low
  B. the separation between real queries and no-evidence queries
  C. threshold sweeps, so you can see what each cut-off would cost

Two different notions of "refused" are tracked, because they disagree:
  refusal_acc  - gate != "good"  (this is what eval/harness.py measures)
  hard_refusal - gate == "none"  (this is what actually drops the context
                 in agent.py, so it is what demo scenario 6 needs)
"""

import sys
from pathlib import Path

HW_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW_DIR))            # -> `import rag...`
sys.path.insert(0, str(HW_DIR / "eval"))   # -> `import harness`

from sentence_transformers import SentenceTransformer

import harness
from rag import config, data, indexing, retrieval

# Index built once, at whatever config.py currently says (your sweep winner).
CHUNK_SIZE = config.CHUNK_SIZE
CHUNK_OVERLAP = config.CHUNK_OVERLAP

# Grid for the threshold sweeps.
GRID = [round(0.15 + 0.01 * i, 2) for i in range(56)]   # 0.15 .. 0.70

def collect(deps, golden) -> list[dict]:
    """Top score + top title for every golden query."""
    rows = []
    for q in golden:
        results = retrieval.search(deps, q["query"], config.TOP_K)
        rows.append({
            "type": q["type"],
            "query": q["query"],
            "top": results[0]["score"] if results else 0.0,
            "top_title": results[0]["article_title"] if results else "-",
            "expected": q["expected_titles"],
        })
    return rows


def print_scores(rows: list[dict]) -> None:
    print("\nA. Top score per golden query (sorted)")
    print(f"{'':>3} {'type':<10}{'top':>7}  {'top chunk came from':<22} query")
    print("-" * 100)
    for r in sorted(rows, key=lambda r: -r["top"]):
        # Mark no-evidence rows so they are easy to spot in the ranking.
        mark = ">>" if r["type"] == "no_evidence" else "  "
        # Did retrieval actually find an expected article at rank 1?
        ok = "" if r["type"] == "no_evidence" else (
            " *" if r["top_title"] in r["expected"] else " x")
        print(f"{mark:>3} {r['type']:<10}{r['top']:>7.3f}  "
              f"{r['top_title'][:22]:<22}{ok:<2} {r['query'][:45]}")
    print("\n  >> = no-evidence query   * = rank-1 chunk is an expected article   x = it is not")


def print_separation(rows: list[dict]) -> None:
    real = [r for r in rows if r["type"] != "no_evidence"]
    noev = [r for r in rows if r["type"] == "no_evidence"]

    worst_real = min(real, key=lambda r: r["top"])
    best_noev = max(noev, key=lambda r: r["top"])

    print("\nB. Separation")
    print(f"  lowest-scoring REAL query        {worst_real['top']:.3f}  {worst_real['query']}")
    print(f"  highest-scoring NO-EVIDENCE      {best_noev['top']:.3f}  {best_noev['query']}")
    print(f"                                            (matched: {best_noev['top_title']})")

    if best_noev["top"] >= worst_real["top"]:
        print("\n  OVERLAP: a no-evidence query outscores a real one.")
        print("  No single threshold separates them. Whatever you pick, you either")
        print("  let that no-evidence query through or you block a real question.")
    else:
        gap_lo, gap_hi = best_noev["top"], worst_real["top"]
        print(f"\n  CLEAN GAP: {gap_lo:.3f} .. {gap_hi:.3f}")
        print(f"  Any threshold inside this gap separates them. Midpoint: {(gap_lo + gap_hi) / 2:.3f}")


def print_good_sweep(rows: list[dict]) -> None:
    """What GOOD costs: real queries kept vs no-evidence queries let through."""
    real = [r for r in rows if r["type"] != "no_evidence"]
    noev = [r for r in rows if r["type"] == "no_evidence"]

    print("\nC1. GOOD threshold sweep")
    print(f"{'good':>6}{'real kept':>12}{'noev leaked':>14}{'refusal_acc':>14}")
    print("-" * 46)
    prev = None
    for g in GRID:
        kept = sum(1 for r in real if r["top"] >= g)
        leaked = sum(1 for r in noev if r["top"] >= g)
        row = (kept, leaked)
        if row == prev:          # only print where something actually changes
            continue
        prev = row
        acc = (len(noev) - leaked) / len(noev)
        print(f"{g:>6.2f}{kept:>7}/{len(real):<4}{leaked:>9}/{len(noev):<4}{acc:>14.3f}")
    print("\n  'real kept' = real queries still gated GOOD (want high)")
    print("  'noev leaked' = no-evidence queries wrongly gated GOOD (want 0)")


def print_weak_sweep(rows: list[dict]) -> None:
    """What WEAK costs: hard refusals earned vs real queries silenced."""
    real = [r for r in rows if r["type"] != "no_evidence"]
    noev = [r for r in rows if r["type"] == "no_evidence"]

    print("\nC2. WEAK threshold sweep (below WEAK = 'none' = context dropped)")
    print(f"{'weak':>6}{'noev refused':>15}{'real killed':>14}")
    print("-" * 37)
    prev = None
    for w in GRID:
        refused = sum(1 for r in noev if r["top"] < w)
        killed = sum(1 for r in real if r["top"] < w)
        row = (refused, killed)
        if row == prev:
            continue
        prev = row
        print(f"{w:>6.2f}{refused:>10}/{len(noev):<4}{killed:>9}/{len(real):<4}")
    print("\n  'noev refused' = honest refusals, demo scenario 6 (want all)")
    print("  'real killed' = real questions refused by mistake (want 0)")


def print_current(rows: list[dict]) -> None:
    """Where the thresholds in config.py land right now."""
    print("\nD. Your current config.py")
    print(f"  GOOD={config.CRAG_GOOD_THRESHOLD}  WEAK={config.CRAG_WEAK_THRESHOLD}")
    buckets = {"good": [], "weak": [], "none": []}
    for r in rows:
        gate = retrieval.crag_gate([{"score": r["top"]}])
        buckets[gate].append(r)
    for gate in ("good", "weak", "none"):
        noev = [r for r in buckets[gate] if r["type"] == "no_evidence"]
        flag = "  <-- leaked" if (gate == "good" and noev) else ""
        print(f"  {gate:<5} {len(buckets[gate]):>2} queries "
              f"({len(noev)} no-evidence){flag}")
        for r in noev:
            print(f"          {r['top']:.3f}  {r['query']}")


def main() -> None:
    encoder = SentenceTransformer(config.ENCODER_NAME)
    deps = data.build_deps(data.load_corpus(), encoder=encoder)
    print(f"Building index at chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP} ...")
    indexing.build_index(deps, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"  {len(deps.chunks)} chunks")

    rows = collect(deps, harness.load_golden())

    print_scores(rows)
    print_separation(rows)
    print_good_sweep(rows)
    print_weak_sweep(rows)
    print_current(rows)


if __name__ == "__main__":
    main()
