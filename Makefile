.PHONY: setup dev build up down migrate migration downgrade test lint format reset
setup:
	docker compose up -d
	@sleep 3
	docker compose exec db psql -U postgres -c "CREATE DATABASE app;" 2>/dev/null || true
	docker compose exec db psql -U postgres -c "CREATE DATABASE test;" 2>/dev/null || true
	uv run alembic upgrade head
	@echo "Setup complete. Run 'make dev' or 'make up' to start."
dev:
	uv run fastapi dev app/main.py
build:
	docker compose build
up:
	docker compose up -d
down:
	docker compose down
reset:
	docker compose down -v
	docker compose up -d
	@sleep 3
	docker compose exec db psql -U postgres -c "CREATE DATABASE app;" 2>/dev/null || true
	docker compose exec db psql -U postgres -c "CREATE DATABASE test;" 2>/dev/null || true
	uv run alembic upgrade head
	@echo "Reset complete."
migrate:
	uv run alembic upgrade head
migration:
	uv run alembic revision --autogenerate -m "$(msg)"
	uv run ruff format alembic/versions/
downgrade:
	uv run alembic downgrade -1
test:
	uv run pytest -v
lint:
	uv run ruff check .
	uv run ruff format --check .
format:
	uv run ruff check --fix .
	uv run ruff format .
