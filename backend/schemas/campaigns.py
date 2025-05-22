from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import SettingsConfigDict
from datetime import datetime
from typing import Optional, Dict, List, Any
from .enums import CampaignType, TargetPlatform, EngagementStyle, TargetAudience, CampaignGoal, CampaignTimeline, CampaignStatus


class TokenomicsInfo(BaseModel):
    initial_price: Optional[float] = Field(default=None, alias="initialPrice")
    current_price: Optional[float] = Field(default=None, alias="currentPrice")
    market_cap: Optional[float] = Field(default=None, alias="marketCap")
    circulating_supply: Optional[float] = Field(default=None, alias="circulatingSupply")
    total_supply: Optional[float] = Field(default=None, alias="totalSupply")
    token_distribution: Optional[Dict] = Field(default=None, alias="tokenDistribution")
    vesting_schedule: Optional[Dict] = Field(default=None, alias="vestingSchedule")
    launch_date: Optional[datetime] = Field(default=None, alias="launchDate")
    project_token_address: Optional[str] = Field(default=None, alias="projectTokenAddress")
    project_token_symbol: Optional[str] = Field(default=None, alias="projectTokenSymbol")
    project_token_decimals: Optional[int] = Field(default=None, alias="projectTokenDecimals")

    model_config = SettingsConfigDict(populate_by_name=True)


class TechnicalInfo(BaseModel):
    blockchain_networks: list[str] = Field(default_factory=list, alias="blockchainNetworks")
    smart_contract_features: list[str] = Field(default_factory=list, alias="smartContractFeatures")
    technology_stack: list[str] = Field(default_factory=list, alias="technologyStack")
    github_repository: Optional[HttpUrl] = Field(default=None, alias="githubRepository")
    audit_reports: list[HttpUrl] = Field(default_factory=list, alias="auditReports")

    model_config = SettingsConfigDict(populate_by_name=True)


class MarketInfo(BaseModel):
    target_markets: list[str] = Field(default_factory=list, alias="targetMarkets")
    competitor_analysis: List[Dict] = Field(default_factory=list, alias="competitorAnalysis")
    unique_selling_points: list[str] = Field(default_factory=list, alias="uniqueSellingPoints")
    market_positioning: Optional[str] = Field(default=None, alias="marketPositioning")

    model_config = SettingsConfigDict(populate_by_name=True)


class CommunityMetrics(BaseModel):
    community_size: Dict[str, int] = Field(default_factory=dict, alias="communitySize")
    growth_rate: Dict[str, float] = Field(default_factory=dict, alias="growthRate")
    engagement_rate: Dict[str, float] = Field(default_factory=dict, alias="engagementRate")
    influencer_partnerships: List[Dict] = Field(default_factory=list, alias="influencerPartnerships")

    model_config = SettingsConfigDict(populate_by_name=True)


class CampaignSpecifics(BaseModel):
    key_messages: list[str] = Field(default_factory=list, alias="keyMessages")
    prohibited_terms: list[str] = Field(default_factory=list, alias="prohibitedTerms")
    tone_guidelines: Optional[str] = Field(default=None, alias="toneGuidelines")
    campaign_budget: Optional[float] = Field(default=None, alias="campaignBudget")
    campaign_kpis: Dict = Field(default_factory=dict, alias="campaignKpis")
    content_guidelines: Dict = Field(default_factory=dict, alias="contentGuidelines")

    model_config = SettingsConfigDict(populate_by_name=True)


class ComplianceInfo(BaseModel):
    regulatory_restrictions: list[str] = Field(default_factory=list, alias="regulatoryRestrictions")
    restricted_territories: list[str] = Field(default_factory=list, alias="restrictedTerritories")
    compliance_requirements: list[str] = Field(default_factory=list, alias="complianceRequirements")

    model_config = SettingsConfigDict(populate_by_name=True)


class TeamInfo(BaseModel):
    team_members: List[Dict] = Field(default_factory=list, alias="teamMembers")
    project_history: Optional[str] = Field(default=None, alias="projectHistory")
    project_roadmap: Dict = Field(default_factory=dict, alias="projectRoadmap")
    previous_campaigns: List[Dict] = Field(default_factory=list, alias="previousCampaigns")

    model_config = SettingsConfigDict(populate_by_name=True)


class ContentAssets(BaseModel):
    brand_guidelines: Dict = Field(default_factory=dict, alias="brandGuidelines")
    content_themes: list[str] = Field(default_factory=list, alias="contentThemes")
    approved_hashtags: list[str] = Field(default_factory=list, alias="approvedHashtags")
    approved_media_assets: list[HttpUrl] = Field(default_factory=list, alias="approvedMediaAssets")
    content_calendar: Dict = Field(default_factory=dict, alias="contentCalendar")

    model_config = SettingsConfigDict(populate_by_name=True)


class CreateCampaign(BaseModel):
    # Basic Campaign Info
    campaign_name: str = Field(min_length=3, max_length=128, alias="campaignName")
    campaign_type: CampaignType = Field(alias="campaignType")
    target_platforms: list[TargetPlatform] = Field(alias="targetPlatforms")
    engagement_style: EngagementStyle = Field(alias="engagementStyle")
    campaign_start_date: datetime = Field(alias="campaignStartDate")
    campaign_timeline: CampaignTimeline = Field(alias="campaignTimeline")

    # Project Basic Info
    project_name: str = Field(min_length=3, max_length=128, alias="projectName")
    project_info: str = Field(alias="projectInfo")
    target_audience: list[TargetAudience] = Field(alias="targetAudience", min_length=1)
    campaign_goals: list[CampaignGoal] = Field(alias="campaignGoals", min_length=1)

    # Project Links
    project_website: Optional[HttpUrl] = Field(default=None, alias="projectWebsite")
    project_twitter: Optional[HttpUrl] = Field(default=None, alias="projectTwitter")
    project_telegram: Optional[HttpUrl] = Field(default=None, alias="projectTelegram")
    project_discord: Optional[HttpUrl] = Field(default=None, alias="projectDiscord")

    # Project Assets
    project_logo: Optional[HttpUrl] = Field(default=None, alias="projectLogo")
    project_banner: Optional[HttpUrl] = Field(default=None, alias="projectBanner")
    project_whitepaper: Optional[HttpUrl] = Field(default=None, alias="projectWhitepaper")

    # Extended Information
    tokenomics: Optional[TokenomicsInfo] = None
    technical_info: Optional[TechnicalInfo] = Field(default=None, alias="technicalInfo")
    market_info: Optional[MarketInfo] = Field(default=None, alias="marketInfo")
    # community_metrics: Optional[CommunityMetrics] = Field(default=None, alias="communityMetrics")
    # campaign_specifics: Optional[CampaignSpecifics] = Field(default=None, alias="campaignSpecifics")
    # compliance_info: Optional[ComplianceInfo] = Field(default=None, alias="complianceInfo")
    # team_info: Optional[TeamInfo] = Field(default=None, alias="teamInfo")
    # content_assets: Optional[ContentAssets] = Field(default=None, alias="contentAssets")

    model_config = SettingsConfigDict(populate_by_name=True)


class UpdateCampaign(CreateCampaign):
    pass


class Campaign(CreateCampaign):
    id: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    status: CampaignStatus = Field(alias="status")
    is_active: bool = Field(alias="isActive")
    is_paused: bool = Field(alias="isPaused")
    completion_percentage: int = Field(alias="completionPercentage", default=0)

    model_config = SettingsConfigDict(populate_by_name=True)


def campaign_from_db_to_schema(campaign: Campaign) -> Campaign:
    preferred_order = ["twitter", "telegram", "discord"]
    c = Campaign(
        id=campaign.id,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        status=campaign.status,
        is_active=campaign.is_active,
        is_paused=campaign.is_paused,
        campaign_name=campaign.campaign_name,
        campaign_type=campaign.campaign_type,
        target_platforms=sorted(
            campaign.target_platforms,
            key=lambda x: preferred_order.index(x.lower()) if x.lower() in preferred_order else len(preferred_order)
        ),
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
        tokenomics=TokenomicsInfo(
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
        technical_info=TechnicalInfo(
            blockchain_networks=campaign.blockchain_networks or [],
            smart_contract_features=campaign.smart_contract_features or [],
            technology_stack=campaign.technology_stack or [],
            github_repository=str(campaign.github_repository) if campaign.github_repository else None,
            audit_reports=campaign.audit_reports or [],
        ),
        market_info=MarketInfo(
            target_markets=campaign.target_markets or [],
            competitor_analysis=campaign.competitor_analysis or [],
            unique_selling_points=campaign.unique_selling_points or [],
            market_positioning=campaign.market_positioning,
        ),
    )
    return c


def get_campaign_completion_percentage(campaign: Campaign) -> int:
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
