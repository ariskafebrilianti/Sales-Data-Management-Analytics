CREATE OR REPLACE VIEW public.vw_geographic_sales AS

SELECT
    c.country,
    c.city,

    COUNT(t.transaction_id) AS total_transactions,

    COUNT(DISTINCT c.customer_id) AS unique_customers,

    COUNT(DISTINCT t.product_id) AS unique_products,

    SUM(t.quantity_ordered) AS total_quantity,

    SUM(t.sales) AS total_sales,

    SUM(t.total_profit_loss) AS total_profit_loss,

    ROUND(
        SUM(t.total_profit_loss) * 100.0
        / NULLIF(SUM(t.sales), 0),
        2
    ) AS profit_margin_pct,

    COUNT(*) FILTER (
        WHERE t.status = 'Profit'
    ) AS profit_transactions,

    COUNT(*) FILTER (
        WHERE t.status = 'Loss'
    ) AS loss_transactions,

    ROUND(
        AVG(t.sales),
        2
    ) AS average_sales_per_transaction

FROM public.customers c

INNER JOIN public.transactions t
    ON t.customer_id = c.customer_id

GROUP BY
    c.country,
    c.city;