import datetime

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str


class ItemResponse(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime

    class Config:
        from_atributes = True
