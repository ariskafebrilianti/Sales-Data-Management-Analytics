WITH source_data AS (
    SELECT
        TRIM(customer_code) AS source_transaction_code,
        TRIM(quantity_ordered)::INTEGER AS quantity_ordered,

        REPLACE(
            REPLACE(TRIM(sales), '.', ''),
            ',',
            '.'
        )::NUMERIC(14,2) AS sales,

        REPLACE(
            REPLACE(TRIM(total_profit_loss), '.', ''),
            ',',
            '.'
        )::NUMERIC(14,2) AS total_profit_loss

    FROM public.raw_sales_staging
    WHERE import_batch_id =
        'b85e058c-cece-5d7f-8eef-f30a58dc0679'
      AND LOWER(TRIM(customer_code)) <> 'total'
),

source_totals AS (
    SELECT
        COUNT(*) AS source_rows,
        COUNT(DISTINCT source_transaction_code) AS unique_source_codes,
        SUM(quantity_ordered) AS source_quantity,
        SUM(sales) AS source_sales,
        SUM(total_profit_loss) AS source_profit
    FROM source_data
),

target_totals AS (
    SELECT
        COUNT(*) AS target_rows,
        COUNT(DISTINCT source_transaction_code) AS unique_target_codes,
        SUM(quantity_ordered) AS target_quantity,
        SUM(sales) AS target_sales,
        SUM(total_profit_loss) AS target_profit
    FROM public.transactions
),

row_checks AS (
    SELECT
        COUNT(*) FILTER (
            WHERE t.transaction_id IS NULL
        ) AS missing_transactions,

        COUNT(*) FILTER (
            WHERE t.transaction_id IS NOT NULL
              AND (
                  t.quantity_ordered IS DISTINCT FROM s.quantity_ordered
                  OR t.sales IS DISTINCT FROM s.sales
                  OR t.total_profit_loss IS DISTINCT FROM s.total_profit_loss
              )
        ) AS mismatched_rows

    FROM source_data s
    LEFT JOIN public.transactions t
        ON t.source_transaction_code = s.source_transaction_code
),

extra_rows AS (
    SELECT COUNT(*) AS extra_transactions
    FROM public.transactions t
    LEFT JOIN source_data s
        ON s.source_transaction_code = t.source_transaction_code
    WHERE s.source_transaction_code IS NULL
)

SELECT
    st.source_rows,
    tt.target_rows,

    st.source_quantity,
    tt.target_quantity,
    tt.target_quantity - st.source_quantity AS quantity_difference,

    st.source_sales,
    tt.target_sales,
    tt.target_sales - st.source_sales AS sales_difference,

    st.source_profit,
    tt.target_profit,
    tt.target_profit - st.source_profit AS profit_difference,

    rc.missing_transactions,
    er.extra_transactions,
    rc.mismatched_rows,

    (
        st.source_rows = tt.target_rows
        AND st.source_quantity = tt.target_quantity
        AND st.source_sales = tt.target_sales
        AND st.source_profit = tt.target_profit
        AND rc.missing_transactions = 0
        AND er.extra_transactions = 0
        AND rc.mismatched_rows = 0
    ) AS reconciliation_passed

FROM source_totals st
CROSS JOIN target_totals tt
CROSS JOIN row_checks rc
CROSS JOIN extra_rows er;