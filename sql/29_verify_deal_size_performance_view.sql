SELECT
    COUNT(*) AS deal_size_groups,

    COUNT(DISTINCT deal_size) AS unique_deal_sizes,

    SUM(total_transactions) AS total_transactions,

    SUM(total_quantity) AS total_quantity,

    SUM(total_sales) AS total_sales,

    SUM(total_profit_loss) AS total_profit_loss,

    SUM(profit_transactions) AS profit_transactions,

    SUM(loss_transactions) AS loss_transactions,

    ROUND(
        SUM(sales_contribution_pct),
        2
    ) AS total_sales_contribution_pct

FROM public.vw_deal_size_performance;


--Melihat detail dari setiap deal size--
SELECT *
FROM public.vw_deal_size_performance
ORDER BY
    CASE deal_size
        WHEN 'Large' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Small' THEN 3
    END;