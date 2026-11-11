SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'raw_sales_staging',
      'customers',
      'products',
      'transactions'
  )
ORDER BY table_name;
