"""python3 -m mpesa_analyzer STATEMENT.csv --categories CATEGORIES.json [--top N]. Prints the report; writes no file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mpesa_analyzer.analyzer import StatementError, monthly_totals, parse_statement, top_spenders


def report(txns: list, rules: dict, top: int) -> str:
    if not txns:
        return "No completed transactions.\n"
    lines = ["Monthly spending"]
    for month, data in sorted(monthly_totals(txns, rules).items()):
        lines.append(month)
        for category, amount in sorted(data["spent"].items()):
            lines.append(f"  {category}: {amount:.2f}")
        lines.append(f"  Total spent: {data['total_spent']:.2f}")
        lines.append(f"  Received: {data['received']:.2f}")
    ranked = top_spenders(txns, top)
    lines += ["", f"Top spenders ({len(ranked)})"]
    lines += [f"{i}. {name}: {amount:.2f}" for i, (name, amount) in enumerate(ranked, 1)]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="mpesa_analyzer")
    parser.add_argument("statement")
    parser.add_argument("--categories", required=True)
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args(argv)
    try:
        rules = json.loads(Path(args.categories).read_text(encoding="utf-8"))
        if not isinstance(rules, dict) or not all(isinstance(v, list) for v in rules.values()):
            raise StatementError("the categories file is not an object of name to a list of keywords")
        txns = parse_statement(Path(args.statement).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        message = str(exc) if isinstance(exc, StatementError) else "a file could not be read or is not valid"
        print(f"error: {message}", file=sys.stderr)
        return 2
    sys.stdout.write(report(txns, rules, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
