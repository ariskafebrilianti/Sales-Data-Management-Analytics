
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

st.set_page_config(
    page_title="Transaction History",
    layout="wide",
)


# ==================================================
# 2. DATABASE CONNECTION
# ==================================================

@st.cache_resource
def get_engine():

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

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "postgres"),
        query={"sslmode": "require"},
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )


# ==================================================
# 3. PAGE HEADER
# ==================================================

st.title("Transaction History")

st.caption(
    "View, search, and filter transactions "
    "stored in the sales database."
)

st.divider()


# ==================================================
# 4. FILTERS AND SEARCH
# ==================================================

st.subheader("Search and Filters")

filter_col1, filter_col2, filter_col3 = st.columns(
    [1, 1, 2]
)

with filter_col1:
    status_filter = st.selectbox(
        "Transaction Status",
        options=["All", "Profit", "Loss"],
        key="history_status_filter",
    )

with filter_col2:
    deal_size_filter = st.selectbox(
        "Deal Size",
        options=["All", "Small", "Medium", "Large"],
        key="history_deal_size_filter",
    )

with filter_col3:
    search_text = st.text_input(
        "Search Transaction",
        placeholder="Transaction code, customer, or product code",
        type="search",
        key="history_search",
    )


# ==================================================
# 5. PREPARE FILTER PARAMETERS
# ==================================================

filter_params = {
    "status_filter": status_filter,
    "deal_size_filter": deal_size_filter,
    "search_text": search_text.strip(),
    "search_pattern": f"%{search_text.strip()}%",
}


# ==================================================
# 6. COUNT MATCHING TRANSACTIONS
# ==================================================

count_sql = text("""
    SELECT COUNT(*)

    FROM public.transactions t

    INNER JOIN public.customers c
        ON c.customer_id = t.customer_id

    INNER JOIN public.products p
        ON p.product_id = t.product_id

    WHERE
        (:status_filter = 'All'
         OR t.status = :status_filter)

        AND
        (:deal_size_filter = 'All'
         OR t.deal_size = :deal_size_filter)

        AND (
            :search_text = ''
            OR t.source_transaction_code ILIKE :search_pattern
            OR c.customer_name ILIKE :search_pattern
            OR p.product_code ILIKE :search_pattern
        );
""")


# ==================================================
# 7. LOAD TRANSACTION HISTORY
# ==================================================

history_sql = text("""
    SELECT
        t.transaction_id AS "Transaction ID",

        t.source_transaction_code AS "Transaction Reference",

        t.order_date AS "Order Date",

        c.customer_name AS "Customer",

        c.city AS "City",

        c.country AS "Country",

        p.product_code AS "Product Code",

        p.product_category AS "Product Category",

        t.quantity_ordered AS "Quantity",

        t.selling_price AS "Selling Price",

        t.sales AS "Sales",

        t.total_profit_loss AS "Profit/Loss",

        t.status AS "Status",

        t.deal_size AS "Deal Size"

    FROM public.transactions t

    INNER JOIN public.customers c
        ON c.customer_id = t.customer_id

    INNER JOIN public.products p
        ON p.product_id = t.product_id

    WHERE
        (:status_filter = 'All'
         OR t.status = :status_filter)

        AND
        (:deal_size_filter = 'All'
         OR t.deal_size = :deal_size_filter)

        AND (
            :search_text = ''
            OR t.source_transaction_code ILIKE :search_pattern
            OR c.customer_name ILIKE :search_pattern
            OR p.product_code ILIKE :search_pattern
        )

    ORDER BY
        t.order_date DESC,
        t.transaction_id DESC

    LIMIT :row_limit;
""")


# ==================================================
# 8. DISPLAY TRANSACTION HISTORY
# ==================================================

try:

    engine = get_engine()

    with engine.connect() as connection:

        total_matching = connection.execute(
            count_sql,
            filter_params,
        ).scalar_one()

        result = connection.execute(
            history_sql,
            {
                **filter_params,
                "row_limit": 100,
            },
        ).mappings().all()

    history_rows = [
        dict(row) for row in result
    ]

    st.divider()

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric(
            "Matching Transactions",
            f"{total_matching:,}",
        )

    with metric_col2:
        st.metric(
            "Displayed Transactions",
            f"{len(history_rows):,}",
        )

    st.caption(
        "Showing up to 100 matching transactions, "
        "ordered by most recent order date."
    )

    if history_rows:

        st.dataframe(
            history_rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No transactions match the selected filters."
        )

except Exception:
    st.error(
        "Unable to load transaction history. "
        "Please check the database connection."
    )


# ==================================================
# 9. DATABASE INFORMATION
# ==================================================

st.divider()

st.caption(
    "Transaction History is a read-only page. "
    "Changes to transaction records must be made "
    "through the authorized database workflow."
)
