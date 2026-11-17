
-- ==================================================
-- CREATE TRANSACTION ANALYTICS VIEW
-- Purpose: Provide transaction-level data for
-- interactive dashboard filtering
-- ==================================================

CREATE OR REPLACE VIEW public.vw_transaction_analytics AS
SELECT
    t.transaction_id,
    t.source_transaction_code,
    t.created_at,
    t.order_date,

    EXTRACT(YEAR FROM t.order_date)::INTEGER
        AS order_year,

    EXTRACT(QUARTER FROM t.order_date)::INTEGER
        AS order_quarter,

    EXTRACT(MONTH FROM t.order_date)::INTEGER
        AS order_month,

    TO_CHAR(t.order_date, 'FMMonth')
        AS month_name,

    DATE_TRUNC('month', t.order_date)::DATE
        AS month_start,

    t.customer_id,
    c.customer_name,
    c.city,
    c.country,

    t.product_id,
    p.product_code,
    p.product_category,
    p.msrp,

    t.quantity_ordered,
    t.estimated_cost_per_unit,
    t.selling_price,
    t.sales,
    t.profit_per_unit,
    t.total_profit_loss,
    t.status,
    t.deal_size

FROM public.transactions AS t

INNER JOIN public.customers AS c
    ON t.customer_id = c.customer_id

INNER JOIN public.products AS p
    ON t.product_id = p.product_id;
