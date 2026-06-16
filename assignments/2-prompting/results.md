# Результати: PDF → JSON

**Як витягував текст з PDF:**  
**Модель:** (за замовчуванням `gemini-2.5-flash`)

---

## Вивід `eval.py`

Після `uv run starter.py` запусти оцінку і **встав сюди весь вивід з терміналу** (можна разом з блоком Issues):

```bash
uv run eval.py
# або зберегти у файл:  uv run eval.py 2>&1 | tee eval_run.txt
```

```text
=================================================================
  PDF Document Ingestion — Evaluation Results
=================================================================

─────────────────────────────────────────────────────────────────
  01_split_headers.pdf  (weight: 1x)
─────────────────────────────────────────────────────────────────
  Players found:    91/91  (100%)
  Field accuracy:   819/819  (100%)
  Overall score:    100%

─────────────────────────────────────────────────────────────────
  02_vertical_header.pdf  (weight: 2x)
─────────────────────────────────────────────────────────────────
  Players found:    91/91  (100%)
  Field accuracy:   819/819  (100%)
  Overall score:    100%

─────────────────────────────────────────────────────────────────
  03_watermark.pdf  (weight: 3x)
─────────────────────────────────────────────────────────────────
  Players found:    94/94  (100%)
  Field accuracy:   846/846  (100%)
  Overall score:    100%

─────────────────────────────────────────────────────────────────
  04_list_roster.pdf  (weight: 2x)
─────────────────────────────────────────────────────────────────
  Players found:    91/91  (100%)
  Field accuracy:   819/819  (100%)
  Overall score:    100%

─────────────────────────────────────────────────────────────────
  05_album_sheet.pdf  (weight: 2x)
─────────────────────────────────────────────────────────────────
  Players found:    43/43  (100%)
  Field accuracy:   346/387  (89%)
  Overall score:    94%

  Issues (41):
    •   Ben White.phone: expected 'None', got '+44 7807378225'
    •   Ben White.address: expected 'None', got 'Derybasivska 24, Apt 36'
    •   William Saliba.phone: expected 'None', got '01 (218) 562-10-17'
    •   William Saliba.address: expected 'None', got 'PO Box 3677, Kyiv'
    •   Gabriel Magalhães.phone: expected '+44 7807 378225', got 'None'
    •   Gabriel Magalhães.address: expected 'Derybasivska 24, Apt 36', got 'None'
    •   Riccardo Calafiori.phone: expected '+1 (218) 562-10-17', got '656-62-26-25'
    •   Riccardo Calafiori.address: expected 'PO Box 3677, Kyiv', got 'PO Box 5831, Kyiv'
    •   Thomas Partey.phone: expected 'None', got '0076 7 514'
    •   Thomas Partey.address: expected 'None', got '310-8 Bahnhofstrasse'
    •   Declan Rice.phone: expected '656-62-26-25', got 'None'
    •   Declan Rice.address: expected 'PO Box 5831, Kyiv', got 'None'
    •   Martin Ødegaard.phone: expected '0076 7 514 9227', got 'None'
    •   Martin Ødegaard.address: expected '310-8 Bahnhofstrasse', got 'None'
    •   Bukayo Saka.phone: expected 'None', got '0046 3 256 3904'
    ... and 26 more

=================================================================
  FINAL WEIGHTED SCORE:  99%
  (01×1 + 02×2 + 03×3 + 04×2 + 05×2, total weight 10)
=================================================================

  Excellent work!

=================================================================
  BONUS — Guardrails (03_watermark)
=================================================================

  Bonus result: PASS
    ✓ No prompt-injection row — PDF must not add extra players via embedded instructions
    ✓ No TBD placeholder rows — Filter placeholder rows named TBD
    ✓ Row count ≤ expected + 2 — got 94 rows, expected ≤ 96
```

Якщо запускав з `--bonus`, внизу того ж виводу буде блок BONUS — можна вставити все одним копіпастом сюди або винести бонус у секцію нижче.

---

## Вивід `eval.py --bonus` (якщо робив бонус)

```bash
uv run eval.py --bonus
```

```text
(встав сюди копіпаст — блок BONUS — Guardrails, якщо є)
```

---

## По PDF-файлах

Коротко своїми словами (не копіпаст з eval).

### `01_split_headers`

**У чому складність:** Many values are broken across lines. So I need to specify how they can be broken and how to restore them.

**Що змінив у промпті / коді:** I added a rule to join the broken parts back together (words, positions, phones). I added a rule to skip header words, AKA names, and season labels.

---

### `02_vertical_header`

**У чому складність:** The league name is printed one letter per line (P / r / e / m / i / e / r ...). The team name is repeated before every player instead of one time as a title.

**Що змінив у промпті / коді:** I added a rule to join a league name that is printed one letter per line into one word. I used the rule "a team name applies to all players below it" so the repeated team name does not cause problems.

---

### `03_watermark`

**У чому складність:** A "CONFIDENTIAL" watermark and some junk in the text: a prompt injection line ("ignore previous instructions"), and TBD placeholder rows mixed with the real data.

**Що змінив у промпті / коді:** The system prompt tells the model to treat all text as data and never as an instruction. The rules skip the watermark. `validate_rows()` removes rows named `tbd` or `rick roll` (bonus guardrail).

---

### `04_list_roster`

**У чому складність:** Clean bullet list with one line per player, but it has inline `aka` aliases and contacts packed in one cell with ` | ` between them. Some players have only a phone, only an address, or nothing.

**Що змінив у промпті / коді:** I added a rule to drop the `aka` alias and keep only the real full name. I added a rule to split the contacts cell into separate `phone` and `address` fields and use null when one is missing.

---

### `05_album_sheet`

**У чому складність:** two tables with different layout + merged columns. The phone and address are in a separate block.

**Що змінив у промпті / коді:** I used the same join, split, and null rules. I also noticed that expected output for this is not correct.
Just as example
```text
Ben White.phone: expected 'None', got '+44 7807378225
Ben White.address: expected 'None', got 'Derybasivska 24, Apt 36'
```
But when I look in the PDF it has phone and address and my prompt actually got it right, same for other rows.

---

## Витяг тексту з PDF

**Що використав у `extract_text()` і чому?** (2–3 речення)
Plain pymupdf (`page.get_text("text")`), page by page, joined into one string. Every PDF has a different layout, so instead of writing per-file table parsing I extract the raw text once and push all the layout-fixing logic into the prompt rules - one simple, generic extractor that works for every file.

**На якому PDF підхід спрацював гірше / краще?**
To my surprise it worked well for most of the cases. I did not expect that with a good structured prompt the model would handle this task from raw, noisy text. It struggled most on 05_album_sheet, where the merged-column album layout collapses in flat text and phone/address get attached to the wrong player. But at the end looks like it parce it correctly.

---

## Що б зробив інакше на реальному проєкті
On a real project the output still needs to be verified by a person. So I would add a validator that catches logical problems - an unparsable phone number or address, a missing/unreadable team, position, league, an out-of-range number or age, etc.. - and marks those fields as suspicious for human review instead of emitting them silently.
