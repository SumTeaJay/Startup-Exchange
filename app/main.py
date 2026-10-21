from fastapi import FastAPI

from app.api import router
from app.db import Base, engine
from app import models  # noqa: F401


Base.metadata.create_all(bind=engine)
app = FastAPI(title="Startup Exchange", version="0.1.0")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
