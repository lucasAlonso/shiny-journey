# p3 — FastAPI Starter

FastAPI + PostgreSQL + Docker + Alembic + CI/CD

## Quick Start

Prerequisites: [uv](https://docs.astral.sh/uv/), Docker, Python 3.12+

1. Clone and setup:

   ```bash
   git clone <repo-url>
   cd p3
   cp .env.example .env
   make setup
   ```

2. Start developing:

   ```bash
   make dev        # local dev server with auto-reload
   make up         # or run in Docker
   ```

3. Open http://localhost:8000/docs

## Common Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start local dev server |
| `make up` | Start Docker services |
| `make down` | Stop Docker services |
| `make migration msg="description"` | Generate a new migration |
| `make migrate` | Apply pending migrations |
| `make test` | Run tests |
| `make lint` | Check code quality |
| `make format` | Auto-fix code style |
| `make reset` | Reset databases from scratch |

## Project Structure

```
app/
├── core/         # config, database, dependencies
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic request/response schemas
├── routers/      # API route handlers
└── services/     # Business logic
tests/            # pytest tests
alembic/          # Database migrations
```

## Deployment

Push to `main` → GitHub Actions runs lint + tests → Render auto-deploys.
