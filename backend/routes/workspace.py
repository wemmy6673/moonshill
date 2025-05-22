from fastapi import APIRouter, HTTPException, Depends, status, Query
from models.workspace import Workspace
from schemas import workspace as workspace_schema
from schemas.pricing import PricingResponse
from sqlalchemy.orm import Session
from services.database import get_db
from utils.helpers import verify_ethereum_signature
from services.security import access_security
from config.settings import get_settings
from datetime import timedelta
from services.logging import init_logger
from routes.deps import get_current_workspace
from services.pricing import PricingService
import random
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
async def get_current_workspace_route(workspace: Workspace | None = Depends(get_current_workspace)):
    res = {
        "workspace": workspace_schema.Workspace(**workspace.to_dict()) if workspace else None
    }

    return res


@router.get("/pricing", response_model=PricingResponse)
async def get_pricing(
    db: Session = Depends(get_db)
):
    """
    Get current pricing tiers and features.
    Returns the active pricing strategy and its tiers.
    """
    try:
        adjustment = random.randint(-20, -10)
        pricing_service = PricingService(price_adjustment=adjustment)  # Initialize with default price_adjustment
        pricing: PricingResponse = pricing_service.get_current_pricing()

        logger.info(f"Retrieved pricing strategy: {pricing.strategy} with default adjustment: {pricing.price_adjustment}%")
        return pricing

    except Exception as e:
        logger.error(f"Error getting pricing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve pricing information"
        )


@router.post("/validate-price-tag", response_model=workspace_schema.PriceTagValidation)
async def validate_price_tag(
    validation: workspace_schema.PriceTagValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a price tag to ensure it hasn't been tampered with.
    Used during signup to verify the selected pricing tier.
    """
    try:
        pricing_service = PricingService()
        validation_result = pricing_service.validate_price_tag(validation.price_tag)

        if not validation_result:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired price tag"
            )

        return {
            "is_valid": True,
            "details": validation_result
        }

    except Exception as e:
        logger.error(f"Error validating price tag: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to validate price tag"
        )
