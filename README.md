# col — Cost of Living

A two-step CLI tool for analyzing personal expenses exported from **PKO BP** (Polish bank). It preprocesses raw bank CSV exports into a clean format and then groups, maps, and sums them by category.

---

## Workflow

```
PKO BP export (.csv)
        │
        ▼
preprocess_pkobp.py      →   .preprocessed/<filename>.csv
        │
        ▼
      col.py             →   grouped & summed table printed to stdout
```

---

## Files

### `preprocess_pkobp.py`

Cleans a raw PKO BP CSV export and extracts only the two columns that `col.py` needs: **group name** and **amount**.

**Usage:**
```bash
python preprocess_pkobp.py export1.csv export2.csv ...
```

---

### `col.py`

Reads one or more preprocessed CSVs, applies category mappings, skips ignored records, and prints a sorted expense summary table.


**Usage:**
```bash
python col.py .preprocessed/jan.csv .preprocessed/feb.csv
```

**Example output:**
```
Group Key              |          Amount
----------------------------------------
bankomat               |        -400.00
sklep                  |        -320.50
zarcie na miescie      |        -185.00
...
----------------------------------------
     PLUS              |         500.00
     MINUS             |        -905.50
----------------------------------------
TOTAL                  |        -405.50
```

---

### `mapping`

A CSV file (no header) with keyword-to-category rules used by `col.py`. Each line:
```
<keyword>,<category>
```

- Matching is **case-insensitive substring** — if the group name contains the keyword, it is replaced with the category.
- First match wins (order matters).
- Controls how raw merchant names are folded into meaningful budget categories (e.g. `biedronka,sklep`, `apteka,apteka`, `pizza,pizza`).

Edit this file to add or rename categories. Run `print_group` to check existing entries.

---

### `ignored`

A plain text file listing group names (one per line, as they appear after mapping) that should be **completely excluded** from the summary. Useful for filtering out internal transfers or your own name appearing as a recipient.

Example content:
```
PIOTR ANDRZEJ CZAPLA
```

---

### `print_group`

A small bash helper that searches `mapping` for a keyword and prints matching entries (just the keyword column). Useful for quickly checking if a merchant is already mapped.

**Usage:**
```bash
./print_group biedronka
```

---

### `.preprocessed/`

Directory where `preprocess_pkobp.py` writes its output. All `*.csv` files are git-ignored (see `.gitignore`), so raw bank data and preprocessed files never enter version control.

---

### `.gitignore`

Ignores:
- `**/*.csv` — all CSV files (raw exports and preprocessed data stay local)

---

## Quickstart

```bash
# 1. Export your transaction history from PKO BP as CSV
# 2. Preprocess it
python preprocess_pkobp.py 02.2026.csv

# 3. Analyze
python col.py .preprocessed/02.2026.csv
```

---

## Customization

- **Add a new merchant mapping:** append a line to `mapping`, e.g. `starbucks,kawa`
- **Ignore a payee:** append their name (as it appears in the preprocessed CSV) to `ignored`
- **Multiple months:** pass multiple preprocessed files to `col.py` — amounts are merged and summed across all files
