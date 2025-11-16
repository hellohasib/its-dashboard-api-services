#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Skipping migrations (tables already created manually)..."
# Note: Migrations are skipped because ANPR and Auth services share the same database
# and alembic_version table. Tables were created manually via SQL script.

echo "Starting ANPR service..."
cd /app/services/anpr-service
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

