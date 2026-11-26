"""Read an M-Pesa statement CSV, sort the money that went out into categories and total it by month. Standard library only (see SPEC.md)."""
from mpesa_analyzer.analyzer import (StatementError, Txn, categorize, counterparty, monthly_totals, parse_statement,
                                     top_spenders)

__all__ = ["StatementError", "Txn", "categorize", "counterparty", "monthly_totals", "parse_statement", "top_spenders"]
