
CREATE INDEX IF NOT EXISTS idx_transactions_customer
    ON transactions(customer_id);

CREATE INDEX IF NOT EXISTS idx_transactions_product
    ON transactions(product_id);

CREATE INDEX IF NOT EXISTS idx_transactions_order_date
    ON transactions(order_date);
