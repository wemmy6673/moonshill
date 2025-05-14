from pydantic import BaseModel, Field, field_validator, ValidationError, EmailStr, HttpUrl, conlist
from pydantic_settings import SettingsConfigDict
from datetime import datetime
from eth_utils import is_address
from typing import Optional, Dict, List
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


class TechnicalInfo(BaseModel):
    blockchain_networks: list[str] = Field(default_factory=list, alias="blockchainNetworks")
    smart_contract_features: list[str] = Field(default_factory=list, alias="smartContractFeatures")
    technology_stack: list[str] = Field(default_factory=list, alias="technologyStack")
    github_repository: Optional[HttpUrl] = Field(default=None, alias="githubRepository")
    audit_reports: list[HttpUrl] = Field(default_factory=list, alias="auditReports")


class MarketInfo(BaseModel):
    target_markets: list[str] = Field(default_factory=list, alias="targetMarkets")
    competitor_analysis: List[Dict] = Field(default_factory=list, alias="competitorAnalysis")
    unique_selling_points: list[str] = Field(default_factory=list, alias="uniqueSellingPoints")
    market_positioning: Optional[str] = Field(default=None, alias="marketPositioning")


class CommunityMetrics(BaseModel):
    community_size: Dict[str, int] = Field(default_factory=dict, alias="communitySize")
    growth_rate: Dict[str, float] = Field(default_factory=dict, alias="growthRate")
    engagement_rate: Dict[str, float] = Field(default_factory=dict, alias="engagementRate")
    influencer_partnerships: List[Dict] = Field(default_factory=list, alias="influencerPartnerships")


class CampaignSpecifics(BaseModel):
    key_messages: list[str] = Field(default_factory=list, alias="keyMessages")
    prohibited_terms: list[str] = Field(default_factory=list, alias="prohibitedTerms")
    tone_guidelines: Optional[str] = Field(default=None, alias="toneGuidelines")
    campaign_budget: Optional[float] = Field(default=None, alias="campaignBudget")
    campaign_kpis: Dict = Field(default_factory=dict, alias="campaignKpis")
    content_guidelines: Dict = Field(default_factory=dict, alias="contentGuidelines")


class ComplianceInfo(BaseModel):
    regulatory_restrictions: list[str] = Field(default_factory=list, alias="regulatoryRestrictions")
    restricted_territories: list[str] = Field(default_factory=list, alias="restrictedTerritories")
    compliance_requirements: list[str] = Field(default_factory=list, alias="complianceRequirements")


class TeamInfo(BaseModel):
    team_members: List[Dict] = Field(default_factory=list, alias="teamMembers")
    project_history: Optional[str] = Field(default=None, alias="projectHistory")
    project_roadmap: Dict = Field(default_factory=dict, alias="projectRoadmap")
    previous_campaigns: List[Dict] = Field(default_factory=list, alias="previousCampaigns")


class ContentAssets(BaseModel):
    brand_guidelines: Dict = Field(default_factory=dict, alias="brandGuidelines")
    content_themes: list[str] = Field(default_factory=list, alias="contentThemes")
    approved_hashtags: list[str] = Field(default_factory=list, alias="approvedHashtags")
    approved_media_assets: list[HttpUrl] = Field(default_factory=list, alias="approvedMediaAssets")
    content_calendar: Dict = Field(default_factory=dict, alias="contentCalendar")


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
    project_twitter_handle: Optional[str] = Field(default=None, alias="projectTwitterHandle")
    project_telegram_handle: Optional[str] = Field(default=None, alias="projectTelegramHandle")
    project_discord_handle: Optional[str] = Field(default=None, alias="projectDiscordHandle")

    # Project Assets
    project_logo: Optional[HttpUrl] = Field(default=None, alias="projectLogo")
    project_banner: Optional[HttpUrl] = Field(default=None, alias="projectBanner")
    project_whitepaper: Optional[HttpUrl] = Field(default=None, alias="projectWhitepaper")

    # Extended Information
    tokenomics: Optional[TokenomicsInfo] = None
    technical_info: Optional[TechnicalInfo] = Field(default=None, alias="technicalInfo")
    market_info: Optional[MarketInfo] = Field(default=None, alias="marketInfo")
    community_metrics: Optional[CommunityMetrics] = Field(default=None, alias="communityMetrics")
    campaign_specifics: Optional[CampaignSpecifics] = Field(default=None, alias="campaignSpecifics")
    compliance_info: Optional[ComplianceInfo] = Field(default=None, alias="complianceInfo")
    team_info: Optional[TeamInfo] = Field(default=None, alias="teamInfo")
    content_assets: Optional[ContentAssets] = Field(default=None, alias="contentAssets")

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

    model_config = SettingsConfigDict(populate_by_name=True)
