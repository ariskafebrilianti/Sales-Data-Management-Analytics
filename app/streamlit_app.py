
import os
import uuid
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError


# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

st.set_page_config(
    page_title="Sales Transaction Management",
    page_icon="",
    layout="wide",
)

CENT = Decimal("0.01")


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
# 3. LOAD CUSTOMER AND PRODUCT DATA
# ==================================================

@st.cache_data(ttl=300)
def get_customers():
    with get_engine().connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    customer_id,
                    customer_name,
                    city,
                    country
                FROM public.customers
                ORDER BY customer_name, city, country;
            """)
        )

        return [dict(row) for row in result.mappings().all()]


@st.cache_data(ttl=300)
def get_products():
    with get_engine().connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    product_id,
                    product_code,
                    product_category,
                    msrp
                FROM public.products
                ORDER BY product_code;
            """)
        )

        return [dict(row) for row in result.mappings().all()]


# ==================================================
# 4. HELPER FUNCTIONS
# ==================================================

def money(value):
    return Decimal(str(value)).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def format_amount(value):
    return f"{money(value):,.2f}"


def generate_transaction_code():
    return f"MANUAL-{uuid.uuid4().hex.upper()}"


# ==================================================
# 5. APPLICATION HEADER
# ==================================================

st.title("Sales Transaction Management")

st.caption(
    "Enter and manage new sales transactions "
    "using the PostgreSQL database."
)

st.divider()


# ==================================================
# 6. CHECK DATABASE AND LOAD DATA
# ==================================================

try:
    engine = get_engine()
    customers = get_customers()
    products = get_products()

except Exception as error:
    st.error("Unable to connect to the database.")
    st.code(str(error))
    st.stop()


if not customers:
    st.warning("No customer records found in the database.")
    st.stop()

if not products:
    st.warning("No product records found in the database.")
    st.stop()

# Reset input fields after successful transaction
if st.session_state.pop("_reset_transaction_form", False):
    for key in [
        "product_label",
        "order_date",
        "customer_label",
        "quantity",
        "selling_price",
        "deal_size",
        "confirm_save",
    ]:
        st.session_state.pop(key, None)
# ==================================================
# 7. GENERATE TRANSACTION REFERENCE
# ==================================================

if "transaction_code" not in st.session_state:
    st.session_state.transaction_code = (
        generate_transaction_code()
    )

if "flash_message" in st.session_state:
    st.success(st.session_state.pop("flash_message"))

st.subheader("Transaction Information")

st.text_input(
    "Transaction Reference",
    value=st.session_state.transaction_code,
    disabled=True,
)

st.caption(
    "A unique transaction reference is generated automatically."
)


# ==================================================
# 8. SELECT PRODUCT
# ==================================================

st.subheader("Product Selection")

product_options = {
    f"{product['product_code']} | "
    f"{product['product_category']}": product
    for product in products
}

selected_product_label = st.selectbox(
    "Select Product",
    options=list(product_options.keys()),
    key="product_label",
)

selected_product = product_options[selected_product_label]

product_msrp = money(selected_product["msrp"])

estimated_cost = money(
    product_msrp * Decimal("0.50")
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Product MSRP",
        format_amount(product_msrp),
    )

with col2:
    st.metric(
        "Estimated Cost per Unit (50% MSRP)",
        format_amount(estimated_cost),
    )

st.caption(
    "Estimated cost is based on the dataset's "
    "50% MSRP assumption, not actual procurement cost."
)



# ==================================================
# 9. TRANSACTION INPUT
# ==================================================

st.divider()
st.subheader("Transaction Details")

customer_options = {
    (
        f"{customer['customer_name']} | "
        f"{customer['city']}, {customer['country']} "
        f"(ID: {customer['customer_id']})"
    ): customer
    for customer in customers
}

col1, col2 = st.columns(2)

with col1:
    order_date = st.date_input(
        "Order Date",
        value=date.today(),
        key="order_date",
    )

    customer_label = st.selectbox(
        "Select Customer",
        options=list(customer_options.keys()),
        key="customer_label",
    )

    quantity = st.number_input(
        "Quantity Ordered",
        min_value=1,
        value=1,
        step=1,
        key="quantity",
    )

with col2:
    selling_price_input = st.number_input(
        "Selling Price per Unit",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.2f",
        key="selling_price",
    )

    deal_size = st.selectbox(
        "Deal Size",
        options=["", "Small", "Medium", "Large"],
        format_func=lambda value: (
            "Select Deal Size" if value == "" else value
        ),
        key="deal_size",
    )


# ==================================================
# 10. LIVE CALCULATION PREVIEW
# ==================================================

quantity = int(quantity)
selling_price = money(selling_price_input)

sales_preview = money(
    selling_price * quantity
)

profit_per_unit_preview = money(
    selling_price - estimated_cost
)

total_profit_preview = money(
    profit_per_unit_preview * quantity
)

status_preview = (
    "Profit"
    if total_profit_preview >= 0
    else "Loss"
)

st.divider()
st.subheader("Transaction Calculation Preview")

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric(
        "Estimated Sales",
        format_amount(sales_preview),
    )

with metric2:
    st.metric(
        "Estimated Profit/Loss",
        format_amount(total_profit_preview),
    )

with metric3:
    st.metric(
        "Transaction Status",
        status_preview,
    )

st.write("**Calculation Details**")

st.write(
    f"- Quantity: {quantity}\n"
    f"- Selling Price per Unit: {format_amount(selling_price)}\n"
    f"- Estimated Cost per Unit: {format_amount(estimated_cost)}\n"
    f"- Profit per Unit: {format_amount(profit_per_unit_preview)}\n"
    f"- Total Sales: {format_amount(sales_preview)}\n"
    f"- Total Profit/Loss: {format_amount(total_profit_preview)}"
)

st.caption(
    "Profit calculation uses the estimated cost assumption "
    "of 50% MSRP. It does not represent verified actual cost."
)


# ==================================================
# 11. CONFIRMATION AND DATABASE INSERT
# ==================================================

st.divider()
st.subheader("Confirm Transaction")

confirmed = st.checkbox(
    "I have reviewed the transaction details "
    "and confirm that they are correct.",
    key="confirm_save",
)

save_clicked = st.button(
    "Save Transaction",
    type="primary",
    use_container_width=True,
)

if save_clicked:

    if not confirmed:
        st.warning(
            "Please confirm the transaction details before saving."
        )

    elif not deal_size:
        st.error("Please select a deal size.")

    elif selling_price <= 0:
        st.error("Selling price must be greater than zero.")

    else:
        selected_customer = customer_options[customer_label]

        transaction_code = st.session_state.transaction_code

        insert_sql = text("""
            INSERT INTO public.transactions (
                source_transaction_code,
                customer_id,
                product_id,
                order_date,
                quantity_ordered,
                estimated_cost_per_unit,
                selling_price,
                sales,
                profit_per_unit,
                total_profit_loss,
                status,
                deal_size
            )
            VALUES (
                :source_transaction_code,
                :customer_id,
                :product_id,
                :order_date,
                :quantity_ordered,
                :estimated_cost_per_unit,
                :selling_price,
                :sales,
                :profit_per_unit,
                :total_profit_loss,
                :status,
                :deal_size
            )
            RETURNING transaction_id;
        """)

        parameters = {
            "source_transaction_code": transaction_code,
            "customer_id": selected_customer["customer_id"],
            "product_id": selected_product["product_id"],
            "order_date": order_date,
            "quantity_ordered": quantity,
            "estimated_cost_per_unit": estimated_cost,
            "selling_price": selling_price,
            "sales": sales_preview,
            "profit_per_unit": profit_per_unit_preview,
            "total_profit_loss": total_profit_preview,
            "status": status_preview,
            "deal_size": deal_size,
        }

        try:
            with engine.begin() as connection:
                transaction_id = connection.execute(
                    insert_sql,
                    parameters,
                ).scalar_one()

            st.session_state.flash_message = (
                f"Transaction saved successfully. "
                f"Transaction ID: {transaction_id}"
            )

            st.session_state.transaction_code = (
                generate_transaction_code()
            )

            st.session_state["_reset_transaction_form"] = True

            st.rerun()

        except SQLAlchemyError as error:
            st.error(
                "Transaction could not be saved. "
                "The database rejected the operation."
            )

            st.code(str(error))

# ==================================================
# 12. DATABASE INFORMATION
# ==================================================

st.divider()

st.caption(
    "Data is stored directly in the Supabase PostgreSQL database. "
    "Database constraints provide the final validation layer."
)
