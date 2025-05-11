from services.logging import init_logger
from config.settings import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.entry import router as entry_router

logger = init_logger()
settings = get_settings()


app = FastAPI(title=settings.app_name, debug=settings.debug)


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
