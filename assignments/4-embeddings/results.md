# Результати: Автокатегоризація тікетів через Embeddings

> Заповніть цей файл після виконання домашнього завдання.

---

## 1. Кластеризація

**Датасет:** 300 synthetic support tickets (labeled — `category` field used for ARI ground truth)

**Embedding модель:** all-MiniLM-L6-v2

### Пошук оптимального k

Запустіть `uv run starter.py --quick --clusters N` для кожного значення і запишіть ARI:

| k  | ARI score |
|----|-----------|
| 3  | 0.336     |
| 4  | 0.396     |
| 5  | 0.476     |
| 6  | 0.523     |
| 7  | 0.500     |
| 8  | 0.471     |
| 9  | 0.428     |
| 10 | 0.397     |
| 12 | 0.400     |

**Оптимальне k:** 6 — **ARI:** 0.523

**Чому саме це k?** *(1–2 речення)*
k=6 is the peak of ARI because our embedding model does not separate the data into the same 7 categories that we have. Some of them overlap so the model can only tell about 6 groups. Below 6 different categories are merged into one cluster, even though they should stay separate. Above 6, the opposite happends - the model over-splits and tickets that belong to one group start to break into different clusters.


### Візуалізація t-SNE

<!-- Перетягніть clusters.png або вставте скріншот -->

![clusters](clusters.png)

### Таблиця кластерів

| # | Назва від LLM         | К-ть тікетів |
|---|-----------------------|--------------|
| 0 | Account Access Issue  | 44           |
| 1 | Feature Requests      | 69           |
| 2 | Order Issues          | 50           |
| 3 | Device & App Issues   | 51           |
| 4 | Billing & Payments    | 44           |
| 5 | Delivery Issues       | 42           |

*(Додайте або приберіть рядки відповідно до обраного k)*

---

## 2. Порівняння методів пошуку

Скопіюйте результати з консолі для кожного з 5 демо-запитів.

### Запит 1: `"my laptop screen is broken"` → очікувана категорія: `technical`

| Метод           | Час (ms) | Топ-1 результат (коротко)                | Recall 3/5 (≥3 з top-5 правильна категорія?) |
|-----------------|----------|------------------------------------------|:--------------------------------------------:|
| BM25            | 1.96     | My laptop screen flickers constantly     | так |
| Cosine numpy    | 0.31     | The item I received has a cracked screen | так |
| Fusion RRF      | 0.02     | My laptop screen flickers constantly     | так |
| Qdrant :memory: | 1.84     | The item I received has a cracked        | так |

### Запит 2: `"I can't authenticate my identity"` → очікувана категорія: `account`

| Метод           | Час (ms) | Топ-1 результат (коротко)            | Recall 3/5 |
|-----------------|----------|--------------------------------------|:----------:|
| BM25            | 2.10     | Can't complete identity verification | так |
| Cosine numpy    | 0.35     | Can't complete identity verification | так |
| Fusion RRF      | 0.01     | Can't complete identity verification | так |
| Qdrant :memory: | 0.94     | Can't complete identity verification | так |

### Запит 3: `"money problems with my purchase"` → очікувана категорія: `billing`

| Метод           | Час (ms) | Топ-1 результат (коротко)          | Recall 3/5 |
|-----------------|----------|------------------------------------|:----------:|
| BM25            | 2.04     | My company's purchase order number | ні  |
| Cosine numpy    | 0.31     | My account doesn't show the purchase | ні  |
| Fusion RRF      | 0.01     | My account doesn't show the purchase | так |
| Qdrant :memory: | 0.81     | My account doesn't show the purchase | ні  |

### Запит 4: `"package not delivered to my address"` → очікувана категорія: `shipping`

| Метод           | Час (ms) | Топ-1 результат (коротко)                  | Recall 3/5 |
|-----------------|----------|--------------------------------------------|:----------:|
| BM25            | 2.02     | I want to change the email address         | ні  |
| Cosine numpy    | 0.31     | The courier marked the parcel as delivered | так |
| Fusion RRF      | 0.01     | The package was returned to sender         | ні  |
| Qdrant :memory: | 0.84     | The courier marked the parcel as delivered | так |

### Запит 5: `"want to send the item back for a refund"` → очікувана категорія: `returns`

| Метод           | Час (ms) | Топ-1 результат (коротко)                | Recall 3/5 |
|-----------------|----------|------------------------------------------|:----------:|
| BM25            | 1.75     | I returned the wrong item by mistake     | так |
| Cosine numpy    | 0.16     | I requested a partial refund for an item | так |
| Fusion RRF      | 0.01     | I requested a partial refund for an item | так |
| Qdrant :memory: | 0.55     | I requested a partial refund for an item | так |

### Приклад: Ticket Helper

*(Ticket Helper використовує **останній** демо-запит. У `--quick` режимі кластери називаються "Cluster 0", "Cluster 1" тощо — для LLM-назв запустіть без `--quick`.)*

**Новий тікет:** "want to send the item back for a refund"

**Підказана категорія (majority top-3):** returns

**Найближча назва кластера (k-means + LLM):** Order Issues

**Подібні звернення:**
1. [billing] I requested a partial refund for an item I returned but got nothing...
2. [returns] I returned the wrong item by mistake - how do I send back the correc...
3. [returns] I received a refund for only part of the order, not all items I return...

---

## 3. Latency-Quality Frontier

Заповніть середні значення по 5 запитах. Cosine numpy — навчальний baseline, він показує що Qdrant робить ту саму математику; в production його не використовують.

Значення виводяться автоматично в кінці скрипта — рядок **"Summary — avg over all demo queries"**. Скопіюйте звідти:

| Метод                       | Avg recall@5 | Avg latency (ms) | Production-ready?         |
|-----------------------------|:------------:|:----------------:|---------------------------|
| BM25 keyword                | 3.0 / 5      | 1.97 ms          | ✓ (для keyword)           |
| Cosine numpy *(baseline)*   | 3.8 / 5      | 0.28 ms          | ✗ O(n), не масштабується  |
| Fusion RRF                  | 3.6 / 5      | 0.01 ms          | ✓ (BM25 + cosine)         |
| Qdrant :memory: *(TODO 5)*  | 3.8 / 5      | 1.00 ms          | ✓ (vector DB)             |

**Qdrant vs Cosine numpy overlap:** 5/5 (має бути 5/5 — вони роблять одне і те саме)

*(Бонус reranker — окремо в секції 5)*

**Висновок:** Який метод дав найвищий recall? Яке рішення обрали б для production helpdesk де точність важливіша за latency? Чому cosine numpy не підходить для прод, навіть якщо зараз він швидший за Qdrant?

The highest recall came from Cosine and Qdrant, both 3.8/5 - the embedding methods beat BM25 (3.0). For a production helpdesk where accuracy matters more than speed, I would choose Qdrant: it reaches the same recall as cosine but scales to millions of tickets.  Cosine numpy is only faster now because there are just 300 vectors. It is brute-force O(n), comparing the query to every vector on each search and keeping them all in memory.


---

## 4. Висновки

**1.** Які типи запитів краще знаходить BM25? Які — cosine? Наведіть конкретний приклад із запитів 2 або 5.

BM25 works best when the query uses the same words as the ticket, because it matches exact tokens. Cosine works best when the meaning is the same but the words are different, because it compares semantic vectors.

Query 2 ("I can't authenticate my identity", category `account`) shows this well: cosine reaches 5/5 while BM25 gets only 4/5. Cosine finds tickets like "Can't log in even though I'm sure the password is correct" and "I enabled two-step verification but now can't get back in" - they share no keywords with the query, but cosine understands they mean the same thing. BM25 cannot see this link and instead returns a billing ticket that just happens to share a word.

**2.** Порівняйте Qdrant :memory: і cosine numpy за точністю — overlap вивів скрипт. Що ви побачили? Чому результати майже ідентичні?

The overlap was 5/5 for every query, so the results are identical. This happens because at 300 tickets Qdrant does exact cosine search - the same math as our numpy baseline, just inside a real database. The difference only shows up at large scale: with millions of vectors Qdrant switches to approximate search (ANN), which loses a tiny bit of accuracy but stays fast, while numpy would become too slow because it compares the query with every single vector.

**3.** Проаналізуйте ARI-таблицю з секції 1. При якому k ARI досягає піку? Що відбувається з кластерами при k нижче і вище оптимального?

ARI reaches its peak at k=6 (0.523). Below 6 the model under-clusters: categories that should be separate are merged into one group. Above 6 it over-clusters: tickets that belong to one category are split across several clusters. k=6 is the point where the embedding model naturally separates the tickets, even though the ground truth has 7 categories - some of them overlap too much for the model to tell apart.
**4.** Fusion RRF: чи вплинув він на топ-1 порівняно з окремими методами? При якому із запитів найбільша різниця?

Most of the time Fusion did not create a better top-1 - it simply copied the top-1 of whichever single method was stronger (BM25 in query 1, cosine in queries 3 and 5). The biggest positive difference is query 3 ("money problems with my purchase"): BM25 and cosine each got only 2/5, but Fusion reached 4/5. Query 4 is the opposite case - Fusion dropped to 2/5 (cosine alone got 5/5). So Fusion helps when both methods are reasonable and disagree usefully, but it hurts when one method is clearly weaker and adds noise.

**5.** Що таке latency-quality tradeoff у пошуку? Де на вашій таблиці знаходиться Pareto frontier?

The latency-quality tradeoff means that better results usually cost more time, so you cannot always maximise both - the right method depends on whether the use case needs speed or accuracy.

On the table the top-quality corner is Cosine and Qdrant (both 3.8/5). At large scale Qdrant loses a tiny bit of accuracy from approximate search, but it stays fast, while Cosine is O(n) and cannot scale - so Qdrant is the real production point on the frontier. BM25 is dominated: it is both slower and lower recall (3.0/5). Fusion is also dominated, but for a different reason - its 0.01 ms is only the merge step, and it needs BM25 + cosine to run first (≈2.26 ms end-to-end), so it is the slowest method while its recall (3.6/5) is still below a single vector search.

---

## 5. Бонус: Reranker порівняння

Запустіть: `uv run starter.py --rerank --query "I can't log into my account"`

| Модель              | Топ-1 результат (коротко)                        | Precision@1 (топ-1 правильна категорія?) | Latency (ms) |
|---------------------|--------------------------------------------------|:----------------------------------------:|--------------|
| ms-marco-MiniLM     | Can't log in even though the password is correct | так                                      | 6701 ms      |
| bge-reranker-base   | Someone accessed my account without permission   | так                                      | 16001 ms     |
| bge-reranker-v2-m3  | Can't log in even though the password is correct | так                                      | 20286 ms     |

**Яка модель дала найкращий результат?**

All five candidates were already `account` tickets, so precision@1 is good for every model — the category metric cannot separate them here. The real difference is which account ticket ranks first. ms-marco and bge-v2-m3 both put the exact match "Can't log in even though the password is correct" at #1, which is the most relevant answer. bge-base put "Someone accessed my account" first, which is about account intrusion, not a login problem, so it was slightly worse. bge-v2-m3 is the strongest model in general, but it is also the slowest.

**Чому ms-marco програє на коротких support-ticket текстах?** _(підказка: на яких даних вона тренувалась?)_

ms-marco was trained on the MS MARCO passage-ranking dataset — Bing search queries paired with long web passages. It is tuned for longer, information-rich text, not one-sentence support tickets, and its raw scores are uncalibrated logits (here from +3.26 down to -9.71), which are hard to compare or threshold. On short tickets there is little context to work with, so it is usually less reliable — although in this particular query it still found the right top-1, because all candidates were already account tickets and the query shared the literal words "log in".

---

## 6. Бонус: свій запит

Придумайте запит і запустіть: `uv run starter.py --query "ваш запит"`

**Ваш запит:** "someone hacked into my profile" (target category: `account`)

| Метод           | Топ-1 результат (коротко)                          | Overlap з Cosine |
|-----------------|----------------------------------------------------|:----------------:|
| BM25            | Someone accessed my account without my permission  | 1 / 5            |
| Cosine numpy    | Someone accessed my account without my permission  | —                |
| Qdrant :memory: | Someone accessed my account without my permission  | 5 / 5            |

Чому BM25 і cosine дали саме такі результати? _(2–3 речення)_

All three methods agree on the top-1 result, because "Someone accessed my account without my permission" both shares literal words ("someone" and "my") with the query and is the closest in meaning. But below the top-1 they diverge completely - BM25 vs cosine overlap is only 1/5. BM25 found other category by surface words: it ranked "My profile picture won't upload" high (it shares "profile") and pulled in two shipping tickets about "someone else's order" (they share the word "someone" but have nothing to do with hacking). Cosine ignored the exact words and returned five account-security tickets (suspicious activity, unrequested password reset, logins I didn't make) that all match the meaning - the word "hacked" never appears in the dataset, so BM25 cannot use it, while cosine understands the intent. Qdrant matched cosine 5/5 because it runs the same exact cosine math.