# Результати: Wikipedia RAG Pipeline v3

> Заповніть після виконання. Головна ідея — **довести числом**, що кожне покращення справді допомогло (а не просто ускладнило). Запускайте `uv run eval/eval.py --ablation`.

## Скріншот чату

<!-- Вставте скріншот вашого чатбота (app.py) тут -->

---

## 1. Retrieval-якість: chunk-size sweep (вимірюється)

Скопіюйте числа прямо з таблиці, яку друкує `uv run eval/eval.py --ablation`.

| chunk_size | recall (single) | recall (multi) | precision@k | MRR | refusal_acc | retrieval ms | index build ms | # chunks |
|:----------:|:---------------:|:--------------:|:-----------:|:---:|:-----------:|:------------:|:--------------:|:--------:|
| 200 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| 400 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| 700 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |

> `recall (multi)` — це **RAW-retrieval** без decomposition (один вектор на весь multi-hop запит), тому він **нижчий** за single — це і є мотивація для query decomposition (fan-out у чат-пайплайні, bonus).

**Який розмір виграв і чому? Порівняйте recall (single) vs recall (multi) vs precision vs latency — де компроміс?**

_____

---

## 2. Внесок компонентів (спостерігається)

Harness міряє лише raw-retrieval. Внесок `rewrite / packing / CRAG / validator` **не є числом recall** — це поведінка на конкретних запитах. Для кожного рядка: чи допомогло, на якому запиті, і доказ (демо-сценарій нижче або рядок `[debug]` / trace у консолі).

| Компонент | Де має допомогти | Допомогло? | Доказ (запит / trace) |
|-----------|------------------|:----------:|-----------------------|
| Naive (search → answer) | прості факти (Eiffel Tower, Sun) | — | _____ |
| + rewrite | follow-up (Paris → landmark; Titanic → deaths) | ___ | _____ |
| + context packing | порівняння (Paris + Eiffel — різні джерела) | ___ | _____ |
| + CRAG gate | немає доказів (2025 NBA Finals → відмова) | ___ | _____ |
| + validator (faithfulness) | вигадана цитата → ModelRetry | ___ | _____ |

**Який компонент не покращив жодного запиту (тобто зайвий у цьому pipeline)?**

_____

---

## 3. Вартість (обчислюється)

Harness **не міряє** вартість автоматично: retrieval/indexing = **0 LLM-викликів → $0**. Ціна береться лише з LLM-кроків — порахуйте виклики на один запит:

| Крок пайплайну | LLM-викликів | Коштує? |
|---|:---:|---|
| indexing (ембеддинг), search, CRAG gate, context packing, faithfulness **Tier-1** | **0** | ні — локальна математика / regex |
| generation (основна відповідь) | 1 | так, завжди |
| rewrite_query | +1 | лише на follow-up, що його тригерить |
| decompose / HyDE (bonus) | +1 | лише на multi-hop |
| faithfulness **Tier-2** (LLM-judge, bonus) | +1 | лише якщо ввімкнено |

```
tokens ≈ len(prompt+response) / 4              # ~4 символи на токен
cost $ ≈ (tokens / 1000) × USD_PER_1K_TOKENS   # константа в rag/config.py (= 0.0003)
```

| Конфіг | LLM calls / запит | приблизна cost $ / запит |
|--------|:-----------------:|:------------------------:|
| Naive (лише generation) | 1 | ___ |
| + rewrite (на follow-up) | 2 | ___ |
| + decompose (multi-hop, bonus) | 2–3 | ___ |
| + Tier-2 judge (bonus) | +1 | ___ |

**Головний висновок:** платите за трансформації запиту й генерацію, не за retrieval. Де додатковий виклик НЕ вартий приросту якості?

_____

---

## 4. Демо-сценарії (слайди 6.2)

| Сценарій | Очікувано | Що сталося |
|----------|-----------|------------|
| Paris → «its most famous landmark?» | знайшов Eiffel Tower | _____ |
| Titanic → «How many people died?» | знайшов Titanic, не випадкові трагедії | _____ |
| «Compare Paris and Eiffel Tower» | різні джерела в контексті | _____ |
| «How are the Sun, gravity, and photosynthesis connected?» | 3 статті через decomposition (bonus) | _____ |
| Titanic → «more detail about how it sank» | drill-down: агент кличе `get_full_article` (`DRILL` у trace) | _____ |
| «Who won the 2025 NBA Finals?» | чесна відмова (CRAG) | _____ |

---

## 5. Висновки

1. **CRAG-пороги (калібрування, TODO 2):** які значення `CRAG_GOOD_THRESHOLD` / `CRAG_WEAK_THRESHOLD` ви підібрали? На основі яких top-score ви їх обрали (наведіть 1-2 приклади: реальний запит vs no-evidence)? Чи знайшли запит, де жоден поріг не працює ідеально?

Стартові: GOOD=___ WEAK=___ → Ваші: GOOD=___ WEAK=___

_____

2. **Faithfulness:** наведіть приклад, де валідатор відхилив вигадану цитату `[Source: X]`, якої не було серед знайдених.

_____

---

## Bonus

**Query bake-off (rewrite vs decompose vs HyDE):** яка трансформація виграла на golden-наборі і чому?

_____

**Injection defense:** чи витік canary-токен з `adversarial.jsonl` до і після `sanitize_context`?

_____

**Contextual retrieval / LLM-judge:** що змінилось у метриках?

_____
