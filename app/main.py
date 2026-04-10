from fastapi import FastAPI
from app.routers import tasks

from contextlib import asynccontextmanager
from app.core.database import engine
from app.models.base import Base


@asynccontextmanager
async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="alonsoTheOne", lifespan=lifespan)

app.include_router(tasks.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
