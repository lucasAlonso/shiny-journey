from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import items


@asynccontextmanager
async def lifespan(app):
    yield


app = FastAPI(title="alonsoTheOne", lifespan=lifespan)
app.include_router(items.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
