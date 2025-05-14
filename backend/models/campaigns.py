from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from sqlalchemy import ForeignKey, UniqueConstraint, Column, String
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from datetime import datetime
from utils.pure_funcs import get_now
from services.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    campaign_name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="PENDING")
    campaign_type:  Mapped[str] = mapped_column(nullable=False)
    target_platforms: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    campaign_goals: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    engagement_style: Mapped[str] = mapped_column(nullable=False)
    target_audience: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    campaign_start_date: Mapped[datetime] = mapped_column(nullable=False)
    campaign_timeline: Mapped[str] = mapped_column(nullable=False)

    project_name: Mapped[str] = mapped_column(nullable=False)
    project_info:  Mapped[str] = mapped_column(nullable=False)
    project_website: Mapped[str] = mapped_column(nullable=True)
    project_twitter: Mapped[str] = mapped_column(nullable=True)
    project_telegram: Mapped[str] = mapped_column(nullable=True)
    project_discord: Mapped[str] = mapped_column(nullable=True)
    project_logo: Mapped[str] = mapped_column(nullable=True)
    project_banner: Mapped[str] = mapped_column(nullable=True)
    project_whitepaper: Mapped[str] = mapped_column(nullable=True)
    project_token_address: Mapped[str] = mapped_column(nullable=True)
    project_token_symbol: Mapped[str] = mapped_column(nullable=True)
    project_token_decimals: Mapped[int] = mapped_column(nullable=True)
    project_token_supply: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=get_now)
    updated_at: Mapped[datetime] = mapped_column(default=get_now, onupdate=get_now)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_paused: Mapped[bool] = mapped_column(default=False)

    # unique_constraints on user+ campaign name
    __table_args__ = (
        UniqueConstraint("workspace_id", "campaign_name", name="unique_workspace_campaign_name"),
    )


class CampaignSettings(Base):
    __tablename__ = "campaign_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, unique=True)
    content_filtering: Mapped[bool] = mapped_column(default=False)
    meme_generation: Mapped[bool] = mapped_column(default=False)
