# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "litellm",
# ]
# ///
"""
HW1 Starter — Foundational Models & Sampling Parameters

Запускай цей скрипт окремо для кожного кейсу (1–4):
  1. Встанови CASE_NAME (рядок нижче) відповідно до кейсу.
  2. Введи свій PROMPT для цього кейсу.
  3. Розкоментуй потрібні моделі в SMALL_MODELS та LARGE_MODELS.
  4. uv run starter.py

Результати зберігаються в responses/<CASE_NAME>/.
Кейс 5 (Capability Ladder) — окремий скрипт: uv run ladder.py
Загалом: 4 кейси × 6 запусків = 24 автоматичні запуски.

──────────────────────────────────────────────
Setup — Large model (хмара, через OpenRouter):
  export OPENROUTER_API_KEY="sk-or-..."

Setup — Small model (локально, через Ollama):
  1. Встановити: https://ollama.com
  2. Завантажити модель: ollama pull gemma3:2b
  3. Розкоментувати рядок нижче в SMALL_MODELS

Setup — Small model (хмара, через OpenRouter):
  Розкоментувати "openrouter/google/gemma-3-4b-it" в SMALL_MODELS
──────────────────────────────────────────────
"""

import time
from pathlib import Path

import litellm
from litellm import completion

litellm.suppress_debug_info = True

# ── Змінюй цей рядок для кожного кейсу ──────────────────────────────────────
CASE_NAME = "case1_data_extraction"
# Варіанти:
#   "case1_data_extraction"
#   "case2_summarization"
#   "case3_reasoning"
#   "case4_creative_pitch"
# (Кейс 5 = Capability Ladder — запускай ladder.py)
# ─────────────────────────────────────────────────────────────────────────────

PROMPT = "YOUR PROMPT HERE"

# ── Large models (хмара) — розкоментуй один ──────────────────────────────────
LARGE_MODELS = [
    "openrouter/openai/gpt-4o",
    # "openrouter/meta-llama/llama-4-scout",
]

# ── Small / Local models — розкоментуй один ──────────────────────────────────
SMALL_MODELS = [
    # Варіант A: платна мала модель через OpenRouter (~$0.04/M токенів, найпростіше)
    # "openrouter/google/gemma-3-4b-it",

    # Варіант B: локально через Ollama (безкоштовно, потребує ~2 ГБ RAM)
    # "ollama/gemma3:2b",

    # Варіант C: хмара безкоштовно через OpenRouter (є rate limit, може не пройти)
    # "openrouter/meta-llama/llama-3.2-3b-instruct:free",
]

MODELS = LARGE_MODELS + SMALL_MODELS

TEMPERATURES = [0.1, 0.7, 1.2]
SEED = 42


def ask(model: str, prompt: str, temperature: float = 0.7, seed: int | None = SEED):
    """Returns (text, elapsed_s, cost_usd_or_none)."""
    start = time.time()
    resp = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        seed=seed,
        max_tokens=1024,
    )
    elapsed = time.time() - start
    cost = (getattr(resp, "_hidden_params", None) or {}).get("response_cost", None)
    return resp.choices[0].message.content, elapsed, cost


def save_response(out_dir: Path, short_name: str, temp: float, text: str, elapsed: float, cost):
    case_dir = out_dir / CASE_NAME
    case_dir.mkdir(parents=True, exist_ok=True)
    slug = short_name.replace("/", "_").replace(" ", "_").replace(":", "_")
    path = case_dir / f"{slug}_t{temp}.txt"
    cost_str = f"${cost:.6f}" if cost is not None else "n/a"
    header = f"# time: {elapsed:.1f}s | cost: {cost_str}\n"
    path.write_text(header + text + "\n")
    print(f"  → saved {path}")


def main():
    out_dir = Path(__file__).parent / "responses"

    if not MODELS:
        print("ERROR: MODELS is empty. Розкоментуй хоча б одну модель у SMALL_MODELS або LARGE_MODELS.")
        return

    print("=" * 70)
    print(f"Case:   {CASE_NAME}")
    print(f"Prompt: {PROMPT[:80]}{'…' if len(PROMPT) > 80 else ''}")
    print("=" * 70)

    for model in MODELS:
        for temp in TEMPERATURES:
            short_name = model.removeprefix("openrouter/").removeprefix("ollama/")
            tier = "LARGE" if model in LARGE_MODELS else "SMALL"
            print(f"\n{'─' * 70}")
            print(f"[{tier}] Model: {short_name}  |  T={temp}")
            print("─" * 70)
            try:
                result, elapsed, cost = ask(model, PROMPT, temp)
                cost_str = f"${cost:.6f}" if cost is not None else "n/a"
                print(f"Time: {elapsed:.1f}s | Cost: {cost_str}")
                print(result)
                save_response(out_dir, short_name, temp, result, elapsed, cost)
            except Exception as e:
                print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
