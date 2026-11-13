CREATE OR REPLACE VIEW public.vw_deal_size_performance AS

WITH deal_size_summary AS (
    SELECT
        deal_size,

        COUNT(transaction_id) AS total_transactions,
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

        COUNT(*) FILTER (
            WHERE status = 'Profit'
        ) AS profit_transactions,

        COUNT(*) FILTER (
            WHERE status = 'Loss'
        ) AS loss_transactions

    FROM public.transactions

    GROUP BY deal_size
)

SELECT
    deal_size,
    total_transactions,
    unique_customers,
    unique_products,
    total_quantity,
    total_sales,
    total_profit_loss,
    profit_margin_pct,
    average_sales_per_transaction,
    profit_transactions,
    loss_transactions,

    ROUND(
        total_sales * 100.0
        / NULLIF(SUM(total_sales) OVER (), 0),
        2
    ) AS sales_contribution_pct

FROM deal_size_summary;