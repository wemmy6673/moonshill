from fastapi import Depends, HTTPException, Security, status
from fastapi_jwt import JwtAuthorizationCredentials
from services.database import SessionLocal
from sqlalchemy.orm import Session
from arq.connections import create_pool
from contextlib import contextmanager, asynccontextmanager
from services.security import access_security
from services.logging import init_logger
from arq.connections import RedisSettings
from config.settings import get_settings
from models.workspace import Workspace


settings = get_settings()
logger = init_logger()


def get_db():
    db:  Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_arq():
    queue = await create_pool(settings.redis_url)
    try:
        yield queue
    finally:
        await queue.aclose()


def get_current_workspace(db: Session = Depends(get_db), credentials: JwtAuthorizationCredentials = Security(access_security)):
    workspace_id = credentials.payload.get("sub")
    if not workspace_id:
        return None

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return None
    return workspace


@contextmanager
def get_db_context():
    db:  Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_arq_context():
    queue = await create_pool(settings.redis_url)
    try:
        yield queue
    finally:
        await queue.aclose()
