from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from faker import Faker


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "synthetic_transactions.csv"
)

CENT = Decimal("0.01")

MAX_ROWS = 10_000


# ==================================================
# 2. BUSINESS REFERENCE DATA
# ==================================================

PRODUCT_CATEGORIES = {
    "Classic Cars": "CC",
    "Vintage Cars": "VC",
    "Motorcycles": "MC",
    "Planes": "PL",
    "Ships": "SH",
    "Trains": "TR",
    "Trucks and Buses": "TB",
}

CUSTOMER_LOCALES = [
    ("United States", "en_US"),
    ("France", "fr_FR"),
    ("Germany", "de_DE"),
    ("United Kingdom", "en_GB"),
    ("Spain", "es_ES"),
    ("Japan", "ja_JP"),
    ("Italy", "it_IT"),
    ("Australia", "en_AU"),
    ("Canada", "en_CA"),
    ("Netherlands", "nl_NL"),
]

DEAL_SIZES = ["Small", "Medium", "Large"]


CSV_COLUMNS = [
    "source_transaction_code",
    "customer_code",
    "customer_name",
    "city",
    "country",
    "product_code",
    "product_category",
    "quantity_ordered",
    "msrp",
    "estimated_cost_per_unit",
    "selling_price",
    "sales",
    "profit_per_unit",
    "total_profit_loss",
    "status",
    "deal_size",
    "order_date",
]


# ==================================================
# 3. FINANCIAL CALCULATIONS
# ==================================================

def money(value: Decimal) -> Decimal:
    """Round financial values to two decimal places."""

    return value.quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


# ==================================================
# 4. CUSTOMER GENERATION
# ==================================================

def generate_customers(
    count: int,
    rng: random.Random,
    seed: int,
) -> list[dict[str, str]]:

    fake_generators = {}

    for index, (_, locale) in enumerate(CUSTOMER_LOCALES):
        fake = Faker(locale)
        fake.seed_instance(seed + index)

        fake_generators[locale] = fake

    customers = []

    for index in range(1, count + 1):

        country, locale = rng.choice(CUSTOMER_LOCALES)

        fake = fake_generators[locale]

        customers.append({
            "customer_code": f"SYN-CUST-{index:04d}",
            "customer_name": fake.unique.company(),
            "city": fake.city(),
            "country": country,
        })

    return customers


# ==================================================
# 5. PRODUCT GENERATION
# ==================================================

def generate_products(
    rng: random.Random,
) -> list[dict[str, str]]:

    products = []

    for category, prefix in PRODUCT_CATEGORIES.items():

        for index in range(1, 4):

            msrp = Decimal(
                rng.randint(3000, 25000)
            ) / Decimal("100")

            products.append({
                "product_code": (
                    f"SYN-{prefix}-{index:03d}"
                ),
                "product_category": category,
                "msrp": f"{money(msrp):.2f}",
            })

    return products


# ==================================================
# 6. TRANSACTION GENERATION
# ==================================================

def generate_synthetic_transactions(
    rows: int,
    seed: int,
    start_date: date,
    end_date: date,
) -> list[dict[str, str]]:

    if rows < 1 or rows > MAX_ROWS:
        raise ValueError(
            f"Rows must be between 1 and {MAX_ROWS}."
        )

    if start_date > end_date:
        raise ValueError(
            "Start date cannot be later than end date."
        )

    rng = random.Random(seed)

    customer_count = min(
        rows,
        max(5, min(25, rows // 4)),
    )

    customers = generate_customers(
        count=customer_count,
        rng=rng,
        seed=seed,
    )

    products = generate_products(rng)

    date_range = (end_date - start_date).days

    transactions = []

    for index in range(1, rows + 1):

        customer = rng.choice(customers)
        product = rng.choice(products)

        quantity = rng.randint(1, 97)

        msrp = Decimal(product["msrp"])

        estimated_cost = money(
            msrp * Decimal("0.50")
        )

        selling_multiplier = (
            Decimal(rng.randint(30, 120))
            / Decimal("100")
        )

        selling_price = money(
            msrp * selling_multiplier
        )

        sales = money(
            selling_price * quantity
        )

        profit_per_unit = money(
            selling_price - estimated_cost
        )

        total_profit = money(
            profit_per_unit * quantity
        )

        status = (
            "Profit"
            if total_profit >= 0
            else "Loss"
        )

        order_date = (
            start_date
            + timedelta(days=rng.randint(0, date_range))
        )

        transactions.append({

            "source_transaction_code": (
                f"SYN-{index:06d}"
            ),

            "customer_code": customer["customer_code"],
            "customer_name": customer["customer_name"],
            "city": customer["city"],
            "country": customer["country"],

            "product_code": product["product_code"],
            "product_category": product["product_category"],

            "quantity_ordered": str(quantity),

            "msrp": f"{msrp:.2f}",
            "estimated_cost_per_unit": (
                f"{estimated_cost:.2f}"
            ),

            "selling_price": f"{selling_price:.2f}",
            "sales": f"{sales:.2f}",
            "profit_per_unit": f"{profit_per_unit:.2f}",
            "total_profit_loss": f"{total_profit:.2f}",

            "status": status,
            "deal_size": rng.choice(DEAL_SIZES),

            "order_date": order_date.isoformat(),
        })

    return transactions


# ==================================================
# 7. CSV EXPORT
# ==================================================

def save_transactions(
    transactions: list[dict[str, str]],
    output_file: Path,
) -> None:

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        mode="w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=CSV_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(transactions)


# ==================================================
# 8. COMMAND LINE INTERFACE
# ==================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description="Generate synthetic sales transactions."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=100,
        help="Number of synthetic transactions.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible results.",
    )

    parser.add_argument(
        "--start-date",
        default="2023-01-04",
        help="Start date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--end-date",
        default=date.today().isoformat(),
        help="End date in YYYY-MM-DD format.",
    )

    args = parser.parse_args()

    try:

        start_date = date.fromisoformat(args.start_date)
        end_date = date.fromisoformat(args.end_date)

        transactions = generate_synthetic_transactions(
            rows=args.rows,
            seed=args.seed,
            start_date=start_date,
            end_date=end_date,
        )

        save_transactions(
            transactions=transactions,
            output_file=OUTPUT_FILE,
        )

    except (ValueError, OSError) as error:

        parser.error(str(error))

    print("Synthetic data generated successfully.")
    print(f"Total transactions: {len(transactions)}")
    print(f"Random seed: {args.seed}")
    print(f"Output file: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()