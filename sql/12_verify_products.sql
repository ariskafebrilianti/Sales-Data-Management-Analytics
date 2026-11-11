SELECT
    COUNT(*) AS total_products,
    COUNT(DISTINCT product_code) AS unique_product_codes,
    COUNT(*) FILTER (
        WHERE msrp < 0
    ) AS negative_msrp,
    COUNT(*) FILTER (
        WHERE msrp IS NULL
    ) AS null_msrp,
    COUNT(DISTINCT product_category) AS total_categories
FROM public.products;