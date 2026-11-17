
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    "DB_READER_HOST",
    "DB_READER_USER",
    "DB_READER_PASSWORD",
]

missing_vars = [
    var for var in required_vars
    if not os.getenv(var)
]

if missing_vars:
    raise ValueError(f"Missing environment variables: {missing_vars}")

connection_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_READER_USER"),
    password=os.getenv("DB_READER_PASSWORD"),
    host=os.getenv("DB_READER_HOST"),
    port=int(os.getenv("DB_READER_PORT", "5432")),
    database=os.getenv("DB_NAME", "postgres"),
    query={"sslmode": "require"},
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)

try:
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                current_user AS database_user,
                current_database() AS database_name,
                COUNT(*) AS accessible_rows
            FROM public.vw_transaction_analytics
        """)).mappings().one()

        print("Connection successful!")
        print(dict(result))

finally:
    engine.dispose()
