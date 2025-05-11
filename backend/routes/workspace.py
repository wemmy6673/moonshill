from fastapi import APIRouter, HTTPException, Depends, status
from models.workspace import Workspace
from schemas import workspace as workspace_schema
from sqlalchemy.orm import Session
from services.database import get_db
from utils.helpers import verify_ethereum_signature
from services.security import access_security
from config.settings import get_settings
from datetime import timedelta
from services.logging import init_logger
from routes.deps import get_current_workspace

settings = get_settings()
logger = init_logger()

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=workspace_schema.AccessToken)
async def create_workspace(workspace: workspace_schema.CreateWorkspace, db: Session = Depends(get_db)):
    is_valid, error_message = verify_ethereum_signature(workspace.message, workspace.signature, workspace.owner_address)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    if db.query(Workspace).filter(Workspace.owner_address == workspace.owner_address).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="It seems you already have a workspace. Please log in instead.")

    db_workspace = Workspace(
        name=workspace.name,
        owner_address=workspace.owner_address,
        notification_email=workspace.notification_email
    )
    db.add(db_workspace)
    db.commit()

    db.refresh(db_workspace)

    payload = {
        "sub": db_workspace.id,
    }

    access_token = access_security.create_access_token(payload, expires_delta=timedelta(hours=settings.jwt_expiry))

    logger.info(f"Workspace created: {db_workspace.name} by {db_workspace.owner_address}")

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }


@router.post("/access-token", response_model=workspace_schema.AccessToken)
async def get_access_token(access_token_request: workspace_schema.AccessTokenRequest, db: Session = Depends(get_db)):
    is_valid, error_message = verify_ethereum_signature(access_token_request.message, access_token_request.signature, access_token_request.owner_address)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    db_workspace = db.query(Workspace).filter(Workspace.owner_address == access_token_request.owner_address).first()
    if not db_workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It seems you don't have a workspace yet. Please create one first.")

    payload = {
        "sub": db_workspace.id,
    }

    access_token = access_security.create_access_token(payload, expires_delta=timedelta(hours=settings.jwt_expiry))

    logger.info(f"Workspace access token created for {db_workspace.name} by {db_workspace.owner_address}")

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }


@router.get("/current", response_model=dict)
async def get_current_workspace(workspace: Workspace | None = Depends(get_current_workspace)):
    res = {
        "workspace": workspace_schema.Workspace(**workspace.to_dict()) if workspace else None
    }

    print("Res: ", res)

    return res
