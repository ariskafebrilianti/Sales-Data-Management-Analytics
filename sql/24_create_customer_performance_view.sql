CREATE OR REPLACE VIEW public.vw_customer_performance AS

SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.country,

    COUNT(t.transaction_id) AS total_transactions,

    COUNT(DISTINCT t.product_id) AS unique_products_purchased,

    COALESCE(
        SUM(t.quantity_ordered), 0
    ) AS total_quantity,

    COALESCE(
        SUM(t.sales), 0
    ) AS total_sales,

    COALESCE(
        SUM(t.total_profit_loss), 0
    ) AS total_profit_loss,

    ROUND(
        SUM(t.total_profit_loss) * 100.0
        / NULLIF(SUM(t.sales), 0),
        2
    ) AS profit_margin_pct,

    ROUND(
        SUM(t.sales)
        / NULLIF(COUNT(t.transaction_id), 0),
        2
    ) AS average_sales_per_transaction,

    MIN(t.order_date) AS first_order_date,

    MAX(t.order_date) AS last_order_date

FROM public.customers c

LEFT JOIN public.transactions t
    ON t.customer_id = c.customer_id

GROUP BY
    c.customer_id,
    c.customer_name,
    c.city,
    c.country;