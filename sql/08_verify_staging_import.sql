SELECT
    import_batch_id,
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE LOWER(TRIM(customer_code)) = 'total'
    ) AS summary_rows,

    COUNT(*) FILTER (
        WHERE LOWER(TRIM(customer_code)) <> 'total'
    ) AS transaction_rows,

    COUNT(*) FILTER (
        WHERE NULLIF(TRIM(sales), '') IS NOT NULL
    ) AS rows_with_sales,

    COUNT(*) FILTER (
        WHERE LOWER(TRIM(customer_code)) <> 'total'
          AND NULLIF(TRIM(sales), '') IS NOT NULL
    ) AS transaction_rows_with_sales,

    MIN(source_row_number) AS first_source_row,
    MAX(source_row_number) AS last_source_row

FROM raw_sales_staging

WHERE import_batch_id =
    'b85e058c-cece-5d7f-8eef-f30a58dc0679'

GROUP BY import_batch_id;