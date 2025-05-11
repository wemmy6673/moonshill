from fastapi import APIRouter
from .workspace import router as workspace_router

router = APIRouter()

router.include_router(workspace_router)
