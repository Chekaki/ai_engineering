# /// script
# requires-python = ">=3.11"
# dependencies = ["sentence-transformers", "numpy"]
# ///
"""Grid-search chunk_size x overlap over the golden set.

Pure retrieval (no LLM / no API key). Run from the 5-rag directory:

    uv run research/chunk_size_sweep.py

Reuses the eval harness so the numbers match `uv run eval/eval.py --ablation`.
"""

import sys
from pathlib import Path

HW_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW_DIR))            # -> `import rag...`
sys.path.insert(0, str(HW_DIR / "eval"))   # -> `import harness`

from sentence_transformers import SentenceTransformer

import harness
import rag as sol
from rag import config, data, indexing, retrieval


#CHUNK_SIZES = (200, 300, 400, 500, 700)
CHUNK_SIZES = [10000]
OVERLAPS = [0]


def main() -> None:
    encoder = SentenceTransformer(config.ENCODER_NAME)
    deps = data.build_deps(data.load_corpus(), encoder=encoder)
    golden = harness.load_golden()

    header = (f"{'config':<12}{'rec(single)':>12}{'rec(multi)':>12}{'prec@k':>9}"
              f"{'mrr':>7}{'refusal':>9}{'ret_ms':>9}{'n_chunks':>10}")
    print(header)
    print("-" * len(header))

    for chunk_size in CHUNK_SIZES:
        for overlap in OVERLAPS:
            if overlap >= chunk_size:
                continue  # step = chunk_size - overlap must stay positive
            indexing.build_index(deps, chunk_size, overlap)
            n_chunks = len(deps.chunks)
            res = harness.evaluate_retrieval(
                sol, deps, golden, config.TOP_K, label=f"{chunk_size}/{overlap}"
            )
            row = res.as_row()
            print(f"{row['config']:<12}{row['recall_single']:>12}{row['recall_multi']:>12}"
                  f"{row['precision_single']:>9}{row['mrr_single']:>7}{row['refusal_acc']:>9}"
                  f"{row['retrieval_ms']:>9}{n_chunks:>10}")


if __name__ == "__main__":
    main()
