.PHONY: dev build up down migrate migration test lint format
# Development server (local)
dev:
	uv run fastapi dev app/main.py
# Docker
build:
	docker compose build
up:
	docker compose up -d
down:
	docker compose down
# Database
migrate:
	uv run alembic upgrade head
migration:
	uv run alembic revision --autogenerate -m "$(msg)"
downgrade:
	uv run alembic downgrade -1
# Code quality
lint:
	uv run ruff check .
	uv run ruff format --check .
format:
	uv run ruff check --fix .
	uv run ruff format .
# Tests
test:
	uv run pytest
