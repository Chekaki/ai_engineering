"""TODO 4 — Query transformation (lecture 6.2 rewrite; 6.1 decomposition/HyDE).

Core: rewrite_query (resolve follow-ups into standalone queries).
Bonus: decompose() and hyde() behind the same "query in -> query out" shape, so
you can bake them off on golden.json and JUSTIFY which one wins for this corpus.
"""

from __future__ import annotations

from .llm import llm_complete


def rewrite_query(conversation_context: str, ambiguous_query: str) -> str:
    """Rewrite an ambiguous follow-up into a standalone search query.

    Example: after "Tell me about Paris", the follow-up "What about its most
    famous landmark?" should become "What is the most famous landmark in Paris?".

    Write a prompt that includes the conversation context and the follow-up, and
    asks the LLM to return ONLY the rewritten standalone question. Call
    llm_complete(prompt) and return its result.

    Tip (slide 34): a self-contained query ("What is the Eiffel Tower?") needs no
    rewrite — rewriting it only adds latency and cost.
    """
    prompt = f"""You rewrite a follow-up question into a standalone search query.
Rules:
- Use the conversation to replace pronouns and missing words with real names.
- If the follow-up is already standalone, return it unchanged.
- Return ONLY the question. No preamble, no quotes, no explanation.
Example 1:
Conversation: The user asked about coffee.
Follow-up: Where does it grow?
Rewritten: Where does coffee grow?

Example 2:
Conversation: The user asked about coffee.
Follow-up: What is a lighthouse?
Rewritten: What is a lighthouse?

Conversation: {conversation_context}
Follow-up: {ambiguous_query}
Rewritten:
"""
    answer = llm_complete(prompt).strip().strip('"\'').strip()
    return answer or ambiguous_query

# --- BONUS: query bake-off (same interface, pick a winner in results.md) ------

def decompose(query: str) -> list[str]:
    """BONUS: split a multi-hop query into simpler sub-queries (fan-out)."""
    prompt = f"""You split a complex question into simple standalone search queries.
Rules:
- Each sub-query is about ONE entity or topic and makes sense on its own.
- Return 2 to 4 sub-queries, one per line. No numbering, no bullets, no explanation.
- If the question is already about a single topic, return it unchanged as one line.
Example 1:
Question: How are volcanoes, earthquakes, and plate tectonics connected?
Sub-queries:
What is a volcano?
What is an earthquake?
What is plate tectonics?
Example 2:
Question: Compare the Moon and Mars.
Sub-queries:
What is the Moon?
What is Mars?

Question: {query}
Sub-queries:
"""
    answer = llm_complete(prompt)
    subs = []
    for line in answer.splitlines():
        line = line.strip().strip('"\'').lstrip("-*. 0123456789").strip()
        if line and not line.endswith(":"):
            subs.append(line)
    if len(subs) < 2:
        return [query]
    return subs[:4]


def hyde(query: str) -> str:
    """BONUS: HyDE — generate a hypothetical answer to embed instead of the query."""
    prompt = f"""Write a short encyclopedia-style paragraph that answers the question.
Rules:
- 2 to 4 sentences, neutral Wikipedia tone, no first person.
- State facts directly, as if quoting an article. Invented details are fine:
  the text is used only as a search probe and is never shown to anyone.
- Return ONLY the paragraph. No preamble, no quotes.
Question: {query}
Paragraph:
"""
    answer = llm_complete(prompt).strip().strip('"\'').strip()
    return answer or query
