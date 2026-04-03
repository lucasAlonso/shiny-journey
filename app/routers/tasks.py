from fastapi import APIRouter
from app.core.dependencies import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/")
async def schedule_tasks():
    return {"scheduled": [], "buffered": [], "total_profit": 0.0}


@router.get("/")
async def list_tasks(status: str | None = None):
    return []


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int):
    return None
