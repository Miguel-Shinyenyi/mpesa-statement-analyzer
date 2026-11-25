# mpesa-statement-analyzer

A small local tool. It reads an M-Pesa statement saved as a CSV file, sorts the money going out into categories you define, and prints the monthly
totals and the people and shops you paid the most. It runs on your machine only: no network, no upload, and it writes nothing.

Status: the spec and the tests are written first (SPEC.md and tests/). The code does not exist yet; the tests fail until it does. A real statement
never goes in this repo: `*.csv` is ignored, and the tests use made-up transactions.

    python3 -m mpesa_analyzer STATEMENT.csv --categories categories.json --top 5
