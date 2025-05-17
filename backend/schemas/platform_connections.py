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
