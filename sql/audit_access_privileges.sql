
-- =====================================================
-- AUDIT ACCESS PRIVILEGES
-- Purpose: Inspect database roles, object privileges,
-- role memberships, and default privileges.
-- Read-only audit. No database changes.
-- =====================================================

-- 1. Inspect database roles
SELECT
    rolname AS role_name,
    rolsuper AS is_superuser,
    rolcreaterole AS can_create_role,
    rolcreatedb AS can_create_database,
    rolreplication AS can_replicate,
    rolbypassrls AS bypasses_rls,
    rolcanlogin AS can_login
FROM pg_roles
WHERE rolname IN (
    'postgres',
    'anon',
    'authenticated',
    'service_role',
    'sales_dashboard_reader'
)
ORDER BY rolname;


-- 2. Inspect privileges on public schema tables and views
SELECT
    grantee,
    table_schema,
    table_name,
    privilege_type,
    is_grantable
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND grantee IN (
      'PUBLIC',
      'anon',
      'authenticated',
      'service_role',
      'postgres',
      'sales_dashboard_reader'
  )
ORDER BY
    table_name,
    grantee,
    privilege_type;


-- 3. Inspect role memberships
SELECT
    member_role.rolname AS member_role,
    granted_role.rolname AS granted_role,
    grantor_role.rolname AS grantor_role,
    membership.admin_option
FROM pg_auth_members AS membership
JOIN pg_roles AS member_role
    ON membership.member = member_role.oid
JOIN pg_roles AS granted_role
    ON membership.roleid = granted_role.oid
JOIN pg_roles AS grantor_role
    ON membership.grantor = grantor_role.oid
WHERE member_role.rolname IN (
    'postgres',
    'anon',
    'authenticated',
    'service_role',
    'sales_dashboard_reader'
)
OR granted_role.rolname IN (
    'postgres',
    'anon',
    'authenticated',
    'service_role',
    'sales_dashboard_reader'
)
ORDER BY member_role.rolname, granted_role.rolname;


-- 4. Inspect default privileges for public schema
SELECT
    owner_role.rolname AS owner_role,
    schema_info.nspname AS schema_name,
    default_acl.defaclobjtype AS object_type,
    CASE
        WHEN privilege.grantee = 0 THEN 'PUBLIC'
        ELSE grantee_role.rolname
    END AS grantee,
    privilege.privilege_type,
    privilege.is_grantable
FROM pg_default_acl AS default_acl
JOIN pg_roles AS owner_role
    ON default_acl.defaclrole = owner_role.oid
JOIN pg_namespace AS schema_info
    ON default_acl.defaclnamespace = schema_info.oid
CROSS JOIN LATERAL aclexplode(default_acl.defaclacl) AS privilege
LEFT JOIN pg_roles AS grantee_role
    ON privilege.grantee = grantee_role.oid
WHERE schema_info.nspname = 'public'
ORDER BY owner_role.rolname, object_type, grantee;
