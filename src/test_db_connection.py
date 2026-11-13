
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


# Load environment variables
load_dotenv()


# Check required credentials
required_vars = [
    "DB_HOST",
    "DB_USER",
    "DB_PASSWORD",
]

missing_vars = [
    var for var in required_vars
    if not os.getenv(var)
]

if missing_vars:
    raise ValueError(
        f"Missing environment variables: {missing_vars}"
    )


# Create PostgreSQL connection URL
connection_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "postgres"),
    query={"sslmode": "require"},
)


# Create SQLAlchemy engine
engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)


# Test connection
try:
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    current_database() AS database_name,
                    current_user AS connected_user,
                    NOW() AS connected_at;
            """)
        ).mappings().one()

        print("Database connection successful!")
        print("Database:", result["database_name"])
        print("Connected user:", result["connected_user"])
        print("Connected at:", result["connected_at"])

except Exception as error:
    print("Database connection failed.")
    print("Error:", error)

finally:
    engine.dispose()
