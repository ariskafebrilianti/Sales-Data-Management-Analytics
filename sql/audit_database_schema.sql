
-- ==================================================
-- AUDIT: DATABASE SCHEMA INVENTORY
-- Purpose: Inspect tables, views, and their columns
-- ==================================================

SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'transactions',
      'customers',
      'products',
      'raw_sales_staging',
      'vw_sales_kpis',
      'vw_monthly_sales',
      'vw_product_performance',
      'vw_customer_performance',
      'vw_geographic_sales',
      'vw_deal_size_performance'
  )
ORDER BY
    table_name,
    ordinal_position;
