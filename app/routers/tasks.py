from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db
from app.schemas.task import ScheduleRequest, ScheduleResponse, TaskResponse
from app.services.scheduler import schedule
from app.models.task import Task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=ScheduleResponse)
async def schedule_tasks(data: ScheduleRequest, db: AsyncSession = Depends(get_db)):
    new_tasks = []
    for t in data.tasks:
        task = Task(
            name=t.name, resources=t.resources, profit=t.profit, status="buffered"
        )
        db.add(task)
        new_tasks.append(task)
    await db.commit()
    for t in new_tasks:
        await db.refresh(t)

    result = await db.execute(select(Task))
    all_tasks = list(result.scalars().all())

    chosen, remaining = schedule([t.to_dict() for t in all_tasks])

    lookup = {}
    for t in all_tasks:
        key = (t.name, tuple(t.resources), t.profit)
        lookup[key] = t

    scheduled_tasks = []
    for t_dict in chosen:
        key = (t_dict["name"], tuple(t_dict["resources"]), t_dict["profit"])
        db_task = lookup[key]
        db_task.status = "scheduled"
        scheduled_tasks.append(db_task)

    buffered_tasks = []
    for t_dict in remaining:
        key = (t_dict["name"], tuple(t_dict["resources"]), t_dict["profit"])
        db_task = lookup[key]
        db_task.status = "buffered"
        buffered_tasks.append(db_task)

    await db.commit()

    total_profit = sum(t.profit for t in scheduled_tasks)
    return ScheduleResponse(
        scheduled=scheduled_tasks,
        buffered=buffered_tasks,
        total_profit=total_profit,
    )


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(status: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    result = await db.execute(query)

    return list(result.scalars().all())


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    await db.delete(task)
    await db.commit()
    return None
