from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, JSON, DateTime, func, UniqueConstraint
from services.database import Base
from .workspace import Workspace


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
