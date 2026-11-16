
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
# 3. LOAD ANALYTICAL DATA
# ==================================================

@st.cache_data(ttl=300)
def load_dashboard_data():

    engine = get_engine()

    queries = {
        "kpi": """
            SELECT *
            FROM public.vw_sales_kpis;
        """,

        "monthly": """
            SELECT *
            FROM public.vw_monthly_sales
            ORDER BY month_start;
        """,

        "products": """
            SELECT *
            FROM public.vw_product_performance
            ORDER BY total_sales DESC;
        """,

        "customers": """
            SELECT *
            FROM public.vw_customer_performance
            ORDER BY total_sales DESC;
        """,

        "geography": """
            SELECT
                country,
                COUNT(DISTINCT city) AS total_cities,
                SUM(unique_customers) AS unique_customers,
                SUM(total_transactions) AS total_transactions,
                SUM(total_sales) AS total_sales,
                SUM(total_profit_loss) AS total_profit_loss
            FROM public.vw_geographic_sales
            GROUP BY country
            ORDER BY total_sales DESC;
        """,

        "deal_size": """
            SELECT *
            FROM public.vw_deal_size_performance
            ORDER BY
                CASE deal_size
                    WHEN 'Large' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Small' THEN 3
                END;
        """,
    }

    data = {}

    with engine.connect() as connection:

        for key, query in queries.items():

            result = connection.execute(
                text(query)
            ).mappings().all()

            data[key] = pd.DataFrame(
                [dict(row) for row in result]
            )

    return data


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
        use_container_width=True,
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

    dashboard_data = load_dashboard_data()

    kpi_df = dashboard_data["kpi"]
    monthly_df = dashboard_data["monthly"]
    products_df = dashboard_data["products"]
    customers_df = dashboard_data["customers"]
    geography_df = dashboard_data["geography"]
    deal_size_df = dashboard_data["deal_size"]

    if kpi_df.empty:
        st.warning("No KPI data available.")
        st.stop()

    kpi = kpi_df.iloc[0]

except Exception as error:

    st.error("Unable to load dashboard data.")
    st.code(str(error))
    st.stop()


# ==================================================
# 7. EXECUTIVE KPI CARDS
# ==================================================

st.divider()
st.subheader("Executive Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Total Sales",
        format_number(kpi["total_sales"]),
    )

with kpi2:
    st.metric(
        "Total Profit/Loss",
        format_number(kpi["total_profit_loss"]),
    )

with kpi3:
    st.metric(
        "Profit Margin",
        f'{float(kpi["profit_margin_pct"]):.2f}%',
    )

with kpi4:
    st.metric(
        "Transactions",
        format_integer(kpi["total_transactions"]),
    )


kpi5, kpi6, kpi7 = st.columns(3)

with kpi5:
    st.metric(
        "Unique Customers",
        format_integer(kpi["unique_customers"]),
    )

with kpi6:
    st.metric(
        "Unique Products",
        format_integer(kpi["unique_products"]),
    )

with kpi7:
    st.metric(
        "Total Quantity",
        format_integer(kpi["total_quantity"]),
    )

st.caption(
    f'Period: {kpi["first_order_date"]} '
    f'to {kpi["last_order_date"]}'
)

st.caption(
    "Financial values follow the source dataset's "
    "currency unit, which has not yet been independently confirmed."
)


# ==================================================
# 8. MONTHLY SALES TREND
# ==================================================

st.divider()
st.subheader("Monthly Sales Performance")

if not monthly_df.empty:

    monthly_chart = monthly_df.copy()

    monthly_chart["month_start"] = pd.to_datetime(
        monthly_chart["month_start"]
    )

    monthly_chart = (
        monthly_chart
        .set_index("month_start")
        .asfreq("MS", fill_value=0)
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.markdown("**Monthly Sales Trend**")

        st.line_chart(
            monthly_chart[["total_sales"]]
        )

    with chart_col2:

        st.markdown("**Monthly Profit/Loss Trend**")

        st.line_chart(
            monthly_chart[["total_profit_loss"]]
        )

    st.caption(
        "Months without transactions are displayed as zero. "
        "November 2025 has no transaction records in the source dataset."
    )



# ==================================================
# 9. PRODUCT PERFORMANCE
# ==================================================

st.divider()
st.subheader("Product Performance")

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
        x="product_code",
        y="total_sales",
        labels={
            "product_code": "Product Code",
            "total_sales": "Total Sales"
        }
    )

    product_chart.update_xaxes(
        tickangle=-45,
        automargin=True,
        tickfont=dict(size=10)
    )

    product_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=100)
    )

    st.plotly_chart(
        product_chart,
        use_container_width=True
    )


with product_col2:

    st.markdown("**Product Category Summary**")

    category_summary = (
        products_df
        .groupby("product_category", as_index=False)
        .agg(
            total_products=("product_code", "nunique"),
            total_sales=("total_sales", "sum"),
            total_profit=("total_profit_loss", "sum"),
        )
        .sort_values("total_sales", ascending=False)
    )

    st.dataframe(
        category_summary,
        width="stretch",
        hide_index=True,
    )


with st.expander("View Top 10 Product Details"):

    st.dataframe(
        products_df.head(10),
        width="stretch",
        hide_index=True,
    )


# ==================================================
# 10. CUSTOMER PERFORMANCE
# ==================================================

st.divider()
st.subheader("Customer Performance")

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
        x="customer_name",
        y="total_sales",
        labels={
            "customer_name": "Customer Name",
            "total_sales": "Total Sales",
        },
    )

    customer_chart.update_xaxes(
        tickangle=-45,
        automargin=True,
        tickfont=dict(size=10)
    )

    customer_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=100)
    )

    st.plotly_chart(
        customer_chart,
        use_container_width=True,
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
        width="stretch",
        hide_index=True,
    )


# ==================================================
# 11. GEOGRAPHIC SALES PERFORMANCE
# ==================================================

st.divider()
st.subheader("Geographic Sales Performance")

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
        x="country",
        y="total_sales",
        labels={
            "country": "Country",
            "total_sales": "Total Sales",
        },
    )

    country_chart.update_xaxes(
        tickangle=-45,
        automargin=True,
        tickfont=dict(size=10)
    )

    country_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=100)
    )

    st.plotly_chart(
        country_chart,
        use_container_width=True,
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
        ] if "total_customers" in geography_df.columns
        else geography_df[
            [
                "country",
                "total_cities",
                "unique_customers",
                "total_transactions",
                "total_sales",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


# ==================================================
# 12. DEAL SIZE PERFORMANCE
# ==================================================

st.divider()
st.subheader("Deal Size Performance")

deal_col1, deal_col2 = st.columns(2)

with deal_col1:

    st.markdown("**Sales Contribution by Deal Size**")

    deal_chart = px.bar(
        deal_size_df,
        x="deal_size",
        y="total_sales",
        labels={
            "deal_size": "Deal Size",
            "total_sales": "Total Sales",
        },
    )

    deal_chart.update_xaxes(
        tickangle=-45,
        automargin=True,
        tickfont=dict(size=10)
    )

    deal_chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=100)
    )

    st.plotly_chart(
        deal_chart,
        use_container_width=True,
    )


with deal_col2:

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
        width="stretch",
        hide_index=True,
    )

# ==================================================
# 13. FOOTER
# ==================================================

st.divider()

st.caption(
    "Data source: Supabase PostgreSQL Analytical Views. "
    "Dashboard refresh interval: 5 minutes."
)
