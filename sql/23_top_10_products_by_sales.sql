SELECT
    product_code,
    product_category,
    total_transactions,
    unique_customers,
    total_quantity,
    total_sales,
    total_profit_loss,
    profit_margin_pct,
    weighted_avg_selling_price
FROM public.vw_product_performance
ORDER BY total_sales DESC
LIMIT 10;