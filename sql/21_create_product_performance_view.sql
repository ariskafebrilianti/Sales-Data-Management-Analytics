CREATE OR REPLACE VIEW public.vw_product_performance AS

SELECT
    p.product_id,
    p.product_code,
    p.product_category,
    p.msrp,

    COUNT(t.transaction_id) AS total_transactions,

    COUNT(DISTINCT t.customer_id) AS unique_customers,

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
        / NULLIF(SUM(t.quantity_ordered), 0),
        2
    ) AS weighted_avg_selling_price

FROM public.products p

LEFT JOIN public.transactions t
    ON t.product_id = p.product_id

GROUP BY
    p.product_id,
    p.product_code,
    p.product_category,
    p.msrp;