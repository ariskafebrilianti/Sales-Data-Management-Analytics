INSERT INTO public.products (
    product_code,
    product_category,
    msrp
)
SELECT DISTINCT
    TRIM(product_code),
    TRIM(product),
    REPLACE(
        REPLACE(TRIM(msrp), '.', ''),
        ',',
        '.'
    )::NUMERIC(12,2)
FROM public.raw_sales_staging
WHERE import_batch_id =
    'b85e058c-cece-5d7f-8eef-f30a58dc0679'
  AND LOWER(TRIM(customer_code)) <> 'total'

ON CONFLICT (product_code)
DO NOTHING

RETURNING
    product_id,
    product_code,
    product_category,
    msrp;