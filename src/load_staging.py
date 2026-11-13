
import hashlib
import os
import uuid
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"
DATA_FILE = ROOT_DIR / "data" / "raw" / "Sales_dataset.csv"

load_dotenv(dotenv_path=ENV_FILE)

required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(
        f"Missing environment variables: {missing_vars}. "
        "Check the .env file in your project root."
    )

if not DATA_FILE.exists():
    raise FileNotFoundError(f"CSV file not found: {DATA_FILE}")


# --------------------------------------------------
# 2. EXPECTED SOURCE COLUMNS
# --------------------------------------------------

column_mapping = {
    "CUSTOMER_CODE": "customer_code",
    "CUSTOMER_NAME": "customer_name",
    "QUANTITY_ORDERED": "quantity_ordered",
    "MSRP": "msrp",
    "Estimated Cost Price (50%)": "estimated_cost_price_50_pct",
    "Selling price": "selling_price",
    "SALES": "sales",
    "Profit per unit": "profit_per_unit",
    "Total profit / loss": "total_profit_loss",
    "Status": "status",
    "ORDER_DATE": "order_date",
    "MONTH": "month",
    "YEAR": "year",
    "PRODUCT": "product",
    "PRODUCT_CODE": "product_code",
    "CITY": "city",
    "COUNTRY": "country",
    "DEALSIZE": "deal_size",
}

expected_columns = list(column_mapping.values())


# --------------------------------------------------
# 3. READ RAW CSV WITHOUT TRANSFORMING VALUES
# --------------------------------------------------

df = pd.read_csv(
    DATA_FILE,
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
)

# Normalize column headers
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

# Remove completely empty unnamed columns
empty_unnamed_columns = [
    column
    for column in df.columns
    if column.startswith("Unnamed:")
    and df[column].astype(str).str.strip().eq("").all()
]

df = df.drop(columns=empty_unnamed_columns)

# Rename source columns to database column names
df = df.rename(columns=column_mapping)

# Validate column structure
missing_columns = [
    column for column in expected_columns
    if column not in df.columns
]

unexpected_columns = [
    column for column in df.columns
    if column not in expected_columns
]

if missing_columns or unexpected_columns:
    raise ValueError(
        f"CSV column mismatch.\n"
        f"Missing columns: {missing_columns}\n"
        f"Unexpected columns: {unexpected_columns}"
    )

# Keep the exact expected column order
df = df[expected_columns].copy()

# Validate expected dataset size
if len(df) != 2824:
    raise ValueError(
        f"Expected 2824 rows, but found {len(df)}. "
        "Check the source CSV before importing."
    )

# Confirm the source summary row is present
summary_count = (
    df["customer_code"]
    .str.strip()
    .str.lower()
    .eq("total")
    .sum()
)

if summary_count != 1:
    raise ValueError(
        f"Expected 1 summary row, but found {summary_count}."
    )

# Add original CSV row numbers, starting from 1
df.insert(0, "source_row_number", range(1, len(df) + 1))


# --------------------------------------------------
# 4. GENERATE A REPEATABLE IMPORT BATCH ID
# --------------------------------------------------

file_hash = hashlib.sha256(DATA_FILE.read_bytes()).hexdigest()

# Identical CSV content produces the same batch ID.
# This prevents accidental duplicate imports.
batch_id = uuid.uuid5(
    uuid.NAMESPACE_URL,
    f"sales-dataset:{file_hash}",
)

print("CSV validation successful.")
print(f"Rows to import: {len(df)}")
print(f"Summary rows: {summary_count}")
print(f"Import batch ID: {batch_id}")


# --------------------------------------------------
# 5. DATABASE CONNECTION
# --------------------------------------------------

connection_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "postgres"),
    query={"sslmode": "require"},
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)


# --------------------------------------------------
# 6. PREPARE INSERT QUERY
# --------------------------------------------------

insert_sql = text("""
    INSERT INTO raw_sales_staging (
        import_batch_id,
        source_row_number,
        customer_code,
        customer_name,
        quantity_ordered,
        msrp,
        estimated_cost_price_50_pct,
        selling_price,
        sales,
        profit_per_unit,
        total_profit_loss,
        status,
        order_date,
        month,
        year,
        product,
        product_code,
        city,
        country,
        deal_size
    )
    VALUES (
        :import_batch_id,
        :source_row_number,
        :customer_code,
        :customer_name,
        :quantity_ordered,
        :msrp,
        :estimated_cost_price_50_pct,
        :selling_price,
        :sales,
        :profit_per_unit,
        :total_profit_loss,
        :status,
        :order_date,
        :month,
        :year,
        :product,
        :product_code,
        :city,
        :country,
        :deal_size
    );
""")


# --------------------------------------------------
# 7. IMPORT DATA IN ONE DATABASE TRANSACTION
# --------------------------------------------------
print("DataFrame columns:")
print(df.columns.tolist())

print("\nSales column exists:", "sales" in df.columns)

records = df.to_dict(orient="records")

for record in records:
    record["import_batch_id"] = batch_id

try:
    with engine.begin() as connection:

        # Prevent importing identical file content twice
        existing_batch = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM raw_sales_staging
                WHERE import_batch_id = :batch_id
            """),
            {"batch_id": batch_id},
        ).scalar_one()

        if existing_batch > 0:
            print(
                "This exact CSV file has already been imported. "
                f"Existing rows in batch: {existing_batch}"
            )
        else:
            connection.execute(insert_sql, records)

            imported_count = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM raw_sales_staging
                    WHERE import_batch_id = :batch_id
                """),
                {"batch_id": batch_id},
            ).scalar_one()

            if imported_count != len(df):
                raise RuntimeError(
                    f"Row count mismatch. "
                    f"Expected {len(df)}, got {imported_count}."
                )

            print("\nImport successful!")
            print(f"Imported rows: {imported_count}")
            print(f"Batch ID: {batch_id}")

except Exception as error:
    print("\nImport failed. Database transaction was rolled back.")
    raise error

finally:
    engine.dispose()
