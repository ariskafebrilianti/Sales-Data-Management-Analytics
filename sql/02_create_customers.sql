
CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,

    CONSTRAINT uq_customer_identity
        UNIQUE (customer_name, city, country)
);
