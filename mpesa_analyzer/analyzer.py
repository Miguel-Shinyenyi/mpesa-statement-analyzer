"""The functions of SPEC.md. Nothing here reads or writes a file, and no message carries the text of a row."""
from __future__ import annotations

import csv
import io
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

COLUMNS = ("Receipt No.", "Completion Time", "Details", "Transaction Status", "Paid in", "Withdrawn", "Balance")
UNCATEGORIZED = "Uncategorized"


class StatementError(ValueError):
    """The statement is not readable. The message names a line number or a column, never the text of a row."""


@dataclass(frozen=True)
class Txn:
    receipt: str
    when: datetime
    details: str
    status: str
    paid_in: Decimal
    withdrawn: Decimal
    balance: Decimal


def _amount(raw: str, line: int, column: str) -> Decimal:
    text = (raw or "").strip().replace(",", "")
    if not text:
        return Decimal("0")
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise StatementError(f"line {line}: the {column} amount is not a number") from None
    if not value.is_finite():
        raise StatementError(f"line {line}: the {column} amount is not a number")
    return value


def parse_statement(text: str) -> list:
    """The Completed rows of a statement as Txn objects. Other rows are ignored."""
    reader = csv.DictReader(io.StringIO(text))
    names = reader.fieldnames or []
    for column in COLUMNS:
        if column not in names:
            raise StatementError(f"the statement has no {column} column")
    txns = []
    for row in reader:
        line = reader.line_num
        if (row.get("Transaction Status") or "").strip() != "Completed":
            continue
        try:
            when = datetime.strptime((row.get("Completion Time") or "").strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise StatementError(f"line {line}: the Completion Time is not YYYY-MM-DD HH:MM:SS") from None
        txns.append(Txn((row.get("Receipt No.") or "").strip(), when, row.get("Details") or "", "Completed",
                        _amount(row.get("Paid in"), line, "Paid in"), _amount(row.get("Withdrawn"), line, "Withdrawn"),
                        _amount(row.get("Balance"), line, "Balance")))
    return txns


def categorize(txn: Txn, rules: dict) -> str:
    """The first category in `rules` with a keyword in the details, ignoring case, else Uncategorized."""
    details = txn.details.lower()
    for category, keywords in rules.items():
        if any(k.lower() in details for k in keywords):
            return category
    return UNCATEGORIZED


def counterparty(txn: Txn) -> str:
    """The text of the details after the last ' - ', or all of it when there is none."""
    return txn.details.rsplit(" - ", 1)[-1] if " - " in txn.details else txn.details


def monthly_totals(txns: list, rules: dict) -> dict:
    """{'YYYY-MM': {'spent': {category: Decimal}, 'total_spent': Decimal, 'received': Decimal}}."""
    out: dict = {}
    for t in txns:
        month = out.setdefault(t.when.strftime("%Y-%m"), {"spent": defaultdict(Decimal), "total_spent": Decimal("0"), "received": Decimal("0")})
        if t.withdrawn:
            month["spent"][categorize(t, rules)] += t.withdrawn
        month["total_spent"] += t.withdrawn
        month["received"] += t.paid_in
    return {m: {"spent": dict(v["spent"]), "total_spent": v["total_spent"], "received": v["received"]} for m, v in out.items()}


def top_spenders(txns: list, n: int) -> list:
    """(counterparty, total withdrawn), largest first, ties by name, at most n, nobody who spent nothing."""
    totals: dict = defaultdict(Decimal)
    for t in txns:
        totals[counterparty(t)] += t.withdrawn
    ranked = sorted(((name, total) for name, total in totals.items() if total > 0), key=lambda p: (-p[1], p[0]))
    return ranked[:max(n, 0)]
