from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic_settings import SettingsConfigDict


class Timezone(str, Enum):
    UTC = "UTC"
    LAGOS = "Africa/Lagos"
    NEW_YORK = "America/New_York"
    CHICAGO = "America/Chicago"
    DENVER = "America/Denver"
    LOS_ANGELES = "America/Los_Angeles"
    LONDON = "Europe/London"
    TOKYO = "Asia/Tokyo"


class Continent(str, Enum):
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    EUROPE = "Europe"
    ASIA = "Asia"
    AFRICA = "Africa"
    AUSTRALIA = "Australia"


class Language(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    CHINESE = "zh"
    KOREAN = "ko"
    JAPANESE = "ja"


class DateFormat(str, Enum):
    MM_DD_YYYY = "MM/DD/YYYY"
    DD_MM_YYYY = "DD/MM/YYYY"
    YYYY_MM_DD = "YYYY-MM-DD"


class TimeFormat(str, Enum):
    TWELVE_HOUR = "12h"
    TWENTY_FOUR_HOUR = "24h"


class LanguageStyle(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    MIXED = "mixed"


class Persona(str, Enum):
    NEUTRAL = "neutral"
    DEGEN = "degen"
    HYPE = "hype"
    MEMELORD = "memelord"


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

    model_config = SettingsConfigDict(populate_by_name=True)


class AlertThresholds(BaseModel):
    engagement_rate: float = Field(default=0.02, ge=0, le=1, alias="engagementRate")
    sentiment_score: float = Field(default=0.6, ge=0, le=1, alias="sentimentScore")
    response_time: int = Field(default=30, ge=1, le=1440, alias="responseTime")  # in minutes, max 24 hours

    model_config = SettingsConfigDict(populate_by_name=True)


class RateLimits(BaseModel):
    posts_per_day: int = Field(default=5, ge=1, le=100, alias="postsPerDay")
    replies_per_day: int = Field(default=20, ge=1, le=200, alias="repliesPerDay")
    likes_per_day: int = Field(default=50, ge=1, le=500, alias="likesPerDay")

    model_config = SettingsConfigDict(populate_by_name=True)


class FieldUpdate(BaseModel):
    """Base class for all field updates with common validation logic"""
    field_name: str = Field(alias="fieldName")
    value: Union[str, int, float, bool, list, dict]

    @field_validator('field_name')
    def validate_field_name(cls, v):
        valid_fields = {
            # Basic settings
            'content_filtering': bool,
            'meme_generation': bool,
            'sentiment_analysis': bool,
            'content_approval_required': bool,
            'max_daily_posts': int,
            'min_time_between_posts': int,

            # Language settings
            'language_style': str,
            'persona': str,
            'emoji_usage': str,
            'hashtag_usage': str,
            'max_hashtags_per_post': int,

            # Platform settings
            'platform_settings': dict,
            'cross_posting': bool,
            'platform_rotation': bool,

            # Engagement settings
            'auto_reply': bool,
            'reply_to_mentions': bool,
            'engage_with_comments': bool,
            'max_daily_replies': int,
            'engagement_hours': dict,

            # Community settings
            'community_guidelines': dict,
            'blocked_users': list,
            'blocked_keywords': list,
            'auto_moderation': bool,
            'spam_detection': bool,

            # Analytics settings
            'tracking_enabled': bool,
            'analytics_granularity': str,
            'performance_alerts': bool,
            'alert_thresholds': dict,

            # AI settings
            'ai_creativity_level': float,
            'ai_response_speed': str,
            'ai_memory_retention': int,
            'ai_learning_enabled': bool,

            # Internationalization settings
            'origin_timezone': str,
            'origin_continent': str,
            'primary_language': str,
            'date_format': str,
            'time_format': str,
            'holiday_awareness': bool,

            # Risk settings
            'risk_level': str,
            'compliance_check_level': str,
            'content_backup_enabled': bool,
            'emergency_stop_enabled': bool,

            # Rate limiting
            'rate_limiting_enabled': bool,
            'rate_limits': dict,
        }
        if v not in valid_fields:
            raise ValueError(f"Invalid field name. Must be one of: {', '.join(valid_fields.keys())}")
        return v

    @field_validator('value')
    def validate_value(cls, v, info):
        field_name = info.data.get('field_name')

        validation_rules = {
            'max_daily_posts': lambda x: isinstance(x, int) and 1 <= x <= 100,
            'min_time_between_posts': lambda x: isinstance(x, int) and 5 <= x <= 1440,
            'max_hashtags_per_post': lambda x: isinstance(x, int) and 0 <= x <= 30,
            'max_daily_replies': lambda x: isinstance(x, int) and 0 <= x <= 500,
            'ai_creativity_level': lambda x: isinstance(x, float) and 0.0 <= x <= 1.0,
            'ai_memory_retention': lambda x: isinstance(x, int) and 1 <= x <= 30,
            'language_style': lambda x: x in LanguageStyle.__members__.values(),
            'persona': lambda x: x in Persona.__members__.values(),
            'emoji_usage': lambda x: x in UsageLevel.__members__.values(),
            'hashtag_usage': lambda x: x in UsageLevel.__members__.values(),
            'analytics_granularity': lambda x: x in AnalyticsGranularity.__members__.values(),
            'ai_response_speed': lambda x: x in AIResponseSpeed.__members__.values(),
            'risk_level': lambda x: x in RiskLevel.__members__.values(),
            'compliance_check_level': lambda x: x in ComplianceLevel.__members__.values(),
            'origin_timezone': lambda x: x in Timezone.__members__.values(),
            'origin_continent': lambda x: x in Continent.__members__.values(),
            'primary_language': lambda x: x in Language.__members__.values(),
            'date_format': lambda x: x in DateFormat.__members__.values(),
            'time_format': lambda x: x in TimeFormat.__members__.values(),
            'holiday_awareness': lambda x: isinstance(x, bool),
        }

        validator = validation_rules.get(field_name)
        if validator and not validator(v):
            raise ValueError(f"Invalid value for field {field_name}")

        return v


class CampaignSettings(BaseModel):
    """Full campaign settings schema"""
    id: int
    campaign_id: int = Field(alias="campaignId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    # Content Generation Settings
    content_filtering: bool = Field(default=False, alias="contentFiltering")
    meme_generation: bool = Field(default=False, alias="memeGeneration")
    sentiment_analysis: bool = Field(default=False, alias="sentimentAnalysis")
    content_approval_required: bool = Field(default=False, alias="contentApprovalRequired")
    max_daily_posts: int = Field(default=10, ge=1, le=100, alias="maxDailyPosts")
    min_time_between_posts: int = Field(default=30, ge=5, le=1440, alias="minTimeBetweenPosts")

    # Language Settings
    language_style: LanguageStyle = Field(default=LanguageStyle.PROFESSIONAL, alias="languageStyle")
    persona: Persona = Field(default=Persona.NEUTRAL, alias="persona")
    emoji_usage: UsageLevel = Field(default=UsageLevel.MODERATE, alias="emojiUsage")
    hashtag_usage: UsageLevel = Field(default=UsageLevel.MODERATE, alias="hashtagUsage")
    max_hashtags_per_post: int = Field(default=2, ge=0, le=30, alias="maxHashtagsPerPost")

    # Platform-specific Settings
    platform_settings: Dict = Field(default_factory=dict, alias="platformSettings")
    cross_posting: bool = Field(default=True, alias="crossPosting")
    platform_rotation: bool = Field(default=True, alias="platformRotation")

    # Engagement Settings
    auto_reply: bool = Field(default=False, alias="autoReply")
    reply_to_mentions: bool = Field(default=False, alias="replyToMentions")
    engage_with_comments: bool = Field(default=False, alias="engageWithComments")
    max_daily_replies: int = Field(default=50, ge=0, le=500, alias="maxDailyReplies")
    engagement_hours: EngagementHours = Field(
        default_factory=lambda: EngagementHours(start="09:00", end="21:00", timezone="UTC"), alias="engagementHours"
    )

    # Community Management
    community_guidelines: Dict = Field(default_factory=dict, alias="communityGuidelines")
    blocked_users: List[str] = Field(default_factory=list, alias="blockedUsers")
    blocked_keywords: List[str] = Field(default_factory=list, alias="blockedKeywords")
    auto_moderation: bool = Field(default=False, alias="autoModeration")
    spam_detection: bool = Field(default=False, alias="spamDetection")

    # Analytics & Reporting
    tracking_enabled: bool = Field(default=False, alias="trackingEnabled")
    analytics_granularity: AnalyticsGranularity = Field(default=AnalyticsGranularity.HOURLY, alias="analyticsGranularity")
    performance_alerts: bool = Field(default=False, alias="performanceAlerts")
    alert_thresholds: AlertThresholds = Field(
        default_factory=lambda: AlertThresholds(
            engagement_rate=0.02,
            sentiment_score=0.6,
            response_time=30
        ), alias="alertThresholds"
    )

    # AI Behavior Settings
    ai_creativity_level: float = Field(default=0.7, ge=0, le=1, alias="aiCreativityLevel")
    ai_response_speed: AIResponseSpeed = Field(default=AIResponseSpeed.BALANCED, alias="aiResponseSpeed")
    ai_memory_retention: int = Field(default=7, ge=1, le=30, alias="aiMemoryRetention")
    ai_learning_enabled: bool = Field(default=False, alias="aiLearningEnabled")

    # Internationalization Settings
    origin_timezone: str = Field(default="UTC", alias="originTimezone")
    origin_continent: str = Field(default="Europe", alias="originContinent")
    primary_language: str = Field(default="en", alias="primaryLanguage")
    date_format: str = Field(default="MM/DD/YYYY", alias="dateFormat")
    time_format: str = Field(default="HH:mm", alias="timeFormat")
    holiday_awareness: bool = Field(default=True, alias="holidayAwareness")

    # Risk Management
    risk_level: RiskLevel = Field(default=RiskLevel.MODERATE, alias="riskLevel")
    compliance_check_level: ComplianceLevel = Field(default=ComplianceLevel.STRICT, alias="complianceCheckLevel")
    content_backup_enabled: bool = Field(default=True, alias="contentBackupEnabled")
    emergency_stop_enabled: bool = Field(default=False, alias="emergencyStopEnabled")

    # Rate Limiting
    rate_limiting_enabled: bool = Field(default=True, alias="rateLimitingEnabled")
    rate_limits: RateLimits = Field(
        default_factory=lambda: RateLimits(
            posts_per_day=11,
            replies_per_day=21,
            likes_per_day=43
        ), alias="rateLimits"
    )

    model_config = SettingsConfigDict(populate_by_name=True)
