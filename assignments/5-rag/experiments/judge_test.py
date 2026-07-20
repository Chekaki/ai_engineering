# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "pydantic-ai"]
# ///
"""Tier-2 judge smoke test: grounded vs fabricated answer, titles only.
    uv run experiments/judge_test.py   (needs OPENROUTER_API_KEY)
"""
import os
import sys
from pathlib import Path

HW_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW_DIR))

os.environ["RAG_TIER2"] = "1"

from pydantic_ai import ModelRetry

from rag import validation

titles = ["Eiffel Tower", "Paris"]

cases = {
    "grounded":   "The Eiffel Tower is a wrought-iron lattice tower in Paris [Source: Eiffel Tower].",
    "fabricated": "The Eiffel Tower was built in 1750 by Napoleon as a lighthouse [Source: Eiffel Tower].",
    "wrong home": "The Louvre is the most visited museum in the world [Source: Eiffel Tower].",
}
for name, answer in cases.items():
    try:
        validation.check_faithfulness(answer, titles)
        print(f"{name}: PASS")
    except ModelRetry as e:
        print(f"{name}: RETRY -> {e}")