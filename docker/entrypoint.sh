#!/usr/bin/env sh
set -e

uv run wait-db
uv run python -m alembic upgrade head
uv run seed-db

exec uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
