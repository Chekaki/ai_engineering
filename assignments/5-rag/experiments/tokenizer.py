# /// script
# requires-python = ">=3.11"
# dependencies = ["sentence-transformers", "numpy"]
# ///
import sys
from pathlib import Path

HW_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW_DIR))            # -> `import rag...`

from sentence_transformers import SentenceTransformer
from rag import config, data, indexing
import numpy as np

CHUNK_SIZES = [700, 5000]
OVERLAPS = [60]


def main() -> None:
    encoder = SentenceTransformer(config.ENCODER_NAME)
    tokenizer = encoder.tokenizer
    deps = data.build_deps(data.load_corpus(), encoder=encoder)

    header = (f"{'config':<12}{'p95':>8}{'p99':>8}{'max':>8}")

    print(header)
    print("-" * len(header))

    for chunk_size in CHUNK_SIZES:
        for overlap in OVERLAPS:
            if overlap >= chunk_size:
                continue  # step = chunk_size - overlap must stay positive
            
            ind = 0
            chunk_token_sizes = []
            for text in deps.texts:
                chunks = indexing.chunk_text(text, chunk_size, overlap)
                for chunk in chunks:
                    chunk_token_size = len(tokenizer.encode(chunk))
                    if chunk_token_size > 256:
                        ind += 1
                    chunk_token_sizes.append(chunk_token_size)
            print (ind)

            p95 = np.percentile(chunk_token_sizes, 95)
            p99 = np.percentile(chunk_token_sizes, 99)
            max_tokens = max(chunk_token_sizes)
            print(f"{f'{chunk_size}/{overlap}':<12}{p95:>8.1f}{p99:>8.1f}{max_tokens:>8}")


if __name__ == "__main__":
    main()
