from pydantic import BaseModel, Field, field_validator, ValidationError, EmailStr, HttpUrl
from pydantic_settings import SettingsConfigDict
from datetime import datetime
from eth_utils import is_address
from typing import Optional
from .enums import CampaignType, TargetPlatform, EngagementStyle, TargetAudience, CampaignGoal, CampaignTimeline, CampaignStatus


class CreateCampaign(BaseModel):
    campaign_name: str = Field(min_length=3, max_length=128, alias="campaignName")
    campaign_type: CampaignType = Field(alias="campaignType")
    target_platforms: list[TargetPlatform] = Field(alias="targetPlatforms")
    engagement_style: EngagementStyle = Field(alias="engagementStyle")
    campaign_start_date: datetime = Field(alias="campaignStartDate")
    campaign_timeline: CampaignTimeline = Field(alias="campaignTimeline")

    # project information
    project_name: str = Field(min_length=3, max_length=128, alias="projectName")
    project_info: str = Field(alias="projectInfo")
    target_audience: list[TargetAudience] = Field(alias="targetAudience", min_length=1, )
    campaign_goals: list[CampaignGoal] = Field(alias="campaignGoals", min_length=1, )
    project_website: Optional[HttpUrl] = Field(default=None, alias="projectWebsite")
    project_twitter_handle: Optional[str] = Field(default=None, alias="projectTwitterHandle")
    project_telegram_handle: Optional[str] = Field(default=None, alias="projectTelegramHandle")
    project_discord_handle: Optional[str] = Field(default=None, alias="projectDiscordHandle")
    project_logo: Optional[HttpUrl] = Field(default=None, alias="projectLogo")
    project_banner: Optional[HttpUrl] = Field(default=None, alias="projectBanner")
    project_whitepaper: Optional[HttpUrl] = Field(default=None, alias="projectWhitepaper")

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
