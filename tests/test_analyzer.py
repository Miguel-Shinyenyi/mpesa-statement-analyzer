"""The tests of mpesa-statement-analyzer, written BEFORE the code (see SPEC.md). They fail until the package exists.
Every transaction here is made up. No real statement is read, and no network or file outside a temporary folder is used."""
import ast
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from mpesa_analyzer import StatementError, categorize, counterparty, monthly_totals, parse_statement, top_spenders

ROOT = Path(__file__).resolve().parent.parent
HEADER = "Receipt No.,Completion Time,Details,Transaction Status,Paid in,Withdrawn,Balance\n"
ROWS = (
    'AAA1,2026-01-05 08:14:02,Merchant Payment to 111111 - Super Mart,Completed,,"1,350.00","8,650.00"\n'
    'AAA2,2026-01-06 09:00:00,Funds received from - Employer Ltd,Completed,"50,000.00",,"58,650.00"\n'
    "AAA3,2026-01-07 18:30:10,Customer Payment to Small Business - Bus Fare Ltd,Completed,,120.00,\"58,530.00\"\n"
    "AAA4,2026-01-08 12:00:00,Merchant Payment to 222222 - Super Mart,Completed,,350.00,\"58,180.00\"\n"
    "AAA5,2026-01-09 12:00:00,Merchant Payment to 333333 - Failed Shop,Failed,,999.00,\"58,180.00\"\n"
    'AAA6,2026-02-01 00:00:00,Pay Bill to 444444 - Power Company,Completed,,"2,000.00","56,180.00"\n'
    "AAA7,2026-01-31 23:59:59,Customer Transfer to - Jane Roe,Completed,,500.00,\"57,680.00\"\n"
)
STATEMENT = HEADER + ROWS
RULES = {"Food": ["super mart"], "Transport": ["bus fare"], "Bills": ["power company"]}
RULES_JSON = '{"Food": ["super mart"], "Transport": ["bus fare"], "Bills": ["power company"]}'
REPORT = """Monthly spending
2026-01
  Food: 1700.00
  Transport: 120.00
  Uncategorized: 500.00
  Total spent: 2320.00
  Received: 50000.00
2026-02
  Bills: 2000.00
  Total spent: 2000.00
  Received: 0.00

Top spenders (3)
1. Power Company: 2000.00
2. Super Mart: 1700.00
3. Jane Roe: 500.00
"""


class ParseTests(unittest.TestCase):
    def test_only_completed_rows_are_kept_and_the_fields_are_read(self):
        txns = parse_statement(STATEMENT)
        self.assertEqual([t.receipt for t in txns], ["AAA1", "AAA2", "AAA3", "AAA4", "AAA6", "AAA7"])  # AAA5 is Failed
        first = txns[0]
        self.assertEqual(first.when, datetime(2026, 1, 5, 8, 14, 2))
        self.assertEqual((first.paid_in, first.withdrawn, first.balance), (Decimal("0"), Decimal("1350.00"), Decimal("8650.00")))
        self.assertEqual(first.status, "Completed")

    def test_thousands_commas_and_empty_amounts(self):
        txns = parse_statement(STATEMENT)
        income = [t for t in txns if t.receipt == "AAA2"][0]
        self.assertEqual((income.paid_in, income.withdrawn), (Decimal("50000.00"), Decimal("0")))

    def test_a_missing_column_is_a_statement_error_that_names_no_row_text(self):
        bad = "Receipt No.,Completion Time,Details,Transaction Status,Paid in,Withdrawn\n" + ROWS
        with self.assertRaises(StatementError) as cm:
            parse_statement(bad)
        self.assertIn("Balance", str(cm.exception))
        self.assertNotIn("Super Mart", str(cm.exception))

    def test_a_bad_number_names_the_line_and_never_the_row(self):
        bad = HEADER + 'AAA1,2026-01-05 08:14:02,Merchant Payment to 111111 - Super Mart,Completed,,twelve,"8,650.00"\n'
        with self.assertRaises(StatementError) as cm:
            parse_statement(bad)
        self.assertIn("line 2", str(cm.exception))
        self.assertNotIn("Super Mart", str(cm.exception))
        self.assertNotIn("twelve", str(cm.exception))

    def test_a_statement_with_no_completed_row_is_empty_not_an_error(self):
        only_failed = HEADER + "AAA5,2026-01-09 12:00:00,Merchant Payment to 333333 - Failed Shop,Failed,,999.00,\"58,180.00\"\n"
        self.assertEqual(parse_statement(only_failed), [])


class CategorizeTests(unittest.TestCase):
    def txn(self, details):
        return parse_statement(HEADER + f'X1,2026-01-05 08:14:02,{details},Completed,,10.00,"1.00"\n')[0]

    def test_keywords_match_ignoring_case_and_the_first_category_in_order_wins(self):
        rules = {"Shops": ["mart"], "Food": ["super mart"]}  # both match; Shops comes first
        self.assertEqual(categorize(self.txn("Merchant Payment to 1 - SUPER MART"), rules), "Shops")
        self.assertEqual(categorize(self.txn("Merchant Payment to 1 - Super Mart"), {"Food": ["super mart"]}), "Food")

    def test_a_row_that_matches_nothing_is_uncategorized(self):
        self.assertEqual(categorize(self.txn("Customer Transfer to - Jane Roe"), RULES), "Uncategorized")

    def test_the_counterparty_is_the_text_after_the_last_dash(self):
        self.assertEqual(counterparty(self.txn("Merchant Payment to 111111 - Super Mart")), "Super Mart")
        self.assertEqual(counterparty(self.txn("Airtime Purchase")), "Airtime Purchase")


class TotalsTests(unittest.TestCase):
    def test_monthly_totals_sum_withdrawals_per_category_and_receipts_apart(self):
        totals = monthly_totals(parse_statement(STATEMENT), RULES)
        self.assertEqual(sorted(totals), ["2026-01", "2026-02"])
        jan = totals["2026-01"]
        self.assertEqual(jan["spent"], {"Food": Decimal("1700.00"), "Transport": Decimal("120.00"), "Uncategorized": Decimal("500.00")})
        self.assertEqual((jan["total_spent"], jan["received"]), (Decimal("2320.00"), Decimal("50000.00")))

    def test_the_month_boundary_is_the_completion_time(self):
        totals = monthly_totals(parse_statement(STATEMENT), RULES)
        self.assertEqual(totals["2026-02"]["spent"], {"Bills": Decimal("2000.00")})  # 2026-02-01 00:00:00
        self.assertEqual(totals["2026-02"]["received"], Decimal("0"))
        self.assertIn("Uncategorized", totals["2026-01"]["spent"])  # 2026-01-31 23:59:59 is still January

    def test_top_spenders_rank_by_total_then_name_and_stop_at_n(self):
        txns = parse_statement(STATEMENT)
        self.assertEqual(top_spenders(txns, 3), [("Power Company", Decimal("2000.00")), ("Super Mart", Decimal("1700.00")),
                                                 ("Jane Roe", Decimal("500.00"))])
        self.assertEqual(len(top_spenders(txns, 2)), 2)
        self.assertNotIn("Employer Ltd", [name for name, _ in top_spenders(txns, 10)])  # money received is not spending

    def test_equal_totals_are_ordered_by_name(self):
        tied = HEADER + ('B1,2026-03-01 10:00:00,Pay - Zed Shop,Completed,,10.00,"1.00"\n'
                         'B2,2026-03-02 10:00:00,Pay - Alpha Shop,Completed,,10.00,"1.00"\n')
        self.assertEqual([n for n, _ in top_spenders(parse_statement(tied), 5)], ["Alpha Shop", "Zed Shop"])


class CommandTests(unittest.TestCase):
    def run_cli(self, statement_text, rules_text=RULES_JSON, *extra):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "s.csv").write_text(statement_text, encoding="utf-8")
            (Path(d) / "c.json").write_text(rules_text, encoding="utf-8")
            p = subprocess.run([sys.executable, "-m", "mpesa_analyzer", str(Path(d) / "s.csv"), "--categories", str(Path(d) / "c.json"), *extra],
                               cwd=ROOT, capture_output=True, text=True, timeout=60)
            return p.returncode, p.stdout, p.stderr, sorted(x.name for x in Path(d).iterdir())

    def test_the_report_is_exactly_as_the_spec_says_and_nothing_is_written(self):
        rc, out, err, files = self.run_cli(STATEMENT, RULES_JSON, "--top", "3")
        self.assertEqual((rc, out, err), (0, REPORT, ""))
        self.assertEqual(files, ["c.json", "s.csv"])  # the tool wrote no file next to its input

    def test_a_statement_with_no_completed_row_prints_the_fixed_line(self):
        rc, out, _, _ = self.run_cli(HEADER)
        self.assertEqual((rc, out), (0, "No completed transactions.\n"))

    def test_a_bad_file_is_one_error_line_and_exit_2_with_no_traceback(self):
        rc, out, err, _ = self.run_cli("not,a,statement\n1,2,3\n")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("error: ") and err.count("\n") == 1 and "Traceback" not in err, err)


class RulesOfTheRepoTests(unittest.TestCase):
    def test_no_module_of_the_package_opens_a_connection(self):
        banned = {"socket", "urllib", "http", "requests", "ssl", "ftplib", "smtplib", "telnetlib", "xmlrpc"}
        pkg = ROOT / "mpesa_analyzer"
        self.assertTrue(pkg.is_dir())
        for path in pkg.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = [a.name.split(".")[0] for a in node.names] if isinstance(node, ast.Import) else \
                        [(node.module or "").split(".")[0]] if isinstance(node, ast.ImportFrom) else []
                self.assertFalse(banned & set(names), f"{path.name} imports {banned & set(names)}")

    def test_a_real_statement_cannot_be_committed(self):
        self.assertIn("*.csv", (ROOT / ".gitignore").read_text(encoding="utf-8").split("\n"))


if __name__ == "__main__":
    unittest.main()
