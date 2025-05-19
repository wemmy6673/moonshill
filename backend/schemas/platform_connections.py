from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Literal
from datetime import datetime
from enum import Enum
from pydantic_settings import SettingsConfigDict


class PlatformType(str, Enum):
    TWITTER = "twitter"
    TELEGRAM = "telegram"
    DISCORD = "discord"


class ConnectionStatus(BaseModel):
    is_connected: bool = Field(alias="isConnected")
    platform_username: Optional[str] = Field(default=None, alias="platformUsername")
    connected_at: Optional[datetime] = Field(default=None, alias="connectedAt")
    platform_metadata: Optional[Dict] = Field(default=None, alias="platformMetadata")
    campaign_id: int = Field(alias="campaignId")

    model_config = SettingsConfigDict(populate_by_name=True)


class ConnectionRequest(BaseModel):
    platform: PlatformType
    callback_url: HttpUrl = Field(alias="callbackUrl")
    campaign_id: int = Field(alias="campaignId")

    model_config = SettingsConfigDict(populate_by_name=True)


class ConnectionResponse(BaseModel):
    auth_url: HttpUrl = Field(alias="authUrl")
    platform: PlatformType
    campaign_id: int = Field(alias="campaignId")

    model_config = SettingsConfigDict(populate_by_name=True)


class ConnectionCallback(BaseModel):
    platform: PlatformType
    auth_res_url:  HttpUrl = Field(alias="authResUrl")
    state: str  # CSRF token for verification

    model_config = SettingsConfigDict(populate_by_name=True)


class PlatformConnection(BaseModel):
    id: int
    workspace_id: int = Field(alias="workspaceId")
    campaign_id: int = Field(alias="campaignId")
    platform: PlatformType
    is_connected: bool = Field(alias="isConnected")
    platform_username: Optional[str] = Field(default=None, alias="platformUsername")
    connected_at: Optional[datetime] = Field(default=None, alias="connectedAt")
    last_used_at: Optional[datetime] = Field(default=None, alias="lastUsedAt")
    platform_metadata: Optional[Dict] = Field(default=None, alias="platformMetadata")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = SettingsConfigDict(populate_by_name=True)


class CreateBotRequest(BaseModel):
    bot_token: str = Field(alias="botToken")
    bot_name: str = Field(alias="botName")
    bot_username: str = Field(alias="botUsername")
    bot_description: Optional[str] = Field(default=None, alias="botDescription")
    bot_photo_url: Optional[str] = Field(default=None, alias="botPhotoUrl")

    model_config = SettingsConfigDict(populate_by_name=True)


class CreateBotResponse(BaseModel):
    id: int
    bot_token: str = Field(alias="botToken")
    bot_name: str = Field(alias="botName")
    bot_username: str = Field(alias="botUsername")
    bot_description: Optional[str] = Field(default=None, alias="botDescription")
    bot_photo_url: Optional[str] = Field(default=None, alias="botPhotoUrl")
    assigned: bool = Field(alias="assigned")
    assigned_campaign_id: Optional[int] = Field(default=None, alias="assignedCampaignId")
    assigned_workspace_id: Optional[int] = Field(default=None, alias="assignedWorkspaceId")
    last_assigned_at: Optional[datetime] = Field(default=None, alias="lastAssignedAt")
    last_used_at: Optional[datetime] = Field(default=None, alias="lastUsedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = SettingsConfigDict(populate_by_name=True)
