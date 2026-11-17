SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT transaction_id) AS unique_transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS unique_products,
    SUM(quantity_ordered) AS total_quantity,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(total_profit_loss), 2) AS total_profit
FROM public.vw_transaction_analytics;