
-- =====================================================
-- VERIFY SALES DASHBOARD READER PRIVILEGES
-- =====================================================

SELECT
    rolname,
    rolcanlogin,
    rolsuper,
    rolcreatedb,
    rolcreaterole,
    rolinherit,
    rolreplication,
    rolbypassrls
FROM pg_roles
WHERE rolname = 'sales_dashboard_reader';


-- Check database and schema access
SELECT
    has_database_privilege(
        'sales_dashboard_reader',
        'postgres',
        'CONNECT'
    ) AS can_connect_database,

    has_schema_privilege(
        'sales_dashboard_reader',
        'public',
        'USAGE'
    ) AS can_use_public_schema;


-- Check object privileges
SELECT
    object_name,
    has_select,
    has_insert,
    has_update,
    has_delete
FROM (
    SELECT
        'vw_transaction_analytics' AS object_name,
        has_table_privilege(
            'sales_dashboard_reader',
            'public.vw_transaction_analytics',
            'SELECT'
        ) AS has_select,
        has_table_privilege(
            'sales_dashboard_reader',
            'public.vw_transaction_analytics',
            'INSERT'
        ) AS has_insert,
        has_table_privilege(
            'sales_dashboard_reader',
            'public.vw_transaction_analytics',
            'UPDATE'
        ) AS has_update,
        has_table_privilege(
            'sales_dashboard_reader',
            'public.vw_transaction_analytics',
            'DELETE'
        ) AS has_delete

    UNION ALL

    SELECT
        'transactions',
        has_table_privilege(
            'sales_dashboard_reader',
            'public.transactions',
            'SELECT'
        ),
        has_table_privilege(
            'sales_dashboard_reader',
            'public.transactions',
            'INSERT'
        ),
        has_table_privilege(
            'sales_dashboard_reader',
            'public.transactions',
            'UPDATE'
        ),
        has_table_privilege(
            'sales_dashboard_reader',
            'public.transactions',
            'DELETE'
        )
) AS privilege_check
ORDER BY object_name;
