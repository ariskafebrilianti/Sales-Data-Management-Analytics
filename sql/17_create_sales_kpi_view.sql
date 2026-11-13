CREATE OR REPLACE VIEW public.vw_sales_kpis AS

SELECT
    COUNT(*) AS total_transactions,

    COUNT(DISTINCT customer_id) AS unique_customers,

    COUNT(DISTINCT product_id) AS unique_products,

    SUM(quantity_ordered) AS total_quantity,

    SUM(sales) AS total_sales,

    SUM(total_profit_loss) AS total_profit_loss,

    ROUND(
        SUM(total_profit_loss) * 100.0
        / NULLIF(SUM(sales), 0),
        2
    ) AS profit_margin_pct,

    ROUND(
        AVG(sales),
        2
    ) AS average_sales_per_transaction,

    MIN(order_date) AS first_order_date,

    MAX(order_date) AS last_order_date

FROM public.transactions;