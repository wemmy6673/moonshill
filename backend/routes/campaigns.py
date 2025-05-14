from fastapi import APIRouter, HTTPException, Depends, status
from models.workspace import Workspace
from models.campaigns import Campaign
from schemas import campaigns as campaign_schema
from sqlalchemy.orm import Session
from services.database import get_db
from services.logging import init_logger
from routes.deps import get_current_workspace, get_strict_current_workspace


logger = init_logger()


router = APIRouter(prefix="/campaigns", tags=["Campaigns"], dependencies=[Depends(get_current_workspace)])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=campaign_schema.Campaign)
async def create_campaign(campaign: campaign_schema.CreateCampaign, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    if db.query(Campaign).filter(Campaign.campaign_name == campaign.campaign_name, Campaign.workspace_id == workspace.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campaign name already exists, please choose another name.")

    db_campaign = Campaign(
        workspace_id=workspace.id,
        campaign_name=campaign.campaign_name,
        campaign_type=campaign.campaign_type,
        target_platforms=campaign.target_platforms,
        engagement_style=campaign.engagement_style,
        campaign_start_date=campaign.campaign_start_date,
        campaign_timeline=campaign.campaign_timeline,
        project_name=campaign.project_name,
        project_info=campaign.project_info,
        target_audience=campaign.target_audience,
        campaign_goals=campaign.campaign_goals,
        project_website=campaign.project_website,
        project_twitter=campaign.project_twitter_handle,
        project_telegram=campaign.project_telegram_handle,
        project_discord=campaign.project_discord_handle,
        project_logo=campaign.project_logo,
        project_banner=campaign.project_banner,
        project_whitepaper=campaign.project_whitepaper,
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    logger.info(f"Campaign created: {db_campaign.campaign_name}")

    return db_campaign


@router.get("", response_model=list[campaign_schema.Campaign])
async def get_campaigns(db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaigns = db.query(Campaign).filter(Campaign.workspace_id == workspace.id).all()
    return campaigns


@router.get("/{campaign_id}", response_model=campaign_schema.Campaign)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    if campaign.workspace_id != workspace.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this campaign")

    return campaign


@router.put("/{campaign_id}", response_model=campaign_schema.Campaign)
async def update_campaign(campaign_id: int, campaign: campaign_schema.UpdateCampaign, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    db_campaign.campaign_name = campaign.campaign_name
    db_campaign.campaign_type = campaign.campaign_type
    db_campaign.target_platforms = campaign.target_platforms
    db_campaign.engagement_style = campaign.engagement_style
    db_campaign.campaign_start_date = campaign.campaign_start_date
    db_campaign.campaign_timeline = campaign.campaign_timeline
    db_campaign.project_name = campaign.project_name
    db_campaign.project_info = campaign.project_info
    db_campaign.target_audience = campaign.target_audience
    db_campaign.campaign_goals = campaign.campaign_goals
    db_campaign.project_website = campaign.project_website
    db_campaign.project_twitter = campaign.project_twitter_handle
    db_campaign.project_telegram = campaign.project_telegram_handle
    db_campaign.project_discord = campaign.project_discord_handle
    db_campaign.project_logo = campaign.project_logo
    db_campaign.project_banner = campaign.project_banner
    db_campaign.project_whitepaper = campaign.project_whitepaper

    db.commit()

    logger.info(f"Campaign updated: {db_campaign.campaign_name}")

    return db_campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_200_OK)
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    db.delete(campaign)
    db.commit()

    logger.info(f"Campaign deleted: {campaign.campaign_name}")

    return {"message": "Campaign deleted successfully"}
