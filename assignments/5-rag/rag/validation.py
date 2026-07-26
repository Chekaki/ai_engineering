"""TODO 5 — Faithfulness validator (lecture 6.2, slides 38-40).

This is the fixed, non-gameable version of v2's check. v2 only checked that the
string "[source:" appears — so a hallucination passed as long as you appended
"[Source: X]". Here you receive the titles that were ACTUALLY retrieved and must
verify every cited source is among them.
"""

from __future__ import annotations

import re
import os
from . import llm
from pydantic_ai import ModelRetry

REFUSAL_MARKERS = ("don't have enough", "do not have enough", "no information", "cannot answer", "not found in")

CITATION_RE = re.compile(r"\[source:\s*([^\]]+)\]", re.IGNORECASE)

JUDGE_PROMPT = """You are a strict grader for a Wikipedia RAG assistant.
The assistant was allowed to use ONLY these retrieved articles:
{titles}

ANSWER:
{answer}

Split the answer into factual claims. For each claim check:
- the claim fits the topic of the article it cites (a claim that could not
  plausibly appear in that article is a red flag),
- the claim is not an obvious falsehood.

Score the whole answer 1-5:
5 = every claim fits its cited article and looks correct
4 = minor doubt on one detail
3 = cannot judge without the article text - give this when unsure
2 = a claim clearly does not belong to the article it cites
1 = a claim is an obvious falsehood or invented
Reply with exactly one number as score and nothing else"""

_SCORE_RE = re.compile(r"^\s*([1-5])\b")

def check_faithfulness(output: str, retrieved_titles: list[str]) -> str:
    """Verify the answer is grounded in what was actually retrieved.

    Args:
        output: the agent's answer.
        retrieved_titles: titles of the chunks the search tool actually returned.

    Behaviour (Tier 1 — deterministic, required):
        - If the answer is a refusal ("I don't have enough information..."), pass.
        - If there are no [Source: ...] citations at all, raise ModelRetry.
        - If ANY cited [Source: X] is not among retrieved_titles, raise ModelRetry
          (this is the anti-gaming check — a made-up citation must fail).
        - Otherwise return output unchanged.

    Bonus (Tier 2): use llm.llm_complete as an LLM-as-judge to grade whether each
    claim is actually supported by the retrieved text (score 1-5, retry if < 3).
    """
    if any(marker in output.lower() for marker in REFUSAL_MARKERS):
        return output
    
    cited = [c.strip() for c in CITATION_RE.findall(output)]
    if not cited:
        raise ModelRetry("Your answer has no [Source: Title] citation.")

    allowed = {t.strip().lower() for t in retrieved_titles}
    for title in cited:
        if title.lower() not in allowed:
            raise ModelRetry(f"[Source: {title}] was never retrieved, so that claim is not grounded.")

    judge_faithfulness(output, retrieved_titles)

    return output


def judge_faithfulness(output: str, retrieved_titles: list[str]) -> None:
    """Tier 2 (bonus): LLM-as-judge over the answer + retrieved titles.

    Opt-in via RAG_TIER2=1 (the pre-built agent.py cannot pass extra arguments).
    Fails open on any LLM error or unparseable verdict, so keyless runs and
    eval.py are never affected.
    """
    if os.environ.get("RAG_TIER2") != "1":
        return
    try:
        verdict = llm.llm_complete(
            JUDGE_PROMPT.format(titles=", ".join(retrieved_titles), answer=output)
        )
    except Exception:
        return
    m = _SCORE_RE.search(verdict)
    if not m:
        return
    score = int(m.group(1))
    print(f"  | JUDGE    score={score}/5", flush=True)
    if score < 3:
        raise ModelRetry(
            f"An LLM judge scored your answer {score}/5 for faithfulness. "
            "Rewrite the answer using ONLY facts stated in the retrieved context."
        )
