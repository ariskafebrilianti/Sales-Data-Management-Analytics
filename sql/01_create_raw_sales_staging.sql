
CREATE TABLE IF NOT EXISTS raw_sales_staging (
    staging_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    import_batch_id UUID NOT NULL DEFAULT gen_random_uuid(),
    source_row_number INTEGER,

    customer_code TEXT,
    customer_name TEXT,
    quantity_ordered TEXT,
    msrp TEXT,
    estimated_cost_price_50_pct TEXT,
    selling_price TEXT,
    sales TEXT,
    profit_per_unit TEXT,
    total_profit_loss TEXT,
    status TEXT,
    order_date TEXT,
    month TEXT,
    year TEXT,
    product TEXT,
    product_code TEXT,
    city TEXT,
    country TEXT,
    deal_size TEXT,

    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_staging_batch_row
        UNIQUE (import_batch_id, source_row_number)
);
