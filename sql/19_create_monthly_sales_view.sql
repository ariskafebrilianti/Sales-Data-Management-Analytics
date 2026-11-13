CREATE OR REPLACE VIEW public.vw_monthly_sales AS

SELECT
    DATE_TRUNC('month', order_date)::DATE AS month_start,

    COUNT(*) AS total_transactions,

    COUNT(DISTINCT customer_id) AS unique_customers,

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
    ) AS average_sales_per_transaction

FROM public.transactions

GROUP BY DATE_TRUNC('month', order_date)::DATE;