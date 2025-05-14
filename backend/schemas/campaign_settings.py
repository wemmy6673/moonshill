from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class LanguageStyle(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    MIXED = "mixed"


class UsageLevel(str, Enum):
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    HEAVY = "heavy"


class AnalyticsGranularity(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class AIResponseSpeed(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    THOROUGH = "thorough"


class RiskLevel(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class ComplianceLevel(str, Enum):
    BASIC = "basic"
    MODERATE = "moderate"
    STRICT = "strict"


class EngagementHours(BaseModel):
    start: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: str = "UTC"


class AlertThresholds(BaseModel):
    engagement_rate: float = Field(0.02, ge=0, le=1)
    sentiment_score: float = Field(0.6, ge=0, le=1)
    response_time: int = Field(30, ge=1, le=1440)  # in minutes, max 24 hours


class RateLimits(BaseModel):
    posts_per_hour: int = Field(5, ge=1, le=100)
    replies_per_hour: int = Field(20, ge=1, le=200)
    likes_per_hour: int = Field(50, ge=1, le=500)


class CreateCampaignSettings(BaseModel):
    # Content Generation Settings
    content_filtering: bool = True
    meme_generation: bool = False
    sentiment_analysis: bool = True
    plagiarism_check: bool = True
    content_approval_required: bool = True
    max_daily_posts: int = Field(10, ge=1, le=100)
    min_time_between_posts: int = Field(30, ge=5, le=1440)  # minutes

    # Language Settings
    language_style: LanguageStyle = LanguageStyle.PROFESSIONAL
    emoji_usage: UsageLevel = UsageLevel.MODERATE
    hashtag_usage: UsageLevel = UsageLevel.MODERATE
    max_hashtags_per_post: int = Field(5, ge=0, le=30)

    # Platform-specific Settings
    platform_settings: Dict = Field(default_factory=dict)
    cross_posting: bool = True
    platform_rotation: bool = True

    # Engagement Settings
    auto_reply: bool = False
    reply_to_mentions: bool = True
    engage_with_comments: bool = True
    max_daily_replies: int = Field(50, ge=0, le=500)
    engagement_hours: EngagementHours = Field(
        default_factory=lambda: EngagementHours(start="09:00", end="21:00", timezone="UTC")
    )

    # Community Management
    community_guidelines: Dict = Field(default_factory=dict)
    blocked_users: List[str] = Field(default_factory=list)
    blocked_keywords: List[str] = Field(default_factory=list)
    auto_moderation: bool = True
    spam_detection: bool = True

    # Analytics & Reporting
    tracking_enabled: bool = True
    analytics_granularity: AnalyticsGranularity = AnalyticsGranularity.HOURLY
    performance_alerts: bool = True
    alert_thresholds: AlertThresholds = Field(
        default_factory=lambda: AlertThresholds(
            engagement_rate=0.02,
            sentiment_score=0.6,
            response_time=30
        )
    )

    # AI Behavior Settings
    ai_creativity_level: float = Field(0.7, ge=0, le=1)
    ai_response_speed: AIResponseSpeed = AIResponseSpeed.BALANCED
    ai_memory_retention: int = Field(7, ge=1, le=30)  # days
    ai_learning_enabled: bool = True

    # Risk Management
    risk_level: RiskLevel = RiskLevel.MODERATE
    compliance_check_level: ComplianceLevel = ComplianceLevel.STRICT
    content_backup_enabled: bool = True
    emergency_stop_enabled: bool = True

    # Rate Limiting
    rate_limiting_enabled: bool = True
    rate_limits: RateLimits = Field(
        default_factory=lambda: RateLimits(
            posts_per_hour=5,
            replies_per_hour=20,
            likes_per_hour=50
        )
    )

    class Config:
        use_enum_values = True


class UpdateCampaignSettings(CreateCampaignSettings):
    pass


class CampaignSettings(CreateCampaignSettings):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime
    last_optimized_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
