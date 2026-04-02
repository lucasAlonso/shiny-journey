from fastapi import FastAPI

app = FastAPI(title="lucasAlonso")


@app.get("/")
async def root():
    return {"message": "hola chaval"}


@app.get("/health")
async def healt():
    return {"status": "ok"}
