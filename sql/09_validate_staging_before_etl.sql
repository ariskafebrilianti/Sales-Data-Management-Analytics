WITH transaction_source AS (
    SELECT *
    FROM raw_sales_staging
    WHERE import_batch_id =
        'b85e058c-cece-5d7f-8eef-f30a58dc0679'
      AND LOWER(TRIM(customer_code)) <> 'total'
),

validation AS (
    SELECT
        COUNT(*) AS transaction_rows,

        COUNT(DISTINCT customer_code)
            AS unique_source_codes,

        COUNT(*) - COUNT(DISTINCT customer_code)
            AS duplicate_source_codes,

        COUNT(DISTINCT (
            customer_name,
            city,
            country
        )) AS unique_customers,

        COUNT(DISTINCT product_code)
            AS unique_products,

        COUNT(*) FILTER (
            WHERE
                NULLIF(TRIM(quantity_ordered), '') IS NULL
                OR TRIM(quantity_ordered) !~ '^[0-9]+$'

                OR NULLIF(TRIM(msrp), '') IS NULL
                OR REPLACE(REPLACE(TRIM(msrp), '.', ''), ',', '.')
                    !~ '^-?[0-9]+([.][0-9]+)?$'

                OR NULLIF(TRIM(estimated_cost_price_50_pct), '') IS NULL
                OR REPLACE(REPLACE(TRIM(estimated_cost_price_50_pct), '.', ''), ',', '.')
                    !~ '^-?[0-9]+([.][0-9]+)?$'

                OR NULLIF(TRIM(selling_price), '') IS NULL
                OR REPLACE(REPLACE(TRIM(selling_price), '.', ''), ',', '.')
                    !~ '^-?[0-9]+([.][0-9]+)?$'

                OR NULLIF(TRIM(sales), '') IS NULL
                OR REPLACE(REPLACE(TRIM(sales), '.', ''), ',', '.')
                    !~ '^-?[0-9]+([.][0-9]+)?$'

                OR NULLIF(TRIM(profit_per_unit), '') IS NULL
                OR REPLACE(REPLACE(TRIM(profit_per_unit), '.', ''), ',', '.')
                    !~ '^-?[0-9]+([.][0-9]+)?$'

                OR NULLIF(TRIM(total_profit_loss), '') IS NULL
                OR REPLACE(REPLACE(TRIM(total_profit_loss), '.', ''), ',', '.')
                    !~ '^-?[0-9]+([.][0-9]+)?$'
        ) AS invalid_numeric_rows,

        COUNT(*) FILTER (
            WHERE TRIM(order_date)
                !~ '^[A-Za-z]+, [0-9]{2} [A-Za-z]+ [0-9]{4}$'
        ) AS invalid_date_rows,

        COUNT(*) FILTER (
            WHERE TRIM(status) NOT IN ('Profit', 'Loss')
        ) AS invalid_status_rows,

        COUNT(*) FILTER (
            WHERE TRIM(deal_size)
                NOT IN ('Small', 'Medium', 'Large')
        ) AS invalid_deal_size_rows,

        COUNT(*) FILTER (
            WHERE
                NULLIF(TRIM(customer_name), '') IS NULL
                OR NULLIF(TRIM(product), '') IS NULL
                OR NULLIF(TRIM(product_code), '') IS NULL
                OR NULLIF(TRIM(city), '') IS NULL
                OR NULLIF(TRIM(country), '') IS NULL
        ) AS missing_required_text_rows

    FROM transaction_source
)

SELECT *
FROM validation;