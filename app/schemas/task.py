import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class TaskCreate(BaseModel):
    name: str
    resources: list[str]
    profit: float

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("name must not be empty")
        return v

    @field_validator("profit")
    @classmethod
    def profit_non_negative(cls, v):
        if v < 0:
            raise ValueError("profit must be non-negative")
        return v


class TaskResponse(BaseModel):
    id: int
    name: str
    resources: list[str]
    profit: float
    status: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)


class ScheduleRequest(BaseModel):
    tasks: list[TaskCreate]


class ScheduleResponse(BaseModel):
    scheduled: list[TaskResponse]
    buffered: list[TaskResponse]
    total_profit: float
