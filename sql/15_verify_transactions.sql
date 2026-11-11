SELECT
    COUNT(*) AS total_transactions,

    COUNT(DISTINCT source_transaction_code)
        AS unique_transaction_codes,

    COUNT(*) FILTER (
        WHERE customer_id IS NULL
    ) AS null_customer_ids,

    COUNT(*) FILTER (
        WHERE product_id IS NULL
    ) AS null_product_ids,

    COUNT(DISTINCT customer_id)
        AS customers_used,

    COUNT(DISTINCT product_id)
        AS products_used,

    MIN(order_date) AS earliest_order_date,

    MAX(order_date) AS latest_order_date,

    SUM(quantity_ordered) AS total_quantity,

    SUM(sales) AS total_sales,

    SUM(total_profit_loss) AS total_profit_loss

FROM public.transactions;