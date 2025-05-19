from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, JSON, DateTime, func, UniqueConstraint, Boolean, ARRAY, Integer
from services.database import Base
from .campaigns import Campaign


class PlatformConnection(Base):
    __tablename__ = "platform_connections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)  # 'twitter', 'telegram', 'discord'
    nonce: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String, nullable=False)

    # Connection status
    is_connected: Mapped[bool] = mapped_column(default=False)
    connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Platform-specific data (encrypted in production)
    platform_user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    platform_username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    access_token_secret: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For Twitter
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For Discord
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Additional platform-specific metadata
    platform_metadata: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("workspace_id", "campaign_id", "platform", "nonce", name="unique_workspace_campaign_platform_nonce"),
    )

    def __repr__(self) -> str:
        return f"<PlatformConnection(id={self.id}, platform={self.platform}, workspace_id={self.workspace_id}, campaign_id={self.campaign_id})>"


class ManagedTelegramBot(Base):
    __tablename__ = "managed_telegram_bots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bot_token: Mapped[str] = mapped_column(String, nullable=False)
    bot_username: Mapped[str] = mapped_column(String, nullable=False)
    bot_name: Mapped[str] = mapped_column(String, nullable=False)
    bot_description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bot_photo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Bot assignment
    connected_campaigns: Mapped[List["Campaign"]] = relationship(back_populates="managed_telegram_bot", passive_deletes=True)

    last_assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Bot limits
    max_campaigns: Mapped[int] = mapped_column(default=50)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_exclusive: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_token_refresh: Mapped[bool] = mapped_column(Boolean, default=False)
    token_refresh_required_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("bot_token", "bot_username", name="unique_bot_token_username"),
    )

    def __repr__(self) -> str:
        return f"<ManagedTelegramBot(id={self.id}, bot_username={self.bot_username}, bot_name={self.bot_name})>"
