#!/bin/sh
# Render provides DATABASE_URL as postgresql:// but we need postgresql+asyncpg://
export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
uv run alembic upgrade head
uv run fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}
