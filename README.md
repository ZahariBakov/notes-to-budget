# notes-to-budget

*[Български](README.bg.md)*

Turn the short expense notes you type on your phone into a monthly budget
workbook, and answer questions only about the entries that are unclear.

> **Status: early development.** The project skeleton is in place; the
> features below are being built stage by stage.

## The idea

You write notes like this during the day:

```
14 - 120 / 340 / 1500
 - 12 - lunch - R
 - 35 - groceries - R
 + 300 - rent - C
 - 200 - from card to cash
```

The first line is the day and your morning balances (cash / online wallet /
bank card). Every other line is one movement of money.

`notes-to-budget` will:

1. **Read** the notes and understand dates, amounts, accounts and balances.
2. **Categorise** each entry using rules you own (keywords, people, trips).
3. **Reconcile** the entries against your balances and explain differences.
4. **Ask** you only about what it could not decide, and remember the answer
   as a rule.
5. **Build** an Excel workbook: one sheet per month plus a yearly summary.

## Your data stays yours

The repository contains code and invented examples only. Your notes,
settings, ledgers and workbooks live in a separate folder on your computer.
A commit check refuses files that look like personal data.

## Languages

Code is in English. Documentation, workbook labels and messages are available
in English and Bulgarian. Categories, accounts and keywords are your own
settings, in any language.

## Development

```
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e .[dev]
pytest
ruff check .
git config core.hooksPath .githooks
```

## License

MIT. See [LICENSE](LICENSE).
