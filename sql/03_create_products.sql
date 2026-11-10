
CREATE TABLE IF NOT EXISTS products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_code TEXT NOT NULL UNIQUE,
    product_category TEXT NOT NULL,
    msrp NUMERIC(12,2) NOT NULL,

    CONSTRAINT chk_product_msrp
        CHECK (msrp >= 0)
);
