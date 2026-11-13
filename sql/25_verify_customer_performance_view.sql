SELECT
    COUNT(*) AS total_customers,

    SUM(total_transactions) AS total_transactions,

    SUM(total_quantity) AS total_quantity,

    SUM(total_sales) AS total_sales,

    SUM(total_profit_loss) AS total_profit_loss,

    COUNT(*) FILTER (
        WHERE total_transactions = 0
    ) AS customers_without_transactions

FROM public.vw_customer_performance;