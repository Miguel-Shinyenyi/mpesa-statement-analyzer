"""Read an M-Pesa statement and total it. Nothing here touches a file or a network (see SPEC.md)."""
import csv
import io
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

COLUMNS = ["Receipt No.", "Completion Time", "Details", "Transaction Status", "Paid in", "Withdrawn", "Balance"]
UNCATEGORIZED = "Uncategorized"

_AMOUNT = re.compile(r"(\d{1,3}(,\d{3})+|\d+)(\.\d+)?", re.ASCII)
_TIME = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", re.ASCII)


class StatementError(Exception):
    """A statement that cannot be read. The message never holds text taken from a row."""


@dataclass(frozen=True)
class Txn:
    receipt: str
    when: datetime
    details: str
    status: str
    paid_in: Decimal
    withdrawn: Decimal
    balance: Decimal


def _amount(value, column, line):
    if value == "":
        return Decimal("0")
    if not _AMOUNT.fullmatch(value):
        raise StatementError(f"line {line}: {column} is not a valid amount")
    return Decimal(value.replace(",", ""))


def _time(value, line):
    if _TIME.fullmatch(value):
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    raise StatementError(f"line {line}: Completion Time is not a valid YYYY-MM-DD HH:MM:SS date")


def _rows(text):
    """Yield (number of the line the row starts on, fields)."""
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    line = 1
    try:
        for row in reader:
            yield line, row
            line = reader.line_num + 1
    except csv.Error:
        raise StatementError(f"line {line}: the CSV is malformed") from None


def parse_statement(text):
    rows = _rows(text)
    _, header = next(rows, (1, []))
    missing = [name for name in COLUMNS if name not in header]
    if missing:
        raise StatementError(f"line 1: missing column: {', '.join(missing)}")
    if header != COLUMNS:
        raise StatementError(f"line 1: the header must be exactly: {','.join(COLUMNS)}")

    status_at = COLUMNS.index("Transaction Status")
    txns = []
    for line, row in rows:
        if not row or (len(row) > status_at and row[status_at] != "Completed"):
            continue
        if len(row) != len(COLUMNS):
            raise StatementError(f"line {line}: wrong number of fields")
        receipt, when, details, status, paid_in, withdrawn, balance = row
        txns.append(Txn(receipt, _time(when, line), details, status,
                        _amount(paid_in, "Paid in", line),
                        _amount(withdrawn, "Withdrawn", line),
                        _amount(balance, "Balance", line)))
    return txns


def categorize(txn, rules):
    details = txn.details.casefold()
    for category, keywords in rules.items():
        if any(keyword.casefold() in details for keyword in keywords):
            return category
    return UNCATEGORIZED


def counterparty(txn):
    return txn.details.rsplit(" - ", 1)[-1]


def monthly_totals(txns, rules):
    totals = {}
    for txn in txns:
        month = totals.setdefault(txn.when.strftime("%Y-%m"),
                                  {"spent": {}, "total_spent": Decimal("0"), "received": Decimal("0")})
        month["received"] += txn.paid_in
        if txn.withdrawn:
            category = categorize(txn, rules)
            month["spent"][category] = month["spent"].get(category, Decimal("0")) + txn.withdrawn
            month["total_spent"] += txn.withdrawn
    return totals


def top_spenders(txns, n):
    spent = {}
    for txn in txns:
        name = counterparty(txn)
        spent[name] = spent.get(name, Decimal("0")) + txn.withdrawn
    ranked = sorted((item for item in spent.items() if item[1] > 0), key=lambda item: (-item[1], item[0]))
    return ranked[:max(n, 0)]
