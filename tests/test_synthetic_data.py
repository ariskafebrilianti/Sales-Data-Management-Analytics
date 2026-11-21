import csv
import sys
import tempfile
import unittest

from datetime import date
from decimal import Decimal
from pathlib import Path


# ==================================================
# 1. PROJECT IMPORT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.generate_synthetic_data import (
    CSV_COLUMNS,
    DEAL_SIZES,
    MAX_ROWS,
    PRODUCT_CATEGORIES,
    generate_synthetic_transactions,
    money,
    save_transactions,
)


# ==================================================
# 2. TEST DATA CONFIGURATION
# ==================================================

START_DATE = date(2023, 1, 4)
END_DATE = date(2026, 11, 21)

TEST_ROWS = 100
TEST_SEED = 42


# ==================================================
# 3. SYNTHETIC DATA TESTS
# ==================================================

class TestSyntheticData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.transactions = generate_synthetic_transactions(
            rows=TEST_ROWS,
            seed=TEST_SEED,
            start_date=START_DATE,
            end_date=END_DATE,
        )

    def test_transaction_count(self):

        self.assertEqual(
            len(self.transactions),
            TEST_ROWS,
        )

    def test_column_structure(self):

        for row in self.transactions:

            self.assertEqual(
                list(row.keys()),
                CSV_COLUMNS,
            )

    def test_no_missing_values(self):

        for row in self.transactions:

            for column, value in row.items():

                with self.subTest(column=column):

                    self.assertIsNotNone(value)
                    self.assertNotEqual(str(value).strip(), "")

    def test_unique_transaction_references(self):

        references = [
            row["source_transaction_code"]
            for row in self.transactions
        ]

        self.assertEqual(
            len(references),
            len(set(references)),
        )

    def test_customer_reference_consistency(self):

        customers = {}

        for row in self.transactions:

            customer_code = row["customer_code"]

            customer_details = (
                row["customer_name"],
                row["city"],
                row["country"],
            )

            if customer_code in customers:

                self.assertEqual(
                    customers[customer_code],
                    customer_details,
                )

            else:

                customers[customer_code] = customer_details

    def test_product_reference_consistency(self):

        products = {}

        for row in self.transactions:

            product_code = row["product_code"]

            product_details = (
                row["product_category"],
                row["msrp"],
            )

            if product_code in products:

                self.assertEqual(
                    products[product_code],
                    product_details,
                )

            else:

                products[product_code] = product_details

            self.assertIn(
                row["product_category"],
                PRODUCT_CATEGORIES,
            )

    def test_numeric_business_rules(self):

        for row in self.transactions:

            quantity = int(row["quantity_ordered"])

            msrp = Decimal(row["msrp"])
            estimated_cost = Decimal(
                row["estimated_cost_per_unit"]
            )
            selling_price = Decimal(row["selling_price"])

            with self.subTest(
                transaction=row["source_transaction_code"]
            ):

                self.assertGreaterEqual(quantity, 1)
                self.assertLessEqual(quantity, 97)

                self.assertGreater(msrp, Decimal("0"))
                self.assertGreater(
                    selling_price,
                    Decimal("0"),
                )

                self.assertEqual(
                    estimated_cost,
                    money(msrp * Decimal("0.50")),
                )

    def test_financial_calculations(self):

        for row in self.transactions:

            quantity = int(row["quantity_ordered"])

            estimated_cost = Decimal(
                row["estimated_cost_per_unit"]
            )
            selling_price = Decimal(row["selling_price"])

            sales = Decimal(row["sales"])
            profit_per_unit = Decimal(
                row["profit_per_unit"]
            )
            total_profit = Decimal(
                row["total_profit_loss"]
            )

            with self.subTest(
                transaction=row["source_transaction_code"]
            ):

                expected_sales = money(
                    selling_price * quantity
                )

                expected_profit_per_unit = money(
                    selling_price - estimated_cost
                )

                expected_total_profit = money(
                    expected_profit_per_unit * quantity
                )

                self.assertEqual(
                    sales,
                    expected_sales,
                )

                self.assertEqual(
                    profit_per_unit,
                    expected_profit_per_unit,
                )

                self.assertEqual(
                    total_profit,
                    expected_total_profit,
                )

    def test_status_and_deal_size(self):

        for row in self.transactions:

            total_profit = Decimal(
                row["total_profit_loss"]
            )

            expected_status = (
                "Profit"
                if total_profit >= 0
                else "Loss"
            )

            with self.subTest(
                transaction=row["source_transaction_code"]
            ):

                self.assertEqual(
                    row["status"],
                    expected_status,
                )

                self.assertIn(
                    row["deal_size"],
                    DEAL_SIZES,
                )

    def test_order_date_range(self):

        for row in self.transactions:

            order_date = date.fromisoformat(
                row["order_date"]
            )

            with self.subTest(
                transaction=row["source_transaction_code"]
            ):

                self.assertGreaterEqual(
                    order_date,
                    START_DATE,
                )

                self.assertLessEqual(
                    order_date,
                    END_DATE,
                )

    def test_reproducible_generation(self):

        repeated_transactions = (
            generate_synthetic_transactions(
                rows=TEST_ROWS,
                seed=TEST_SEED,
                start_date=START_DATE,
                end_date=END_DATE,
            )
        )

        self.assertEqual(
            self.transactions,
            repeated_transactions,
        )

    def test_csv_export(self):

        sample_transactions = self.transactions[:5]

        with tempfile.TemporaryDirectory() as temp_dir:

            output_file = (
                Path(temp_dir)
                / "synthetic_transactions.csv"
            )

            save_transactions(
                sample_transactions,
                output_file,
            )

            self.assertTrue(output_file.exists())

            with output_file.open(
                mode="r",
                newline="",
                encoding="utf-8-sig",
            ) as file:

                reader = csv.DictReader(file)

                self.assertEqual(
                    reader.fieldnames,
                    CSV_COLUMNS,
                )

                exported_rows = list(reader)

                self.assertEqual(
                    len(exported_rows),
                    5,
                )

    def test_invalid_generator_parameters(self):

        invalid_cases = [
            {
                "rows": 0,
                "seed": TEST_SEED,
                "start_date": START_DATE,
                "end_date": END_DATE,
            },
            {
                "rows": MAX_ROWS + 1,
                "seed": TEST_SEED,
                "start_date": START_DATE,
                "end_date": END_DATE,
            },
            {
                "rows": 1,
                "seed": TEST_SEED,
                "start_date": END_DATE,
                "end_date": START_DATE,
            },
        ]

        for parameters in invalid_cases:

            with self.subTest(parameters=parameters):

                with self.assertRaises(ValueError):

                    generate_synthetic_transactions(
                        **parameters
                    )


if __name__ == "__main__":

    unittest.main()