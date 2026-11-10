
-- Check total columns per table

SELECT
    table_name,
    COUNT(*) AS total_columns
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'raw_sales_staging',
      'customers',
      'products',
      'transactions'
  )
GROUP BY table_name
ORDER BY table_name;


-- Check foreign key relationships

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.constraint_schema = kcu.constraint_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.constraint_schema = tc.constraint_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;
