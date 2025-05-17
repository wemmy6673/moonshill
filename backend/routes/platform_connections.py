from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.database import get_db
from services.platform_auth import PlatformAuthService
from schemas import platform_connections as platform_schema
from models.workspace import Workspace
from models.campaigns import Campaign
from models.platform_connections import PlatformConnection
from routes.deps import get_current_workspace, get_strict_current_workspace
from typing import List
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix="/platforms",
    tags=["Platform Connections"],
    dependencies=[Depends(get_current_workspace)]
)


@router.get("/campaign/{campaign_id}", response_model=List[platform_schema.PlatformConnection])
async def get_campaign_platform_connections(
    campaign_id: int,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_strict_current_workspace)
):
    """Get all platform connections for a specific campaign"""
    # Verify campaign belongs to workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    connections = db.query(PlatformConnection).filter(
        PlatformConnection.workspace_id == workspace.id,
        PlatformConnection.campaign_id == campaign_id
    ).all()
    return connections


@router.get("/campaign/{campaign_id}/{platform}", response_model=platform_schema.ConnectionStatus)
async def get_campaign_connection_status(
    campaign_id: int,
    platform: platform_schema.PlatformType,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_strict_current_workspace)
):
    """Get connection status for a specific platform in a campaign"""
    # Verify campaign belongs to workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    connection = db.query(PlatformConnection).filter(
        PlatformConnection.workspace_id == workspace.id,
        PlatformConnection.campaign_id == campaign_id,
        PlatformConnection.platform == platform
    ).first()

    if not connection:
        return platform_schema.ConnectionStatus(
            is_connected=False,
            campaign_id=campaign_id
        )

    return platform_schema.ConnectionStatus(
        is_connected=connection.is_connected,
        platform_username=connection.platform_username,
        connected_at=connection.connected_at,
        platform_metadata=connection.platform_metadata,
        campaign_id=campaign_id
    )


@router.post("/connect", response_model=platform_schema.ConnectionResponse)
async def initiate_platform_connection(
    connection_request: platform_schema.ConnectionRequest,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_strict_current_workspace)
):
    """Initiate a connection to a platform for a specific campaign"""
    # Verify campaign belongs to workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == connection_request.campaign_id,
        Campaign.workspace_id == workspace.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Check if connection already exists
    existing_connection = db.query(PlatformConnection).filter(
        PlatformConnection.workspace_id == workspace.id,
        PlatformConnection.campaign_id == connection_request.campaign_id,
        PlatformConnection.platform == connection_request.platform
    ).first()
    if existing_connection and existing_connection.is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {connection_request.platform} is already connected for this campaign"
        )

    auth_service = PlatformAuthService(db)

    if connection_request.platform == platform_schema.PlatformType.TWITTER:
        auth_url = await auth_service.initiate_twitter_connection(
            callback_url=connection_request.callback_url,
            campaign_id=connection_request.campaign_id,
            workspace_id=workspace.id
        )
    elif connection_request.platform == platform_schema.PlatformType.TELEGRAM:
        auth_url, state = await auth_service.initiate_telegram_connection(
            callback_url=connection_request.callback_url
        )
    elif connection_request.platform == platform_schema.PlatformType.DISCORD:
        auth_url, state = await auth_service.initiate_discord_connection(
            callback_url=connection_request.callback_url
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported platform"
        )

    return platform_schema.ConnectionResponse(
        auth_url=auth_url,
        platform=connection_request.platform,
        campaign_id=connection_request.campaign_id
    )


@router.post("/callbacks/{platform}", response_model=platform_schema.ConnectionStatus)
async def handle_platform_callback(
    platform: platform_schema.PlatformType,
    callback_data: platform_schema.ConnectionCallback,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_strict_current_workspace)
):
    """Handle the callback from a platform after authorization"""

    if platform != callback_data.platform:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform mismatch"
        )

    auth_service = PlatformAuthService(db)

    try:
        if platform == platform_schema.PlatformType.TWITTER:
            connection = await auth_service.verify_twitter_callback(
                auth_res_url=callback_data.auth_res_url,
                workspace_id=workspace.id,
                state=callback_data.state,
            )
        elif platform == platform_schema.PlatformType.TELEGRAM:
            # Telegram callback handling will be implemented differently
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Telegram callback not implemented yet"
            )
        elif platform == platform_schema.PlatformType.DISCORD:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Discord callback not implemented yet"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported platform"
            )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {platform} is already connected for this campaign"
        )

    return platform_schema.ConnectionStatus(
        is_connected=connection.is_connected,
        platform_username=connection.platform_username,
        connected_at=connection.connected_at,
        platform_metadata=connection.platform_metadata,
        campaign_id=callback_data.campaign_id
    )


@router.delete("/campaign/{campaign_id}/{platform}", status_code=status.HTTP_200_OK)
async def disconnect_platform(
    campaign_id: int,
    platform: platform_schema.PlatformType,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_strict_current_workspace)
):
    """Disconnect a platform from a campaign"""
    # Verify campaign belongs to workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    connection = db.query(PlatformConnection).filter(
        PlatformConnection.workspace_id == workspace.id,
        PlatformConnection.campaign_id == campaign_id,
        PlatformConnection.platform == platform
    ).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform connection not found"
        )

    db.delete(connection)
    db.commit()

    return {"message": f"Successfully disconnected {platform.value} from campaign {campaign_id}"}
