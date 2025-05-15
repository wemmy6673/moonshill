from fastapi import APIRouter
from .workspace import router as workspace_router
from .campaigns import router as campaigns_router
from .platform_connections import router as platform_connections_router

router = APIRouter()

router.include_router(workspace_router)
router.include_router(campaigns_router)
router.include_router(platform_connections_router)
