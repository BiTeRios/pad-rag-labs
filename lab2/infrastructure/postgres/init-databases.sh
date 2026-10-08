#!/bin/sh
# Database per service: у каждого сервиса своя БД и свой пользователь с паролем из окружения.
# Сервис видит только свою БД — чужие таблицы ему недоступны (REVOKE ... FROM PUBLIC).
# Выполняется один раз, при первом старте пустого тома postgres-data.
set -eu

for service in auth ingestion chat analytics; do
    upper=$(echo "$service" | tr '[:lower:]' '[:upper:]')
    password=$(eval "printf '%s' \"\${${upper}_DB_PASSWORD}\"")
    echo "init: база и пользователь $service"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
        -v name="$service" -v password="$password" <<'EOSQL'
CREATE USER :"name" WITH PASSWORD :'password';
CREATE DATABASE :"name" OWNER :"name";
REVOKE ALL ON DATABASE :"name" FROM PUBLIC;
EOSQL
done
