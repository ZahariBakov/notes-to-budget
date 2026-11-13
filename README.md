# notes-to-budget

*[Български](README.bg.md)*

Turn the short expense notes you type on your phone into a monthly budget
workbook, and answer questions only about the entries that are unclear.

> **Status: early development.** Creating a data folder and checking your
> settings work today. Reading notes, categorising, reconciling and building
> the workbook are being built stage by stage.

## Entering expenses on your phone

The simplest way to record an expense is a form: type the amount, choose a
category, choose the account. No free text for a program to decipher.

```
notes-to-budget form-script --data-folder my-budget
```

writes a Google Apps Script made from **your** categories and accounts. Run it
once in your own Google account and it creates:

- a **Google Form** you can pin to the home screen of your phone;
- a **spreadsheet for the current month** that receives every entry, shows
  plan against actual per category, and checks your account balances.

Only the current month lives in the cloud. At the end of the month you
download it and add it to the ledger on your own computer (in progress).

## What works today

```
notes-to-budget init my-budget --language en    # a data folder with starter settings
notes-to-budget check --data-folder my-budget   # are my settings valid?
notes-to-budget read-notes examples/en/notes/March-2026.txt --data-folder my-budget --show-entries
```

`read-notes` shows what the program understands in a notes file and lists
every line it could not read, with the line number and the reason. It changes
nothing. See [examples](examples/README.md) for the notes format.

```
notes-to-budget preview examples/en/notes/March-2026.txt --data-folder my-budget
```

`preview` shows the type and category chosen for every entry and the rule
that chose it. Entries no rule could decide are flagged for your review,
never guessed. The rules are yours: keywords, people, holidays and your own
earlier answers, all in plain text files in `my-budget/config`.

`init` gives you categories, accounts and rules to start from; edit the files
in `my-budget/config` to match your own life. `check` reads them and explains
any problem in plain words, with the file and the place to look at.

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
