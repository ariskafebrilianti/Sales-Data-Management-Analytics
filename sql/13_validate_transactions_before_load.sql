WITH source_rows AS (
    SELECT *
    FROM public.raw_sales_staging
    WHERE import_batch_id =
        'b85e058c-cece-5d7f-8eef-f30a58dc0679'
      AND LOWER(TRIM(customer_code)) <> 'total'
),

matched_rows AS (
    SELECT
        s.source_row_number,
        s.customer_code,
        c.customer_id,
        p.product_id
    FROM source_rows s

    LEFT JOIN public.customers c
        ON c.customer_name = TRIM(s.customer_name)
       AND c.city = TRIM(s.city)
       AND c.country = TRIM(s.country)

    LEFT JOIN public.products p
        ON p.product_code = TRIM(s.product_code)
),

existing_rows AS (
    SELECT COUNT(*) AS existing_transaction_codes
    FROM public.transactions t
    INNER JOIN source_rows s
        ON t.source_transaction_code = TRIM(s.customer_code)
)

SELECT
    COUNT(*) AS source_rows,

    COUNT(customer_id) AS matched_customer_rows,

    COUNT(*) FILTER (
        WHERE customer_id IS NULL
    ) AS unmatched_customer_rows,

    COUNT(product_id) AS matched_product_rows,

    COUNT(*) FILTER (
        WHERE product_id IS NULL
    ) AS unmatched_product_rows,

    COUNT(DISTINCT customer_id) AS distinct_customers_used,

    COUNT(DISTINCT product_id) AS distinct_products_used,

    (SELECT existing_transaction_codes FROM existing_rows)
        AS existing_transaction_codes

FROM matched_rows;