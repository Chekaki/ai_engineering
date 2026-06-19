# Результати — HW1: Foundational Models & Sampling

**Студент:**  
**Дата:**  
**Large model:** gpt-4o
**Small model:** llama3.1:8b

---

## Task 1: Foundational Models

| Модель | Провайдер | Тип | Context Window | Input $/1M | Output $/1M | Модальності | Vocab size | Architecture |
|---|---|---|---|---|---|---|---|---|
| gpt-4o | openai | proprietary | 128K | 2.50 | 10.00 | Multimodal | ~200K | MoE |
| gpt-4o-mini | openai | proprietary | 128K | 0.15 | 0.60 | Multimodal | ~200K | MoE / Dense |
| claude-haiku-4.5 | anthropic | proprietary | 200K | 1.00 | 5.00 | Multimodal | 65K | MoE? |
| gemma-4-31b-it | google | open-weights | 262K | 0.12 | 0.35 | Multimodal | ~262K | Dense |
| llama-4-maverick | meta-llama | open-weights | 1M | 0.15 | 0.60 | Multimodal | ~202K | MoE |
| Qwen3-30B-A3B | Qwen (Alibaba) | open-weights | 128K | 0 (local) | 0 (local) | Text | ~152K | MoE, 48 layers |
| phi-4 | microsoft | open-weights | 16K | 0 (local) | 0 (local) | Text | ~200K | Dense, 40 layers |
| Gemma-3-12B-it | google | open-weights | 128K | 0 (local) | 0 (local) | Multimodal | ~262K | Dense, 48 layers |
| Qwen3-8B | Qwen | open-weights | 128K | 0 (local) | 0 (local) | Text | ~152K | Dense, 36 layers |
| Llama-3.1-8B-Instruct | meta-llama | open-weights | 128K | 0 (local) | 0 (local) | Text | ~128K | Dense, 32 layers |

**Чому обрав саме ці моделі?** (1-2 речення)
I chose these text/multimodal models to get good visibility into what can be achieved with frontier models compared to cheaper, smaller ones — including a local model.


---

## Task 2: Embedding Models

| Модель | Dimensions | Max Input Tokens | MTEB Score | Ціна / Хостинг |
|---|---|---|---|---|
| openai/text-embedding-3-small | 1536 | 8,191 | 62.3% | $0.02 per 1M |
| openai/text-embedding-3-large | 3072 | 8,192 | 64.6% | $0.13 per 1M |
| intfloat/multilingual-e5-large | 1024 | 8K | 60.9% | $0.01 per 1M |
| CohereLabs/Cohere-embed-multilingual-v3.0 | 1024 | 4096 | 64.0% | 0  (local) |
| Qwen/Qwen3-Embedding-0.6B | 1024 | 32K | ~70% | 0 (local) |

---

## Кейс 1: Data Extraction

**UNIX timestamp** (`1740665406`) — що зробила кожна модель?
- Large (T=0.1 / T=1.2): null / null
- Small (T=0.1 / T=1.2): left as is / left as is

**error_type для рядка WARN** — `"invalid_token"` чи щось інше?
- Large: invalid_token | null | session_expired
- Small: invalid_token | null | session_expired

**Ключова знахідка:**
1. With a temperature higher than 0.1, the smaller model can't handle the task at all.
2. One time llama3.1:8b at T=0.7 wrote a Python script to parse it :D But most of the time it produced unfinished or imaginary JSON.
3. At T=1.2 both models wrap the JSON with explanations before and after, not only the JSON.

---

## Кейс 2: Summarization

**Цифра "60-70%"** — збережена при T=1.2?
- Large: +
- Small: +

**Чи додала маленька модель зайве форматування** (наприклад, жирні заголовки)?
The formatting is wild for llama3.1:8b.

**Ключова знахідка:**
The foundational model is consistent with formatting and summary across the whole temperature range in the test.

---

## Кейс 3: Reasoning

**Вартість 120 ГБ (правильно: $29.50/міс)**
- Large T=0.1: $29.50/міс та $354/рік
- Large T=1.2: $28.80 (first states a price, then reasons about that price)
- Small T=0.1: $30,00
- Small T=1.2: -

**Поріг блокування — гранична умова:** 5 ТБ = рівно 5×. За буквою «понад 5 разів» (строго >5×) це ще 'Pending'; за задумом політики — блок. Найкраща відповідь помічає неоднозначність.
- Large T=0.1: +
- Large T=1.2: +
- Small T=0.1: -
- Small T=1.2: Pending

**Ключова знахідка:**

For calculation, a low temperature works better for both models.

---

## Кейс 4: Creative Pitch

**Кількість речень при T=1.2**
- Large: 3
- Small: 1 explanation + 1 bolded topic + 3 sentences

**Найпомітніша різниця у словнику між T=0.1 та T=1.2 (Large):**
T=0.1 reads more like a technical presentation.
T=1.2 is closer to a sales pitch.

**Чи дотрималась маленька модель формату "одна відповідь, 3 речення"?**
Only with t=0.7

**Ключова знахідка:**
We can control emotion level of response with temperature

---

## Кейс 5: Capability Ladder

Запусти `uv run ladder.py` і заповни таблицю за результатами.  
Правильна відповідь: **$29.50/міс**. Поріг блокування 5× — гранична умова: за буквою «понад 5 разів» (строго >5×) це ще 'Pending', за задумом політики — блок (див. розбір у task.md).

| Модель        | Архітектура   | Вартість (що написала?) | Blocking 5× ✓/✗ | Час   | Cost ($)   |
|---------------|---------------|-------------------------|-----------------|-------|------------|
| llama-3.2-1b  | Dense 1B      | -                       | -               | 1.5s  | $0.000050  |
| gemma-3-4b-it | Dense 4B      | $31.50                  | +               | 13.3s | $0.000047  |
| qwen3-30b-a3b | MoE 3B/30B    | (failed)                | (failed)        | -     | -          |
| llama-4-scout | MoE 17B/109B  | $31.50 / $378           | +               | 2.9s  | $0.000729  |
| llama-3.3-70b | Dense 70B     | $378                    | +               | 6.0s  | $0.000178  |
| gpt-4o        | Frontier      | $354                    | +               | 2.6s  | $0.004045  |

**При якому розмірі вперше з'являється правильна відповідь?**
gpt-4o, but it didn't specify the monthly cost.

**Рефлексія:** Для продукту з 1,000 запитів/день на цій задачі — який tier обираєш і чому?
I would invest more in testing and probably split the cost / blocking rules.
For blocking rules, the smaller models look effective enough (need to confirm through evaluation).
For calculation, I would provide a clearer prompt with examples and test again :D

---

## Загальне

**Який кейс показав найбільший gap між моделями і чому?**
Data Extraction. Because the small model couldn't handle it reliably.

**Що здивувало найбільше?**
That the small model struggled with data extraction so heavily.

---

## Бонус A: The Nucleus Effect (опціонально)

**Кейс 4, T=1.0: Top-P=1.0 vs Top-P=0.1 — різниця декільками реченнями:**

Top-P=0.1 keeps generation within a small subset of options and stays on track without going wild. Top-P=1.0, on the other hand, feels more unnatural, with words like 'annihilate' :D

---

## Бонус B: System Prompt Experiment (опціонально)

**Gemma 4B, T=0.7, без system prompt — кількість речень у відповіді:**
3 Options each with 3 sentences

**Gemma 4B, T=0.7, з system prompt — кількість речень у відповіді:**
3

**Чи виправив system prompt поведінку? (1-2 речення):**
Yes, same result if we put "You must write exactly 3 sentences. Do not provide multiple options or variants." into user prompt.

