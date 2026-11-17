-- ==================================================
-- MONITOR RECENT TRANSACTIONS
-- Purpose: Monitor newly inserted transactions
-- ==================================================

SELECT
    t.transaction_id,
    t.source_transaction_code,
    t.created_at,
    t.order_date,
    c.customer_name,
    p.product_code,
    p.product_category,
    t.quantity_ordered,
    t.selling_price,
    t.sales,
    t.total_profit_loss,
    t.status,
    t.deal_size
FROM public.transactions AS t
JOIN public.customers AS c
    ON t.customer_id = c.customer_id
JOIN public.products AS p
    ON t.product_id = p.product_id
WHERE t.created_at IS NOT NULL
ORDER BY t.created_at DESC
LIMIT 50;