INSERT INTO public.customers (
    customer_name,
    city,
    country
)
SELECT DISTINCT
    TRIM(customer_name),
    TRIM(city),
    TRIM(country)
FROM public.raw_sales_staging
WHERE import_batch_id =
    'b85e058c-cece-5d7f-8eef-f30a58dc0679'
  AND LOWER(TRIM(customer_code)) <> 'total'

ON CONFLICT (customer_name, city, country)
DO NOTHING

RETURNING
    customer_id,
    customer_name,
    city,
    country;