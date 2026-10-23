#!/usr/bin/env bash
set -Eeuo pipefail

: "${POSTGRES_ADMIN_URL:?Set POSTGRES_ADMIN_URL to an administrative PostgreSQL connection string}"
: "${APP_DB_PASSWORD:?Set APP_DB_PASSWORD to the application database password}"

APP_DB="${APP_DB:-startup_exchange}"
APP_DB_USER="${APP_DB_USER:-startup_exchange}"

psql "$POSTGRES_ADMIN_URL" \
  --set=ON_ERROR_STOP=1 \
  --set=app_db="$APP_DB" \
  --set=app_user="$APP_DB_USER" \
  --set=app_password="$APP_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'app_user', :'app_password')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'app_user')\gexec

ALTER ROLE :"app_user" LOGIN PASSWORD :'app_password';

SELECT format('CREATE DATABASE %I OWNER %I', :'app_db', :'app_user')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'app_db')\gexec

ALTER DATABASE :"app_db" OWNER TO :"app_user";
GRANT CONNECT ON DATABASE :"app_db" TO :"app_user";
SQL

printf 'PostgreSQL database %s and role %s are ready.\n' "$APP_DB" "$APP_DB_USER"
