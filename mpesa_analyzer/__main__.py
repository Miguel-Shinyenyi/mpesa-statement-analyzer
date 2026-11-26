"""The command line: python3 -m mpesa_analyzer STATEMENT.csv --categories CATEGORIES.json [--top N]."""
import argparse
import json
import sys

from .analyzer import StatementError, monthly_totals, parse_statement, top_spenders


class InputError(Exception):
    """A file the command cannot use. The message is one line."""


def _read(path, what):
    try:
        with open(path, encoding="utf-8-sig", newline="") as handle:
            return handle.read()
    except OSError as error:
        raise InputError(f"cannot read the {what} file: {error.strerror}") from None
    except UnicodeError:
        raise InputError(f"the {what} file is not UTF-8 text") from None


def _rules(text):
    try:
        rules = json.loads(text)
    except (ValueError, RecursionError):
        raise InputError("the categories file is not valid JSON") from None
    if not (isinstance(rules, dict) and all(
            isinstance(keywords, list) and all(isinstance(keyword, str) for keyword in keywords)
            for keywords in rules.values())):
        raise InputError("the categories file must be an object of category name to a list of keywords")
    return rules


def _report(txns, rules, top):
    if not txns:
        return "No completed transactions."
    lines = ["Monthly spending"]
    for month, totals in sorted(monthly_totals(txns, rules).items()):
        lines.append(month)
        lines += [f"  {category}: {amount:.2f}" for category, amount in sorted(totals["spent"].items())]
        lines.append(f"  Total spent: {totals['total_spent']:.2f}")
        lines.append(f"  Received: {totals['received']:.2f}")
    spenders = top_spenders(txns, top)
    lines += ["", f"Top spenders ({len(spenders)})"]
    lines += [f"{rank}. {name}: {amount:.2f}" for rank, (name, amount) in enumerate(spenders, 1)]
    return "\n".join(lines)


def _count(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m mpesa_analyzer",
                                     description="Monthly spending and top spenders from an M-Pesa statement CSV.")
    parser.add_argument("statement", metavar="STATEMENT.csv")
    parser.add_argument("--categories", required=True, metavar="CATEGORIES.json")
    parser.add_argument("--top", type=_count, default=5, metavar="N")
    args = parser.parse_args(argv)
    try:
        rules = _rules(_read(args.categories, "categories"))
        txns = parse_statement(_read(args.statement, "statement"))
    except (InputError, StatementError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(_report(txns, rules, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
