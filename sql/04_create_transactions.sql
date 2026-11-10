
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_transaction_code TEXT NOT NULL UNIQUE,

    customer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,

    order_date DATE NOT NULL,
    quantity_ordered INTEGER NOT NULL,

    estimated_cost_per_unit NUMERIC(12,2) NOT NULL,
    selling_price NUMERIC(12,2) NOT NULL,
    sales NUMERIC(14,2) NOT NULL,

    profit_per_unit NUMERIC(12,2) NOT NULL,
    total_profit_loss NUMERIC(14,2) NOT NULL,

    status TEXT NOT NULL,
    deal_size TEXT NOT NULL,

    CONSTRAINT fk_transaction_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_transaction_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT chk_transaction_quantity
        CHECK (quantity_ordered > 0),

    CONSTRAINT chk_estimated_cost
        CHECK (estimated_cost_per_unit >= 0),

    CONSTRAINT chk_selling_price
        CHECK (selling_price >= 0),

    CONSTRAINT chk_sales
        CHECK (sales >= 0),

    CONSTRAINT chk_transaction_status
        CHECK (status IN ('Profit', 'Loss')),

    CONSTRAINT chk_transaction_deal_size
        CHECK (deal_size IN ('Small', 'Medium', 'Large'))
);
