SELECT
    COUNT(*) AS total_transactions,
    COUNT(created_at) AS transactions_with_timestamp,
    COUNT(*) FILTER (
        WHERE created_at IS NULL
    ) AS transactions_without_timestamp
FROM public.transactions;