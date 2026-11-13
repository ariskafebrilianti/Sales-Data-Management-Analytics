SELECT
    COUNT(*) AS geographic_groups,

    COUNT(DISTINCT country) AS total_countries,

    COUNT(DISTINCT city) AS total_cities,

    SUM(total_transactions) AS total_transactions,

    SUM(total_quantity) AS total_quantity,

    SUM(total_sales) AS total_sales,

    SUM(total_profit_loss) AS total_profit_loss,

    SUM(profit_transactions) AS profit_transactions,

    SUM(loss_transactions) AS loss_transactions,

    COUNT(*) FILTER (
        WHERE total_transactions = 0
    ) AS locations_without_transactions

FROM public.vw_geographic_sales;