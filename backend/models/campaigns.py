from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from sqlalchemy import ForeignKey, UniqueConstraint, Column, String, Float, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from datetime import datetime
from utils.pure_funcs import get_now
from services.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    # Basic Info
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    campaign_name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="PENDING")
    campaign_type: Mapped[str] = mapped_column(nullable=False)
    target_platforms: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    campaign_goals: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    engagement_style: Mapped[str] = mapped_column(nullable=False)
    target_audience: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    campaign_start_date: Mapped[datetime] = mapped_column(nullable=False)
    campaign_timeline: Mapped[str] = mapped_column(nullable=False)

    # Project Basic Info
    project_name: Mapped[str] = mapped_column(nullable=False)
    project_info: Mapped[str] = mapped_column(nullable=False)
    project_website: Mapped[str] = mapped_column(nullable=True)
    project_twitter: Mapped[str] = mapped_column(nullable=True)
    project_telegram: Mapped[str] = mapped_column(nullable=True)
    project_discord: Mapped[str] = mapped_column(nullable=True)
    project_logo: Mapped[str] = mapped_column(nullable=True)
    project_banner: Mapped[str] = mapped_column(nullable=True)
    project_whitepaper: Mapped[str] = mapped_column(nullable=True)

    # Tokenomics
    project_token_address: Mapped[str] = mapped_column(nullable=True)
    project_token_symbol: Mapped[str] = mapped_column(nullable=True)
    project_token_decimals: Mapped[int] = mapped_column(nullable=True)
    project_token_supply: Mapped[float] = mapped_column(nullable=True)
    project_token_initial_price: Mapped[float] = mapped_column(nullable=True)
    project_token_current_price: Mapped[float] = mapped_column(nullable=True)
    project_market_cap: Mapped[float] = mapped_column(nullable=True)
    project_circulating_supply: Mapped[float] = mapped_column(nullable=True)
    token_distribution: Mapped[dict] = mapped_column(JSON, nullable=True)
    vesting_schedule: Mapped[dict] = mapped_column(JSON, nullable=True)
    token_launch_date: Mapped[datetime] = mapped_column(nullable=True)

    # Technical Info
    blockchain_networks: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    smart_contract_features: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    technology_stack: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    github_repository: Mapped[str] = mapped_column(nullable=True)
    audit_reports: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    # Market Info
    target_markets: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    competitor_analysis: Mapped[dict] = mapped_column(JSON, nullable=True)
    unique_selling_points: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    market_positioning: Mapped[str] = mapped_column(nullable=True)

    # Community Metrics
    community_size: Mapped[dict] = mapped_column(JSON, nullable=True)
    growth_rate: Mapped[dict] = mapped_column(JSON, nullable=True)
    engagement_rate: Mapped[dict] = mapped_column(JSON, nullable=True)
    influencer_partnerships: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Campaign Specifics
    key_messages: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    prohibited_terms: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    tone_guidelines: Mapped[str] = mapped_column(nullable=True)
    campaign_budget: Mapped[float] = mapped_column(nullable=True)
    campaign_kpis: Mapped[dict] = mapped_column(JSON, nullable=True)
    content_guidelines: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Compliance Info
    regulatory_restrictions: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    restricted_territories: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    compliance_requirements: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    # Team Info
    team_members: Mapped[dict] = mapped_column(JSON, nullable=True)
    project_history: Mapped[str] = mapped_column(nullable=True)
    project_roadmap: Mapped[dict] = mapped_column(JSON, nullable=True)
    previous_campaigns: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Content Assets
    brand_guidelines: Mapped[dict] = mapped_column(JSON, nullable=True)
    content_themes: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    approved_hashtags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    approved_media_assets: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    content_calendar: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=get_now)
    updated_at: Mapped[datetime] = mapped_column(default=get_now, onupdate=get_now)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_paused: Mapped[bool] = mapped_column(default=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="campaigns")
    settings = relationship("CampaignSettings", back_populates="campaign", uselist=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("workspace_id", "campaign_name", name="unique_workspace_campaign_name"),
    )


class CampaignSettings(Base):
    __tablename__ = "campaign_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, unique=True)

    # Content Generation Settings
    content_filtering: Mapped[bool] = mapped_column(default=False)
    meme_generation: Mapped[bool] = mapped_column(default=False)
    sentiment_analysis: Mapped[bool] = mapped_column(default=False)
    content_approval_required: Mapped[bool] = mapped_column(default=False)
    max_daily_posts: Mapped[int] = mapped_column(default=10)
    min_time_between_posts: Mapped[int] = mapped_column(default=30)  # minutes

    # Language Settings
    language_style: Mapped[str] = mapped_column(default="professional")  # professional, casual, mixed
    emoji_usage: Mapped[str] = mapped_column(default="moderate")  # none, minimal, moderate, heavy
    hashtag_usage: Mapped[str] = mapped_column(default="moderate")  # none, minimal, moderate, heavy
    max_hashtags_per_post: Mapped[int] = mapped_column(default=2)

    # Platform-specific Settings
    platform_settings: Mapped[dict] = mapped_column(JSON, default={})  # Settings per platform
    cross_posting: Mapped[bool] = mapped_column(default=True)
    platform_rotation: Mapped[bool] = mapped_column(default=True)

    # Engagement Settings
    auto_reply: Mapped[bool] = mapped_column(default=False)
    reply_to_mentions: Mapped[bool] = mapped_column(default=False)
    engage_with_comments: Mapped[bool] = mapped_column(default=False)
    max_daily_replies: Mapped[int] = mapped_column(default=50)
    engagement_hours: Mapped[dict] = mapped_column(JSON, default={
        "start": "09:00",
        "end": "21:00",
        "timezone": "UTC"
    })

    # Community Management
    community_guidelines: Mapped[dict] = mapped_column(JSON, default={})
    blocked_users: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    blocked_keywords: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    auto_moderation: Mapped[bool] = mapped_column(default=False)
    spam_detection: Mapped[bool] = mapped_column(default=False)

    # Analytics & Reporting
    tracking_enabled: Mapped[bool] = mapped_column(default=False)
    analytics_granularity: Mapped[str] = mapped_column(default="hourly")  # hourly, daily, weekly
    performance_alerts: Mapped[bool] = mapped_column(default=False)
    alert_thresholds: Mapped[dict] = mapped_column(JSON, default={
        "engagement_rate": 0.02,
        "sentiment_score": 0.6,
        "response_time": 30  # minutes
    })

    # AI Behavior Settings
    ai_creativity_level: Mapped[float] = mapped_column(default=0.7)  # 0.0 to 1.0
    ai_response_speed: Mapped[str] = mapped_column(default="balanced")  # fast, balanced, thorough
    ai_memory_retention: Mapped[int] = mapped_column(default=7)  # days to remember context
    ai_learning_enabled: Mapped[bool] = mapped_column(default=False)

    # Risk Management
    risk_level: Mapped[str] = mapped_column(default="moderate")  # conservative, moderate, aggressive
    compliance_check_level: Mapped[str] = mapped_column(default="strict")  # basic, moderate, strict
    content_backup_enabled: Mapped[bool] = mapped_column(default=True)
    emergency_stop_enabled: Mapped[bool] = mapped_column(default=False)

    # Rate Limiting
    rate_limiting_enabled: Mapped[bool] = mapped_column(default=True)
    rate_limits: Mapped[dict] = mapped_column(JSON, default={
        "posts_per_hour": 5,
        "replies_per_hour": 20,
        "likes_per_hour": 50
    })

    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=get_now)
    updated_at: Mapped[datetime] = mapped_column(default=get_now, onupdate=get_now)
    last_optimized_at: Mapped[datetime] = mapped_column(nullable=True)

    # Relationship
    campaign = relationship("Campaign", back_populates="settings")
