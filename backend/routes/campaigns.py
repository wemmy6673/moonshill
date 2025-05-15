from fastapi import APIRouter, HTTPException, Depends, status
from models.workspace import Workspace
from models.campaigns import Campaign
from schemas import campaigns as campaign_schema
from sqlalchemy.orm import Session
from services.database import get_db
from services.logging import init_logger
from routes.deps import get_current_workspace, get_strict_current_workspace
from typing import Any
from pydantic import BaseModel
import inspect


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


@router.get("/{campaign_id}", response_model=campaign_schema.Campaign)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db), workspace: Workspace = Depends(get_strict_current_workspace)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.workspace_id == workspace.id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    if campaign.workspace_id != workspace.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this campaign")

    def campaign_from_db_to_schema(campaign: Campaign) -> campaign_schema.Campaign:
        c = campaign_schema.Campaign(
            id=campaign.id,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            status=campaign.status,
            is_active=campaign.is_active,
            is_paused=campaign.is_paused,
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
            tokenomics=campaign_schema.TokenomicsInfo(
                initial_price=campaign.project_token_initial_price,
                current_price=campaign.project_token_current_price,
                market_cap=campaign.project_market_cap,
                circulating_supply=campaign.project_circulating_supply,
                total_supply=campaign.project_token_supply,
                launch_date=campaign.token_launch_date,
                project_token_address=campaign.project_token_address,
                project_token_symbol=campaign.project_token_symbol,
                project_token_decimals=campaign.project_token_decimals,
            ),
            technical_info=campaign_schema.TechnicalInfo(
                blockchain_networks=campaign.blockchain_networks or [],
                smart_contract_features=campaign.smart_contract_features or [],
                technology_stack=campaign.technology_stack or [],
                github_repository=str(campaign.github_repository) if campaign.github_repository else None,
                audit_reports=campaign.audit_reports or [],
            ),
            market_info=campaign_schema.MarketInfo(
                target_markets=campaign.target_markets or [],
                competitor_analysis=campaign.competitor_analysis or [],
                unique_selling_points=campaign.unique_selling_points or [],
                market_positioning=campaign.market_positioning,
            ),
        )
        return c

    def get_campaign_completion_percentage(campaign: campaign_schema.Campaign) -> int:
        """
        Calculate the completion percentage of a campaign by checking all fields including nested models.
        """
        def count_field_completion(obj: Any, model_class: type[BaseModel]) -> tuple[int, int]:
            if obj is None:
                return 0, len(model_class.model_fields)

            total_fields = 0
            completed_fields = 0

            for field_name, field in obj.model_fields.items():
                # Skip metadata fields
                if field_name in {'id', 'created_at', 'updated_at', 'status', 'is_active', 'is_paused', 'completion_percentage'}:
                    continue

                field_value = getattr(obj, field_name, None)

                # Handle nested models
                if field_name in {'tokenomics', 'technical_info', 'market_info'}:
                    if field_value is not None:
                        nested_completed, nested_total = count_field_completion(field_value, type(field_value))
                        total_fields += nested_total
                        completed_fields += nested_completed
                    else:
                        total_fields += 1
                    continue

                total_fields += 1

                # Handle lists and arrays
                if isinstance(field_value, (list, dict)):
                    if field_value:
                        completed_fields += 1
                    continue

                # Count all non-empty fields as completed
                if field_value is not None and field_value != "":
                    completed_fields += 1

            return completed_fields, total_fields

        completed, total = count_field_completion(campaign, type(campaign))
        percentage = round(((completed / total) * 100) + 16) if total > 0 else 0
        return percentage

    c = campaign_from_db_to_schema(campaign)
    c.completion_percentage = get_campaign_completion_percentage(c)
    return c


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


BASIC_TIER = {
    "price": "$199/month",
    "features": {
        "max_campaigns": 1,
        "posts_per_day": 10,
        "platforms": ["Twitter", "Telegram"],
        "ai_creativity_level": 0.5,
        "analytics": "basic"
    }
}

PRO_TIER = {
    "price": "$499/month",
    "features": {
        "max_campaigns": 3,
        "posts_per_day": 30,
        "platforms": ["Twitter", "Telegram", "Discord", "Medium"],
        "ai_creativity_level": 0.7,
        "analytics": "advanced",
        "meme_generation": True
    }
}

ENTERPRISE_TIER = {
    "price": "$1999/month",
    "features": {
        "max_campaigns": "unlimited",
        "posts_per_day": "unlimited",
        "platforms": "all",
        "ai_creativity_level": "customizable",
        "analytics": "premium",
        "custom_features": True,
        "dedicated_support": True
    }
}
