from services.logging import init_logger
from config.settings import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.entry import router as entry_router
from services.task_queue.tkq import broker
from contextlib import asynccontextmanager
from typing import AsyncGenerator


logger = init_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not broker.is_worker_process:
        await broker.startup()
    logger.info("Broker started")

    yield

    if not broker.is_worker_process:
        await broker.shutdown()
    logger.info("Broker shutdown")

app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[*settings.cors_allow_origins, settings.frontend_url],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(entry_router, prefix="/api")


@app.get("/")
def ping():
    return {"ping": "pong"}
