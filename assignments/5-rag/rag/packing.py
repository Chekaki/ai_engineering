"""TODO 3 — Context packing / assembly (lecture 6.2, slides 35-37).

Retrieval finds chunks; packing decides WHICH chunks go into the prompt and in
what shape. This is step 3 of the loop on slide 27 and was missing entirely from
v2 (which just joined text[:500] with blank lines).
"""

from __future__ import annotations
from collections import defaultdict
from itertools import zip_longest
from . import config

_tokenizer = None


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer
        _tokenizer = AutoTokenizer.from_pretrained(f"sentence-transformers/{config.ENCODER_NAME}")
    return _tokenizer


def assemble_context(results: list[dict], token_budget: int = config.TOKEN_BUDGET) -> str:
    """Turn retrieved chunks into a citation-numbered context block.

    Apply the packing rules from the slides:
        1. Deduplicate near-identical chunks.
        2. Prefer diverse sources — for a comparison question, don't return 5
           chunks from one article.
        3. Label each kept chunk with its source so the model can cite it, e.g.:
               [Source: Paris] <text>
               [Source: Eiffel Tower] <text>
           Cite by [Source: Title] (NOT by a bare number like [1]): the faithfulness
           validator (TODO 5) checks cited titles against the retrieved ones, and a
           numeric label would tempt the model into citations the validator rejects.
        4. Stay within token_budget (estimate tokens as len(text)//4). Better 4
           strong chunks than 12 weak ones.
        5. Bonus: pull in a neighbouring/parent chunk when one chunk is too little.

    Returns the assembled context string. The [Source: Title] markers here are
    what the faithfulness validator (TODO 5) checks against.
    """

    if not results:
        return ""
    
    tokenizer = _get_tokenizer()

    unique = []
    seen = set()
    for r in results:
        key = " ".join(r["text"].split()).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
      
    by_title = defaultdict(list)
    for r in unique:
        by_title[r["article_title"]].append(r)
   
    ordered = []
    for tier in zip_longest(*by_title.values()):
        ordered.extend(r for r in tier if r is not None)
   
    blocks = []
    used = 0
    for r in ordered:
        block = f"[Source: {r['article_title']}]\n{r['text']}"
        cost = len(tokenizer.encode(block))
        if blocks and used + cost > token_budget:
            break
        blocks.append(block)
        used += cost
    
    return "\n\n".join(blocks)
