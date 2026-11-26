# Spec: mpesa-statement-analyzer (tests first)

## Purpose

Read an M-Pesa statement CSV, sort the money that went out into categories the user defines, and print the monthly totals and the largest
spenders. Local only. Plain standard library Python 3.10 or later. No network, no file written, no real data in this repo.

## The input

A CSV with this header, in this order: `Receipt No.,Completion Time,Details,Transaction Status,Paid in,Withdrawn,Balance`.

- `Completion Time` is `YYYY-MM-DD HH:MM:SS`.
- An amount may have a thousands comma inside quotes (`"1,350.00"`); an empty amount is zero.
- Only rows whose `Transaction Status` is `Completed` count. Every other row is ignored.
- A statement that has no `Completed` row is a valid statement with nothing to report.

## The categories file

JSON: an object of category name to a list of keywords, in order, for example `{"Food": ["super mart"], "Transport": ["bus fare"]}`. A row goes to
the FIRST category in the file whose keyword appears in its `Details`, ignoring case. A row that matches none goes to `Uncategorized`.

## The functions (package `mpesa_analyzer`)

- `parse_statement(text) -> list[Txn]`. `Txn` has `receipt`, `when` (a `datetime`), `details`, `status`, `paid_in`, `withdrawn`, `balance`; the three
  amounts are `Decimal`. Raises `StatementError` for a missing column or a bad number or date. The message names the line number and what is wrong,
  and never contains the text of a row.
- `categorize(txn, rules) -> str`. `rules` is the ordered mapping above.
- `counterparty(txn) -> str`. The text of `Details` after the last ` - `, or the whole `Details` when there is none.
- `monthly_totals(txns, rules) -> dict`. Keys are `YYYY-MM`. Each value is `{"spent": {category: Decimal}, "total_spent": Decimal, "received": Decimal}`.
  `spent` sums `withdrawn`; `received` sums `paid_in`. The month is the month of `Completion Time`.
- `top_spenders(txns, n) -> list[tuple[str, Decimal]]`. Total `withdrawn` per counterparty, largest first, ties by name (A to Z), at most `n`,
  counterparties that spent nothing left out.

## The command

`python3 -m mpesa_analyzer STATEMENT.csv --categories CATEGORIES.json [--top N]` (N defaults to 5). It prints this report to standard output and exits 0:

    Monthly spending
    2026-01
      Food: 1700.00
      Transport: 120.00
      Uncategorized: 500.00
      Total spent: 2320.00
      Received: 50000.00

    Top spenders (3)
    1. Power Company: 2000.00
    2. Super Mart: 1700.00
    3. Jane Roe: 500.00

Months are in date order; categories inside a month are in name order; amounts have two decimals. With no `Completed` row it prints `No completed transactions.`
and exits 0. With a bad file it prints one line `error: ...` to standard error, no traceback, and exits 2.

## Rules that never bend

- No network: the code imports nothing that opens a connection.
- Nothing is written: no file, no cache, no log.
- A real statement is never committed: `*.csv` is in `.gitignore`.
- The tests use only the made-up rows in `tests/test_analyzer.py`.

## Decisions log

- 2026-11-25: spec and tests first, written by the builder; the code is built later through umwayi-os with Kiro doing real work in it (G-0054).

- 2026-11-26: the code is built by Claude Code against these 17 tests (the owner's order, G-0094). All 17 pass on the local run. No Kiro work is claimed for it.

## Open questions

- Which M-Pesa statement layouts exist besides this header? Recommendation: support this one now and add a layout only with a made-up sample of it.
