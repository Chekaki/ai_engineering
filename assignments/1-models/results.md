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
1. With temperature higher than 0.1 smaller model can't handle it at all.
2. One time llama3.1:8b with t=0.7 created python script to parse it :D But most of the time not finished json / imaginable json
3. Both models include in response before and after explanation with t=1.2, not only json
---

## Кейс 2: Summarization

**Цифра "60-70%"** — збережена при T=1.2?
- Large: +
- Small: +

**Чи додала маленька модель зайве форматування** (наприклад, жирні заголовки)?
Format is wild for llama3.1:8b

**Ключова знахідка:**
Foundational model is consistent with formating and summary through all range of temperature in the test

---

## Кейс 3: Reasoning

**Вартість 120 ГБ (правильно: $29.50/міс)**
- Large T=0.1: $29.50/міс та $354/рік
- Large T=1.2: $28.80 (for first put price then resoning for this price)
- Small T=0.1: $30,00
- Small T=1.2: -

**Поріг блокування (правильно: "5 разів" = негайний блок)**
- Large T=0.1: +
- Large T=1.2: +
- Small T=0.1: -
- Small T=1.2: Pending

**Ключова знахідка:**

For calculation low temperature works better for both model

---

## Кейс 4: Creative Pitch

**Кількість речень при T=1.2**
- Large: 3
- Small: 1 explanation + 1 bolded topic + 3 sentences

**Найпомітніша різниця у словнику між T=0.1 та T=1.2 (Large):**
T=0.1 more like technical presentation, 
T=1.2 closer to sales speech 

**Чи дотрималась маленька модель формату "одна відповідь, 3 речення"?**
Only with t=0.7

**Ключова знахідка:**
We can control emotion level of response with temperature

---

## Кейс 5: Capability Ladder

Запусти `uv run ladder.py` і заповни таблицю за результатами.  
Правильна відповідь: **$29.50/міс**, блокування при **5× ліміту** (негайно, не Pending).

| Модель | Архітектура | Вартість (що написала?) | Blocking 5× ✓/✗ | Час | Cost ($) |
|---|---|---|---|---|---|
| llama-3.2-1b | Dense 1B | - | - | 1.5s | $0.000050 |
| gemma-3-4b-it | Dense 4B | $31.50 | + | 13.3s | $0.000047 |
| qwen3-30b-a3b | MoE 3B/30B | | | | | (failed)
| llama-4-scout | MoE 17B/109B | $31.50 / $378 | + | 2.9s | $0.000729 |
| llama-3.3-70b | Dense 70B | $378 | + | 6.0s |  $0.000178 |
| gpt-4o | Frontier | $354 | + | 2.6s | $0.004045 |

**При якому розмірі вперше з'являється правильна відповідь?**
gpt-4o, but he didn't specify monthly cost.

**Рефлексія:** Для продукту з 1,000 запитів/день на цій задачі — який tier обираєш і чому?
I would invest more in testing and probably split cost / blocking rules.
For blocking rules looks like Smaller models is effective enough (need to confirm through evaluation)
For calculation - i would provide more clear prompt with examples and test again :D

---

## Загальне

**Який кейс показав найбільший gap між моделями і чому?**
Data Extraction. Because small model coudn't handle it reliably.

**Що здивувало найбільше?**
That small model strugling with data extraction havily.

---

## Бонус A: The Nucleus Effect (опціонально)

**Кейс 4, T=1.0: Top-P=1.0 vs Top-P=0.1 — різниця декільками реченнями:**

Top-P=0.1 keeps generation with a small subset of options and keeps generation on track without going wild. On the other hand Top-P=1.0 feels more unnatural with words like 'annihilate':D

---

## Бонус B: System Prompt Experiment (опціонально)

**Gemma 4B, T=0.7, без system prompt — кількість речень у відповіді:**
3 Options each with 3 sentences

**Gemma 4B, T=0.7, з system prompt — кількість речень у відповіді:**
3

**Чи виправив system prompt поведінку? (1-2 речення):**
Yes, same result if we put "You must write exactly 3 sentences. Do not provide multiple options or variants." into user prompt.

