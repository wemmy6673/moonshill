from fastapi import APIRouter, HTTPException, Depends, status
from schemas.enums import CampaignStatus, EmailTemplate
from models.workspace import Workspace
from models.campaigns import Campaign, CampaignSettings
from models.platform_connections import PlatformConnection
from schemas import campaigns as campaign_schema, campaign_settings as campaign_settings_schema
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from services.database import get_db
from services.logging import init_logger
from routes.deps import get_current_workspace, get_strict_current_workspace
from services.task_queue import tasks
from services.campaign_manager import CampaignManager


logger = init_logger()


router = APIRouter(prefix="/campaigns", tags=["Campaigns"], dependencies=[Depends(get_current_workspace)])


@router.get("/{campaign_id}/generate-post", status_code=status.HTTP_200_OK)
async def generate_post(campaign_id: int, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    campaign_manager = CampaignManager(db)
    post = await campaign_manager.process_campaign(campaign.id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to generate post")

    return {"post": post}


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
        project_website=str(campaign.project_website) if campaign.project_website else None,
        project_twitter=str(campaign.project_twitter) if campaign.project_twitter else None,
        project_telegram=str(campaign.project_telegram) if campaign.project_telegram else None,
        project_discord=str(campaign.project_discord) if campaign.project_discord else None,
        project_logo=str(campaign.project_logo) if campaign.project_logo else None,
        project_banner=str(campaign.project_banner) if campaign.project_banner else None,
        project_whitepaper=str(campaign.project_whitepaper) if campaign.project_whitepaper else None,
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
    db_campaign.project_website = str(campaign.project_website) if campaign.project_website else None
    db_campaign.project_twitter = str(campaign.project_twitter) if campaign.project_twitter else None
    db_campaign.project_telegram = str(campaign.project_telegram) if campaign.project_telegram else None
    db_campaign.project_discord = str(campaign.project_discord) if campaign.project_discord else None
    db_campaign.project_logo = str(campaign.project_logo) if campaign.project_logo else None
    db_campaign.project_banner = str(campaign.project_banner) if campaign.project_banner else None
    db_campaign.project_whitepaper = str(campaign.project_whitepaper) if campaign.project_whitepaper else None

    db.commit()

    logger.info(f"Campaign updated: {db_campaign.campaign_name}")

    return db_campaign


@router.put("/tokenomics/{campaign_id}", response_model=campaign_schema.Campaign)
async def update_campaign_tokenomics(campaign_id: int, tokenomics: campaign_schema.TokenomicsInfo, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    db_campaign.project_token_initial_price = tokenomics.initial_price
    db_campaign.project_token_current_price = tokenomics.current_price
    db_campaign.project_market_cap = tokenomics.market_cap
    db_campaign.project_circulating_supply = tokenomics.circulating_supply
    db_campaign.project_token_supply = tokenomics.total_supply
    db_campaign.token_distribution = tokenomics.token_distribution
    db_campaign.vesting_schedule = tokenomics.vesting_schedule
    db_campaign.token_launch_date = tokenomics.launch_date
    db_campaign.project_token_address = tokenomics.project_token_address
    db_campaign.project_token_symbol = tokenomics.project_token_symbol
    db_campaign.project_token_decimals = tokenomics.project_token_decimals

    db.commit()

    logger.info(f"Campaign tokenomics updated: {db_campaign.campaign_name}")

    return db_campaign


@router.put("/technical/{campaign_id}", response_model=campaign_schema.Campaign)
async def update_campaign_technical(campaign_id: int, technical: campaign_schema.TechnicalInfo, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    db_campaign.blockchain_networks = technical.blockchain_networks
    db_campaign.smart_contract_features = technical.smart_contract_features
    db_campaign.technology_stack = technical.technology_stack
    db_campaign.github_repository = str(technical.github_repository) if technical.github_repository else None
    db_campaign.audit_reports = technical.audit_reports

    db.commit()

    logger.info(f"Campaign technical updated: {db_campaign.campaign_name}")

    return db_campaign


@router.put("/market/{campaign_id}", response_model=campaign_schema.Campaign)
async def update_campaign_market(campaign_id: int, market: campaign_schema.MarketInfo, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    db_campaign.target_markets = market.target_markets
    db_campaign.competitor_analysis = market.competitor_analysis
    db_campaign.unique_selling_points = market.unique_selling_points
    db_campaign.market_positioning = market.market_positioning

    db.commit()

    logger.info(f"Campaign market updated: {db_campaign.campaign_name}")

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


@router.get("/settings/{campaign_id}", response_model=campaign_settings_schema.CampaignSettings)
async def get_campaign_settings(campaign_id: int, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaign_settings = db.query(CampaignSettings).filter(CampaignSettings.campaign_id == campaign_id).first()
    if not campaign_settings:
        campaign_settings = CampaignSettings(campaign_id=campaign_id)
        db.add(campaign_settings)
        db.commit()
        db.refresh(campaign_settings)
    return campaign_settings


@router.put("/settings/{campaign_id}", response_model=campaign_settings_schema.CampaignSettings)
async def update_campaign_settings(
    campaign_id: int,
    update: campaign_settings_schema.FieldUpdate,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_strict_current_workspace)
):
    # Verify campaign exists and belongs to workspace
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    # Get or create campaign settings
    campaign_settings = db.query(CampaignSettings).filter(CampaignSettings.campaign_id == campaign_id).first()
    if not campaign_settings:
        campaign_settings = CampaignSettings(campaign_id=campaign_id)
        db.add(campaign_settings)
        db.commit()
        db.refresh(campaign_settings)

    field_name = update.field_name
    field_value = update.value

    if isinstance(field_value, dict) and hasattr(campaign_settings, field_name):
        current_value = getattr(campaign_settings, field_name) or {}
        current_value.update(field_value)
        setattr(campaign_settings, field_name, current_value)
        flag_modified(campaign_settings, field_name)

    elif isinstance(field_value, list) and hasattr(campaign_settings, field_name):
        setattr(campaign_settings, field_name, field_value)
    else:
        setattr(campaign_settings, field_name, field_value)

    try:
        db.commit()
        db.refresh(campaign_settings)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update setting: {str(e)}"
        )

    return campaign_settings


@router.get("/toggle-publish/{campaign_id}", status_code=status.HTTP_200_OK)
async def toggle_publish(campaign_id: int, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not campaign:
        logger.error(f"Campaign not found: {campaign_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    completed_percentage = campaign_schema.get_campaign_completion_percentage(campaign_schema.campaign_from_db_to_schema(campaign))

    if campaign.status == CampaignStatus.RUNNING:
        campaign.status = CampaignStatus.PAUSED
        db.commit()
        db.refresh(campaign)
        logger.info(f"Campaign paused: {campaign.campaign_name}")
        return {"message": "Campaign paused successfully"}

    if campaign.status == CampaignStatus.PAUSED or campaign.status == CampaignStatus.PENDING:
        if completed_percentage < 70:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Your campaign is not ready to be published. Please complete at least 70% of the campaign before publishing.")

        # count connected platforms
        n = db.query(PlatformConnection).filter(PlatformConnection.campaign_id == campaign_id, PlatformConnection.is_connected == True).count()
        if n < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You need to connect at least one platform to publish the campaign.")

        campaign.status = CampaignStatus.RUNNING
        db.commit()
        db.refresh(campaign)
        logger.info(f"Campaign published: {campaign.campaign_name}")

        if workspace.notification_email:
            await tasks.send_email.kiq(workspace.notification_email, EmailTemplate.CAMPAIGN_PUBLISHED, {
                "username": workspace.name,
                "campaign_name": campaign.campaign_name,
                "campaign_type": campaign.campaign_type,
                "target_platforms": campaign.target_platforms,
                "campaign_start_date": campaign.campaign_start_date.strftime("%Y-%m-%d"),
                "campaign_timeline": campaign.campaign_timeline,
                "engagement_style": campaign.engagement_style,
                "completion_percentage": completed_percentage,
            })

        return {"message": "Campaign published successfully"}

    if campaign.status == CampaignStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Your campaign is already completed. Please create a new campaign to publish a new project.")

    if campaign.status == CampaignStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Your campaign is cancelled. Please create a new campaign to publish a new project.")


@router.get("/{campaign_id}", response_model=campaign_schema.Campaign)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    if campaign.workspace_id != workspace.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this campaign")

    c = campaign_schema.campaign_from_db_to_schema(campaign)
    c.completion_percentage = campaign_schema.get_campaign_completion_percentage(c)
    return c
