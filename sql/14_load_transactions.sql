WITH source_data AS (
    SELECT
        s.*,
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                TRIM(s.order_date),
                '^[^,]+,[[:space:]]*',
                ''
            ),
            '[[:space:]]+',
            ' ',
            'g'
        ) AS date_text
    FROM public.raw_sales_staging s
    WHERE s.import_batch_id =
        'b85e058c-cece-5d7f-8eef-f30a58dc0679'
      AND LOWER(TRIM(s.customer_code)) <> 'total'
),

parsed_data AS (
    SELECT
        source_data.*,
        SPLIT_PART(date_text, ' ', 1)::INTEGER AS day_number,
        LOWER(SPLIT_PART(date_text, ' ', 2)) AS month_name,
        SPLIT_PART(date_text, ' ', 3)::INTEGER AS year_number
    FROM source_data
)

INSERT INTO public.transactions (
    source_transaction_code,
    customer_id,
    product_id,
    order_date,
    quantity_ordered,
    estimated_cost_per_unit,
    selling_price,
    sales,
    profit_per_unit,
    total_profit_loss,
    status,
    deal_size
)

SELECT
    TRIM(s.customer_code),
    c.customer_id,
    p.product_id,

    MAKE_DATE(
        s.year_number,
        CASE s.month_name
            WHEN 'january' THEN 1
            WHEN 'february' THEN 2
            WHEN 'march' THEN 3
            WHEN 'april' THEN 4
            WHEN 'may' THEN 5
            WHEN 'june' THEN 6
            WHEN 'july' THEN 7
            WHEN 'august' THEN 8
            WHEN 'september' THEN 9
            WHEN 'october' THEN 10
            WHEN 'november' THEN 11
            WHEN 'december' THEN 12
        END,
        s.day_number
    ),

    TRIM(s.quantity_ordered)::INTEGER,

    REPLACE(
        REPLACE(TRIM(s.estimated_cost_price_50_pct), '.', ''),
        ',',
        '.'
    )::NUMERIC(12,2),

    REPLACE(
        REPLACE(TRIM(s.selling_price), '.', ''),
        ',',
        '.'
    )::NUMERIC(12,2),

    REPLACE(
        REPLACE(TRIM(s.sales), '.', ''),
        ',',
        '.'
    )::NUMERIC(14,2),

    REPLACE(
        REPLACE(TRIM(s.profit_per_unit), '.', ''),
        ',',
        '.'
    )::NUMERIC(12,2),

    REPLACE(
        REPLACE(TRIM(s.total_profit_loss), '.', ''),
        ',',
        '.'
    )::NUMERIC(14,2),

    TRIM(s.status),
    TRIM(s.deal_size)

FROM parsed_data s

INNER JOIN public.customers c
    ON c.customer_name = TRIM(s.customer_name)
   AND c.city = TRIM(s.city)
   AND c.country = TRIM(s.country)

INNER JOIN public.products p
    ON p.product_code = TRIM(s.product_code)

ON CONFLICT (source_transaction_code)
DO NOTHING;