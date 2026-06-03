from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.base import create_db_and_tables
from app.db.session import SessionLocal
from app.services.bootstrap import seed_initial_data
from app.workers.scheduler import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    scheduler_service.start()
    yield


configure_logging()

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ready"}
