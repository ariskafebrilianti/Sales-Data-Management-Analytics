
SELECT
    has_table_privilege(
        'sales_dashboard_reader',
        'public.transactions',
        'SELECT'
    ) AS can_read_transactions,

    has_table_privilege(
        'sales_dashboard_reader',
        'public.transactions',
        'INSERT'
    ) AS can_insert_transactions,

    has_table_privilege(
        'sales_dashboard_reader',
        'public.transactions',
        'UPDATE'
    ) AS can_update_transactions,

    has_table_privilege(
        'sales_dashboard_reader',
        'public.transactions',
        'DELETE'
    ) AS can_delete_transactions,

    has_table_privilege(
        'sales_dashboard_reader',
        'public.vw_transaction_analytics',
        'SELECT'
    ) AS can_read_analytics_view;
