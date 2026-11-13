SELECT *
FROM public.vw_monthly_sales
ORDER BY month_start;

SELECT
    COUNT(*) AS total_months,
    SUM(total_transactions) AS total_transactions,
    SUM(total_quantity) AS total_quantity,
    SUM(total_sales) AS total_sales,
    SUM(total_profit_loss) AS total_profit_loss
FROM public.vw_monthly_sales;