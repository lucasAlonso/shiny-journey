FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
CMD uv run alembic upgrade head && uv run fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}
