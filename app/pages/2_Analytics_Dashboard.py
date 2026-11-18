
import os
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text



# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)



# ==================================================
# 2. DATABASE CONNECTION
# ==================================================

def get_setting(name, default=None):
    """Read configuration from Streamlit secrets or environment variables."""

    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, AttributeError):
        value = None

    if value is None or value == "":
        value = os.getenv(name, default)

    return value


APP_MODE = get_setting("APP_MODE", "local").lower()


@st.cache_resource
def get_engine():

    if APP_MODE == "public":
        required_vars = [
            "DB_READER_HOST",
            "DB_READER_USER",
            "DB_READER_PASSWORD",
        ]

        db_config = {
            "host": get_setting("DB_READER_HOST"),
            "user": get_setting("DB_READER_USER"),
            "password": get_setting("DB_READER_PASSWORD"),
            "port": get_setting("DB_READER_PORT", "5432"),
        }

    else:
        required_vars = [
            "DB_HOST",
            "DB_USER",
            "DB_PASSWORD",
        ]

        db_config = {
            "host": get_setting("DB_HOST"),
            "user": get_setting("DB_USER"),
            "password": get_setting("DB_PASSWORD"),
            "port": get_setting("DB_PORT", "5432"),
        }

    missing_vars = [
        var for var in required_vars
        if not get_setting(var)
    ]

    if missing_vars:
        raise ValueError(
            f"Missing environment variables: {missing_vars}"
        )

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=int(db_config["port"]),
        database=get_setting("DB_NAME", "postgres"),
        query={"sslmode": "require"},
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )


# ==================================================
# 3. LOAD TRANSACTION ANALYTICS DATA
# ==================================================

@st.cache_data(ttl=300)
def load_dashboard_data():

    engine = get_engine()

    query = """
        SELECT *
        FROM public.vw_transaction_analytics
        ORDER BY order_date, transaction_id;
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(query)
        ).mappings().all()

    return pd.DataFrame(
        [dict(row) for row in result]
    )

# ==================================================
# 4. HELPER FUNCTIONS
# ==================================================

def format_number(value, decimals=2):

    if pd.isna(value):
        return "-"

    return f"{float(value):,.{decimals}f}"


def format_integer(value):

    if pd.isna(value):
        return "-"

    return f"{int(value):,}"


# ==================================================
# 5. DASHBOARD HEADER
# ==================================================

st.title("Sales Analytics Dashboard")

st.caption(
    "End-to-End Sales Data Management & Analytics System"
)

st.write(
    "Monitor sales performance, profitability, "
    "product contribution, customer behavior, "
    "and geographic distribution."
)

refresh_col, info_col = st.columns([1, 3])

with refresh_col:

    if st.button(
        "Refresh Dashboard",
        width="stretch",
    ):

        load_dashboard_data.clear()
        st.rerun()

with info_col:

    st.caption(
        "Dashboard data is cached for up to 5 minutes. "
        "Use Refresh Dashboard to retrieve the latest data."
    )

# ==================================================
# 6. LOAD DATA
# ==================================================

try:

    transaction_df = load_dashboard_data()

    if transaction_df.empty:
        st.warning("No transaction data available.")
        st.stop()

    transaction_df["order_date"] = pd.to_datetime(
        transaction_df["order_date"]
    )

    transaction_df["month_start"] = pd.to_datetime(
        transaction_df["month_start"]
    )

except Exception as error:

    st.error("Unable to load transaction analytics data.")
    st.code(str(error))
    st.stop()


# ==================================================
# 7. GLOBAL DASHBOARD FILTERS
# ==================================================

st.divider()
st.subheader("Dashboard Filters")

# Available date range
min_order_date = transaction_df["order_date"].min().date()
max_order_date = transaction_df["order_date"].max().date()

# Filter options
year_options = sorted(
    transaction_df["order_year"].dropna().unique().tolist(),
    reverse=True,
)

quarter_options = sorted(
    transaction_df["order_quarter"].dropna().unique().tolist()
)

month_options = (
    transaction_df[["order_month", "month_name"]]
    .drop_duplicates()
    .sort_values("order_month")["month_name"]
    .tolist()
)

category_options = sorted(
    transaction_df["product_category"].dropna().unique().tolist()
)

product_options = sorted(
    transaction_df["product_code"].dropna().unique().tolist()
)

customer_options = sorted(
    transaction_df["customer_name"].dropna().unique().tolist()
)

country_options = sorted(
    transaction_df["country"].dropna().unique().tolist()
)

city_options = sorted(
    transaction_df["city"].dropna().unique().tolist()
)

deal_size_options = sorted(
    transaction_df["deal_size"].dropna().unique().tolist()
)

status_options = sorted(
    transaction_df["status"].dropna().unique().tolist()
)


# Reset filter callback
def reset_dashboard_filters():

    st.session_state["filter_year"] = []
    st.session_state["filter_quarter"] = []
    st.session_state["filter_month"] = []
    st.session_state["filter_date_range"] = (
        min_order_date,
        max_order_date,
    )
    st.session_state["filter_category"] = []
    st.session_state["filter_product"] = []
    st.session_state["filter_customer"] = []
    st.session_state["filter_country"] = []
    st.session_state["filter_city"] = []
    st.session_state["filter_deal_size"] = []
    st.session_state["filter_status"] = []


with st.expander("Filter Options", expanded=True):

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        selected_years = st.multiselect(
            "Year",
            options=year_options,
            key="filter_year",
        )

        selected_quarters = st.multiselect(
            "Quarter",
            options=quarter_options,
            format_func=lambda x: f"Q{x}",
            key="filter_quarter",
        )

        selected_months = st.multiselect(
            "Month",
            options=month_options,
            key="filter_month",
        )

        selected_date_range = st.date_input(
            "Date Range",
            value=(min_order_date, max_order_date),
            min_value=min_order_date,
            max_value=max_order_date,
            key="filter_date_range",
        )

    with filter_col2:

        selected_categories = st.multiselect(
            "Product Category",
            options=category_options,
            key="filter_category",
        )

        selected_products = st.multiselect(
            "Product Code",
            options=product_options,
            key="filter_product",
        )

        selected_customers = st.multiselect(
            "Customer",
            options=customer_options,
            key="filter_customer",
        )

    with filter_col3:

        selected_countries = st.multiselect(
            "Country",
            options=country_options,
            key="filter_country",
        )

        selected_cities = st.multiselect(
            "City",
            options=city_options,
            key="filter_city",
        )

        selected_deal_sizes = st.multiselect(
            "Deal Size",
            options=deal_size_options,
            key="filter_deal_size",
        )

        selected_statuses = st.multiselect(
            "Status",
            options=status_options,
            key="filter_status",
        )

    st.button(
        "Reset Filters",
        on_click=reset_dashboard_filters,
        width="stretch",
    )


# ==================================================
# 8. APPLY GLOBAL FILTERS
# ==================================================

filtered_df = transaction_df.copy()

if selected_years:
    filtered_df = filtered_df[
        filtered_df["order_year"].isin(selected_years)
    ]

if selected_quarters:
    filtered_df = filtered_df[
        filtered_df["order_quarter"].isin(selected_quarters)
    ]

if selected_months:
    filtered_df = filtered_df[
        filtered_df["month_name"].isin(selected_months)
    ]

if selected_date_range and len(selected_date_range) == 2:

    start_date, end_date = selected_date_range

    filtered_df = filtered_df[
        filtered_df["order_date"].dt.date.between(
            start_date,
            end_date,
        )
    ]

if selected_categories:
    filtered_df = filtered_df[
        filtered_df["product_category"].isin(selected_categories)
    ]

if selected_products:
    filtered_df = filtered_df[
        filtered_df["product_code"].isin(selected_products)
    ]

if selected_customers:
    filtered_df = filtered_df[
        filtered_df["customer_name"].isin(selected_customers)
    ]

if selected_countries:
    filtered_df = filtered_df[
        filtered_df["country"].isin(selected_countries)
    ]

if selected_cities:
    filtered_df = filtered_df[
        filtered_df["city"].isin(selected_cities)
    ]

if selected_deal_sizes:
    filtered_df = filtered_df[
        filtered_df["deal_size"].isin(selected_deal_sizes)
    ]

if selected_statuses:
    filtered_df = filtered_df[
        filtered_df["status"].isin(selected_statuses)
    ]


# Filter summary
st.caption(
    f"Showing {len(filtered_df):,} of "
    f"{len(transaction_df):,} transactions"
)

if filtered_df.empty:
    st.warning(
        "No transactions match the selected filters. "
        "Please adjust or reset your filters."
    )
    st.stop()


# ==================================================
# 9. EXECUTIVE KPI CARDS
# ==================================================

st.divider()
st.subheader("Executive Overview")

total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["total_profit_loss"].sum()

profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales != 0
    else 0
)

total_transactions = filtered_df["transaction_id"].nunique()
unique_customers = filtered_df["customer_id"].nunique()
unique_products = filtered_df["product_id"].nunique()
total_quantity = filtered_df["quantity_ordered"].sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Total Sales (USD*)",
        f"${total_sales:,.2f}",
    )

with kpi2:
    st.metric(
        "Total Profit/Loss (USD*)",
        f"${total_profit:,.2f}",
    )

with kpi3:
    st.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%",
    )

with kpi4:
    st.metric(
        "Transactions",
        format_integer(total_transactions),
    )

kpi5, kpi6, kpi7 = st.columns(3)

with kpi5:
    st.metric(
        "Unique Customers",
        format_integer(unique_customers),
    )

with kpi6:
    st.metric(
        "Unique Products",
        format_integer(unique_products),
    )

with kpi7:
    st.metric(
        "Total Quantity",
        format_integer(total_quantity),
    )

st.caption(
    f"Filtered Period: "
    f"{filtered_df['order_date'].min().date()} "
    f"to {filtered_df['order_date'].max().date()}"
)

st.caption(
    "*Financial values are displayed using USD ($) formatting "
    "for presentation purposes only. The original dataset "
    "does not explicitly specify its currency. "
    "No currency conversion has been performed."
)

# ==================================================
# 10. MONTHLY SALES TREND
# ==================================================

st.divider()
st.subheader("Monthly Sales Performance")

monthly_summary = (
    filtered_df
    .groupby("month_start", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit_loss=("total_profit_loss", "sum"),
    )
    .sort_values("month_start")
)

monthly_chart = (
    monthly_summary
    .set_index("month_start")
    .asfreq("MS", fill_value=0)
    .reset_index()
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    st.markdown("**Monthly Sales Trend**")

    sales_chart = px.line(
        monthly_chart,
        x="month_start",
        y="total_sales",
        markers=True,
        labels={
            "month_start": "Month",
            "total_sales": "Sales (USD*)",
        },
    )

    sales_chart.update_yaxes(
        tickprefix="$",
        tickformat=",.2f",
    )

    sales_chart.update_traces(
        hovertemplate=(
            "%{x|%B %Y}"
            "<br>Sales: $%{y:,.2f}"
            "<extra></extra>"
        )
    )

    sales_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=40),
    )

    st.plotly_chart(
        sales_chart,
        width="stretch",
        key="monthly_sales_trend_chart",
    )


with chart_col2:

    st.markdown("**Monthly Profit/Loss Trend**")

    profit_chart = px.line(
        monthly_chart,
        x="month_start",
        y="total_profit_loss",
        markers=True,
        labels={
            "month_start": "Month",
            "total_profit_loss": "Profit/Loss (USD*)",
        },
    )

    profit_chart.update_yaxes(
        tickprefix="$",
        tickformat=",.2f",
    )

    profit_chart.update_traces(
        hovertemplate=(
            "%{x|%B %Y}"
            "<br>Profit/Loss: $%{y:,.2f}"
            "<extra></extra>"
        )
    )

    profit_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=40),
    )

    st.plotly_chart(
        profit_chart,
        width="stretch",
        key="monthly_profit_trend_chart",
    )

st.caption(
    "Months without transactions within the selected period "
    "are displayed as zero."
)


# ==================================================
# 11. PRODUCT PERFORMANCE
# ==================================================

st.divider()
st.subheader("Product Performance")

products_df = (
    filtered_df
    .groupby(
        ["product_code", "product_category"],
        as_index=False,
    )
    .agg(
        total_transactions=("transaction_id", "nunique"),
        total_quantity=("quantity_ordered", "sum"),
        total_sales=("sales", "sum"),
        total_profit_loss=("total_profit_loss", "sum"),
    )
    .sort_values("total_sales", ascending=False)
)

product_col1, product_col2 = st.columns([1.2, 1])

with product_col1:

    st.markdown("**Top 10 Products by Sales**")

    top_products = (
        products_df
        .head(10)
        .sort_values("total_sales", ascending=True)
    )

    product_chart = px.bar(
        top_products,
        x="total_sales",
        y="product_code",
        orientation="h",
        labels={
            "product_code": "Product Code",
            "total_sales": "Total Sales (USD*)",
        },
    )

    product_chart.update_xaxes(
        tickprefix="$",
        tickformat=",.2f",
    )

    product_chart.update_traces(
        hovertemplate=(
            "Product Code: %{y}"
            "<br>Total Sales: $%{x:,.2f}"
            "<extra></extra>"
        )
    )

    product_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=40),
    )

    st.plotly_chart(
        product_chart,
        width="stretch",
        key="product_sales_chart",
    )

with product_col2:

    st.markdown("**Product Category Summary**")

    category_summary = (
        filtered_df
        .groupby("product_category", as_index=False)
        .agg(
            total_products=("product_id", "nunique"),
            total_transactions=("transaction_id", "nunique"),
            total_sales=("sales", "sum"),
            total_profit=("total_profit_loss", "sum"),
        )
        .sort_values("total_sales", ascending=False)
    )

    st.dataframe(
        category_summary,
        column_config={
            "product_category": st.column_config.TextColumn(
                "Product Category",
            ),
            "total_products": st.column_config.NumberColumn(
                "Total Products",
                format="%d",
            ),
            "total_transactions": st.column_config.NumberColumn(
                "Total Transactions",
                format="%d",
            ),
            "total_sales": st.column_config.NumberColumn(
                "Total Sales (USD*)",
                format="dollar",
            ),
            "total_profit": st.column_config.NumberColumn(
                "Total Profit (USD*)",
                format="dollar",
            ),
        },
        width="stretch",
        hide_index=True,
    )

with st.expander("View Top 10 Product Details"):

    st.dataframe(
        products_df.head(10),
        column_config={
            "product_code": st.column_config.TextColumn(
                "Product Code",
            ),
            "product_category": st.column_config.TextColumn(
                "Product Category",
            ),
            "total_transactions": st.column_config.NumberColumn(
                "Total Transactions",
                format="%d",
            ),
            "total_quantity": st.column_config.NumberColumn(
                "Total Quantity",
                format="%d",
            ),
            "total_sales": st.column_config.NumberColumn(
                "Total Sales (USD*)",
                format="dollar",
            ),
            "total_profit_loss": st.column_config.NumberColumn(
                "Total Profit/Loss (USD*)",
                format="dollar",
            ),
        },
        width="stretch",
        hide_index=True,
    )


# ==================================================
# 12. CUSTOMER PERFORMANCE
# ==================================================

st.divider()
st.subheader("Customer Performance")

customers_df = (
    filtered_df
    .groupby(
        ["customer_id", "customer_name", "country"],
        as_index=False,
    )
    .agg(
        total_transactions=("transaction_id", "nunique"),
        total_quantity=("quantity_ordered", "sum"),
        total_sales=("sales", "sum"),
        total_profit_loss=("total_profit_loss", "sum"),
    )
    .sort_values("total_sales", ascending=False)
)

customer_col1, customer_col2 = st.columns(2)

with customer_col1:

    st.markdown("**Top 10 Customers by Sales**")

    top_customers = (
        customers_df
        .head(10)
        .sort_values("total_sales", ascending=True)
    )

    customer_chart = px.bar(
        top_customers,
        x="total_sales",
        y="customer_name",
        orientation="h",
        labels={
            "customer_name": "Customer Name",
            "total_sales": "Total Sales (USD*)",
        },
    )

    customer_chart.update_xaxes(
        tickprefix="$",
        tickformat=",.2f",
    )

    customer_chart.update_traces(
        hovertemplate=(
            "Customer: %{y}"
            "<br>Total Sales: $%{x:,.2f}"
            "<extra></extra>"
        )
    )

    customer_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=40),
    )

    st.plotly_chart(
        customer_chart,
        width="stretch",
        key="customer_sales_chart",
    )

with customer_col2:

    st.markdown("**Customer Performance Details**")

    st.dataframe(
        customers_df[
            [
                "customer_name",
                "country",
                "total_transactions",
                "total_sales",
                "total_profit_loss",
            ]
        ].head(10),
        column_config={
            "customer_name": st.column_config.TextColumn(
                "Customer Name",
            ),
            "country": st.column_config.TextColumn(
                "Country",
            ),
            "total_transactions": st.column_config.NumberColumn(
                "Total Transactions",
                format="%d",
            ),
            "total_sales": st.column_config.NumberColumn(
                "Total Sales (USD*)",
                format="dollar",
            ),
            "total_profit_loss": st.column_config.NumberColumn(
                "Total Profit/Loss (USD*)",
                format="dollar",
            ),
        },
        width="stretch",
        hide_index=True,
    )


# ==================================================
# 13. GEOGRAPHIC SALES PERFORMANCE
# ==================================================

st.divider()
st.subheader("Geographic Sales Performance")

geography_df = (
    filtered_df
    .groupby("country", as_index=False)
    .agg(
        total_cities=("city", "nunique"),
        total_customers=("customer_id", "nunique"),
        total_transactions=("transaction_id", "nunique"),
        total_sales=("sales", "sum"),
        total_profit_loss=("total_profit_loss", "sum"),
    )
    .sort_values("total_sales", ascending=False)
)

geo_col1, geo_col2 = st.columns(2)

with geo_col1:

    st.markdown("**Top 10 Countries by Sales**")

    top_countries = (
        geography_df
        .head(10)
        .sort_values("total_sales", ascending=True)
    )

    country_chart = px.bar(
        top_countries,
        x="total_sales",
        y="country",
        orientation="h",
        labels={
            "country": "Country",
            "total_sales": "Total Sales (USD*)",
        },
    )

    country_chart.update_xaxes(
        tickprefix="$",
        tickformat=",.2f",
    )

    country_chart.update_traces(
        hovertemplate=(
            "Country: %{y}"
            "<br>Total Sales: $%{x:,.2f}"
            "<extra></extra>"
        )
    )

    country_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=40),
    )

    st.plotly_chart(
        country_chart,
        width="stretch",
        key="country_sales_chart",
    )

with geo_col2:

    st.markdown("**Geographic Summary**")

    st.dataframe(
        geography_df[
            [
                "country",
                "total_cities",
                "total_customers",
                "total_transactions",
                "total_sales",
            ]
        ],
        column_config={
            "country": st.column_config.TextColumn(
                "Country",
            ),
            "total_cities": st.column_config.NumberColumn(
                "Total Cities",
                format="%d",
            ),
            "total_customers": st.column_config.NumberColumn(
                "Total Customers",
                format="%d",
            ),
            "total_transactions": st.column_config.NumberColumn(
                "Total Transactions",
                format="%d",
            ),
            "total_sales": st.column_config.NumberColumn(
                "Total Sales (USD*)",
                format="dollar",
            ),
        },
        width="stretch",
        hide_index=True,
    )


# ==================================================
# 14. DEAL SIZE PERFORMANCE
# ==================================================

st.divider()
st.subheader("Deal Size Performance")

deal_size_df = (
    filtered_df
    .groupby("deal_size", as_index=False)
    .agg(
        total_transactions=("transaction_id", "nunique"),
        total_sales=("sales", "sum"),
        total_profit_loss=("total_profit_loss", "sum"),
    )
)

deal_size_order = ["Large", "Medium", "Small"]

deal_size_df["deal_size"] = pd.Categorical(
    deal_size_df["deal_size"],
    categories=deal_size_order,
    ordered=True,
)

deal_size_df = deal_size_df.sort_values("deal_size")

deal_size_df["profit_margin_pct"] = (
    deal_size_df["total_profit_loss"]
    .div(deal_size_df["total_sales"].replace(0, pd.NA))
    .mul(100)
    .fillna(0)
)

deal_size_df["sales_contribution_pct"] = (
    deal_size_df["total_sales"]
    .div(total_sales if total_sales != 0 else 1)
    .mul(100)
)

deal_size_col1, deal_size_col2 = st.columns(2)

with deal_size_col1:

    st.markdown("**Sales Contribution by Deal Size**")

    deal_chart = px.bar(
        deal_size_df,
        x="deal_size",
        y="total_sales",
        labels={
            "deal_size": "Deal Size",
            "total_sales": "Total Sales (USD*)",
        },
    )

    deal_chart.update_yaxes(
        tickprefix="$",
        tickformat=",.2f",
    )

    deal_chart.update_traces(
        hovertemplate=(
            "Deal Size: %{x}"
            "<br>Total Sales: $%{y:,.2f}"
            "<extra></extra>"
        )
    )

    deal_chart.update_xaxes(
        tickangle=-45,
        automargin=True,
        tickfont=dict(size=10),
    )

    deal_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=100),
    )

    st.plotly_chart(
        deal_chart,
        width="stretch",
        key="deal_size_sales_chart",
    )

with deal_size_col2:

    st.markdown("**Deal Size Details**")

    st.dataframe(
        deal_size_df[
            [
                "deal_size",
                "total_transactions",
                "total_sales",
                "total_profit_loss",
                "profit_margin_pct",
                "sales_contribution_pct",
            ]
        ],
        column_config={
            "deal_size": st.column_config.TextColumn(
                "Deal Size",
            ),
            "total_transactions": st.column_config.NumberColumn(
                "Total Transactions",
                format="%d",
            ),
            "total_sales": st.column_config.NumberColumn(
                "Total Sales (USD*)",
                format="dollar",
            ),
            "total_profit_loss": st.column_config.NumberColumn(
                "Total Profit/Loss (USD*)",
                format="dollar",
            ),
            "profit_margin_pct": st.column_config.NumberColumn(
                "Profit Margin (%)",
                format="%.2f%%",
            ),
            "sales_contribution_pct": st.column_config.NumberColumn(
                "Sales Contribution (%)",
                format="%.2f%%",
            ),
        },
        width="stretch",
        hide_index=True,
    )


# ==================================================
# 15. FOOTER
# ==================================================

st.divider()

st.caption(
    "Data source: Supabase PostgreSQL Analytical Views. "
    "Dashboard refresh interval: 5 minutes."
)
