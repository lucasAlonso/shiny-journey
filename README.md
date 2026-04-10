# p3 — Task Scheduler API

A system that solves the problem of choosing which tasks to execute, maximizing total profit while respecting resource constraints. Tasks that share resources are incompatible and cannot be scheduled together.

FastAPI + PostgreSQL + Docker + Alembic + CI/CD

## How It Works

Each task has a name, a list of required resources, and a profit value. If two tasks require the same resource, they are incompatible. The scheduler finds the subset of tasks that maximizes total profit with no resource conflicts.

**Algorithm**: Two-tier approach — exact branch-and-bound for ≤20 tasks (guaranteed optimal), greedy heuristic for larger batches (fast approximation). All tasks (new + previously buffered) are re-evaluated on every submission.

## Quick Start

Prerequisites: [uv](https://docs.astral.sh/uv/), Docker, Python 3.12+

1. Clone and setup:

   ```bash
   git clone <repo-url>
   cd p3
   cp .env.example .env
   make install   # install dependencies + pre-commit hook
   make setup     # start database + run migrations
   ```

2. Start developing:

   ```bash
   make dev        # local dev server with auto-reload
   make up         # or run in Docker
   ```

3. Open http://localhost:8000/docs

## API Usage

### Submit tasks for scheduling

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {"name": "capture for client 1098", "resources": ["camera", "disk", "proc"], "profit": 9.2},
      {"name": "clean satellite disk", "resources": ["disk"], "profit": 0.4},
      {"name": "upgrade to v2.1", "resources": ["proc"], "profit": 2.9}
    ]
  }'
```

Response:

```json
{
  "scheduled": [
    {"id": 1, "name": "capture for client 1098", "resources": ["camera", "disk", "proc"], "profit": 9.2, "status": "scheduled", "created_at": "..."},
    {"id": 3, "name": "upgrade to v2.1", "resources": ["proc"], "profit": 2.9, "status": "scheduled", "created_at": "..."}
  ],
  "buffered": [
    {"id": 2, "name": "clean satellite disk", "resources": ["disk"], "profit": 0.4, "status": "buffered", "created_at": "..."}
  ],
  "total_profit": 12.1
}
```

### List tasks

```bash
# All tasks
curl http://localhost:8000/tasks/

# Filter by status
curl http://localhost:8000/tasks/?status=scheduled
curl http://localhost:8000/tasks/?status=buffered
```

### Delete a task

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

### Validation rules

- `name` — non-empty string (whitespace-only rejected)
- `resources` — list of strings (can be empty)
- `profit` — non-negative float (0.0 is valid)

## Buffer Behavior

When new tasks are submitted, the system:

1. Fetches all existing tasks from the database (both scheduled and buffered)
2. Merges them with the new tasks
3. Re-runs the scheduler on the full set
4. Previously scheduled tasks may be displaced if a more profitable combination exists

This means a second submission can bump a previously scheduled task back to buffered if the new tasks create a better overall combination.

## Common Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies + pre-commit hook |
| `make setup` | Install deps, start DB, run migrations |
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
├── models/       # SQLAlchemy ORM models (Task)
├── schemas/      # Pydantic request/response schemas
├── routers/      # API route handlers (tasks)
└── services/     # Business logic (scheduler)
tests/            # pytest tests (32 tests)
alembic/          # Database migrations
```

## Deployment

Push to `main` → GitHub Actions runs lint + tests → Render auto-deploys.
