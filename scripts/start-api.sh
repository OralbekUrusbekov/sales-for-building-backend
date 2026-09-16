#!/usr/bin/env sh
set -e

echo "→ Waiting for database, then running migrations…"
alembic upgrade head

if [ "${SEED_ON_START:-true}" = "true" ]; then
  echo "→ Seeding reference data (idempotent)…"
  python -m app.seed
fi

echo "→ Starting Uvicorn on :8000"
if [ "${ENVIRONMENT:-development}" = "development" ]; then
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${WEB_CONCURRENCY:-2}"
fi
