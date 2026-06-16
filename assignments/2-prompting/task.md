# Домашнє завдання: PDF → JSON (витягування з документів)

## Базовий код у `starter.py` — реалізуй `extract_text()`, напиши `PROMPT`, опційно `validate_rows()`

## Мета завдання

Навчитися витягувати структуровані дані з PDF: один скрипт `PDF → текст → LLM → JSON`, який працює, коли верстка і формат файлів різняться.

У вас **5 PDF** з ростером футбольних гравців (5 ліг, 7 команд). Кожен файл зібраний по-іншому — відкрийте їх і подивіться, перш ніж писати промпт.

---

## Що потрібно зробити

1. **`extract_text(pdf_path)`** — витягнути текст з PDF. Бібліотеку обери сам (погугли / PyPI).
2. **`PROMPT`** — промпт для LLM, щоб повертав JSON з плоским списком гравців.
3. **(Бонус)** **`validate_rows()`** — відфільтрувати сміття після LLM (заглушки, зайві рядки, невідомі команди).

Результати — у `output/<stem>.json`. Перевірка: `uv run eval.py`.

---

## 🛠 Інструментарій

* **LLM:** `openrouter/google/gemini-2.5-flash` (за замовчуванням у `starter.py`).
* **API ключ:** `export OPENROUTER_API_KEY="sk-or-..."`

```bash
# Усі 5 PDF
uv run starter.py

# Один файл (зручно для ітерацій)
uv run starter.py pdfs/05_album_sheet.pdf

# Оцінка
uv run eval.py
uv run eval.py 05_album_sheet
uv run eval.py --bonus    # бонус: перевірки на 03_watermark
```

---

## 📂 PDF-файли

| Файл | Вага |
|------|------|
| `01_split_headers.pdf` | ×1 |
| `02_vertical_header.pdf` | ×2 |
| `03_watermark.pdf` | ×3 |
| `04_list_roster.pdf` | ×2 |
| `05_album_sheet.pdf` | ×2 |

У чому складність у кожному файлі — опиши сам у [`results.md`](results.md) після першого прогону.

---

## Очікуваний JSON формат

Плоский список гравців у `output/*.json`:

```json
[
  {
    "league": "Premier League",
    "team": "Arsenal",
    "name": "Bukayo Saka",
    "position": "RW",
    "number": 7,
    "age": 23,
    "nationality": "England",
    "phone": "+44 7123 123456",
    "address": "12 King St, London"
  }
]
```

| Поле | Тип | Опис |
|------|-----|------|
| `league` | string | Назва ліги |
| `team` | string | Назва команди |
| `name` | string | Повне ім'я гравця |
| `position` | string \| null | GK, CB, CAM, RW, … |
| `number` | integer \| null | Номер |
| `age` | integer \| null | Вік |
| `nationality` | string \| null | Національність |
| `phone` | string \| null | Телефон |
| `address` | string \| null | Адреса |

---

## Оцінювання

`eval.py` рахує по кожному PDF окремо:

- **Скільки гравців знайшов** (40%)
- **Точність полів** (60%)

**Зважена оцінка:** `01×1 + 02×2 + 03×3 + 04×2 + 05×2` (знаменник 10)

| Оцінка | Результат |
|--------|-----------|
| ≥ 95%  | Відмінно |
| ≥ 80%  | Добре |
| ≥ 60%  | Прийнятно |
| < 60%  | Потребує доопрацювання |

Бали впиши в [`results.md`](results.md) — **копіпастом** повний вивід `uv run eval.py` (і `--bonus`, якщо робив).

---

## Бонус A: Фільтрація після екстракції

Допиши `validate_rows()` у `starter.py`:

- прибери рядки-заглушки (наприклад `TBD`)
- прибери рядки, які з'явились через інструкції з PDF, а не з даних
- відкинь рядки з невідомою парою league/team

Перевірка: `uv run eval.py --bonus` (тільки для `03_watermark`, на основну оцінку не впливає).

---

## Бонус B: Як витягував текст

У `results.md` коротко: що використав для `extract_text()` і чи була різниця між PDF.
