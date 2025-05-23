from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class GenerationError(Exception):
    """Base exception for generation errors"""
    pass


class LLMProviderError(GenerationError):
    """Exception for LLM provider specific errors"""
    pass


class DatabaseError(GenerationError):
    """Exception for database related errors"""
    pass


class ValidationError(GenerationError):
    """Exception for validation errors"""
    pass


class BudgetError(GenerationError):
    """Exception for budget related errors"""
    pass


class TestError(GenerationError):
    """Exception for A/B testing related errors"""
    pass


class DeviceType(str, Enum):
    """Types of devices for social media posts"""
    MOBILE = "mobile"
    DESKTOP = "desktop"


class PlatformType(str, Enum):
    """Supported social media platforms"""
    TWITTER = "twitter"
    TELEGRAM = "telegram"
    DISCORD = "discord"


class PostStage(str, Enum):
    """Stages of a social media post in the campaign lifecycle"""
    INTRO = "intro"  # Introduction to the project
    HYPE = "hype"    # Building excitement
    MEME = "meme"    # Meme-based engagement
    DEEP_DIVE = "deep_dive"  # Technical or detailed content
    CTA = "cta"      # Call to action
    FUD_RESPONSE = "fud_response"  # Addressing concerns
    NEWS = "news"    # News and updates
    ANALYSIS = "analysis"  # Market or technical analysis


class PostStyle(str, Enum):
    """Styling options for social media posts"""
    THREAD = "thread"  # Twitter thread format
    MEME = "meme"      # Meme-based content
    QUESTION = "question"  # Question-based engagement
    FUD_RESPONSE = "fud_response"  # Response to FUD
    NEWS = "news"      # News article style
    ANALYSIS = "analysis"  # Analytical content
    TUTORIAL = "tutorial"  # How-to or educational content
    POLL = "poll"      # Poll or survey
    DISCUSSION = "discussion"  # Discussion starter


class PostType(str, Enum):
    """Types of social media posts"""
    TEXT = "text"  # Plain text post
    IMAGE = "image"  # Image with caption
    VIDEO = "video"  # Video content
    ARTICLE = "article"  # Long-form article
    THREAD = "thread"  # Thread of posts
    POLL = "poll"  # Poll or survey
    LINK = "link"  # Shared link
    MIXED = "mixed"  # Mixed media content


class PostStatus(str, Enum):
    """Status of a social media post"""
    DRAFT = "draft"  # Post is in draft
    SCHEDULED = "scheduled"  # Post is scheduled
    PUBLISHED = "published"  # Post has been published
    FAILED = "failed"  # Post failed to publish
    DELETED = "deleted"  # Post was deleted
    ARCHIVED = "archived"  # Post is archived


class PersonaType(str, Enum):
    DEGEN = "degen"
    HYPE_MAN = "hype_man"
    ANALYST = "analyst"
    MEME_LORD = "meme_lord"
    NEUTRAL = "neutral"


class PostStrategyGoal(str, Enum):
    AWARENESS = "awareness"
    FOMO = "fomo"
    RE_ENGAGEMENT = "re_engagement"
    CALL_TO_ACTION = "call_to_action"


class CampaignPhase(str, Enum):
    EARLY = "early"
    MID = "mid"
    LATE = "late"


class MessageHistory(BaseModel):
    """Model for storing message history"""
    id: int
    campaign_id: int
    platform_type: PlatformType
    message: str
    stage: PostStage
    style: PostStyle
    created_at: datetime
    engagement_metrics: Optional[Dict[str, Any]] = None
    embeddings: Optional[List[float]] = None


class PromptComponent(BaseModel):
    """Base class for prompt components"""
    content: str
    weight: float = 1.0


class PersonaPrompt(PromptComponent):
    """Persona component of the prompt"""
    persona_type: PersonaType
    tone_guidelines: Optional[str] = None
    emoji_usage: Optional[str] = None


class ProjectInfoPrompt(PromptComponent):
    """Project information component of the prompt"""
    project_name: str
    project_info: str
    tokenomics: Optional[Dict] = None
    technical_info: Optional[Dict] = None
    market_info: Optional[Dict] = None


class PlatformPrompt(PromptComponent):
    """Platform-specific component of the prompt"""
    platform_type: PlatformType
    platform_settings: Optional[Dict] = None


class TrendingHooksPrompt(PromptComponent):
    """Trending hooks component of the prompt"""
    trending_topics: List[str]
    relevant_hashtags: List[str]


class StrategyPrompt(PromptComponent):
    """Strategy component of the prompt"""
    goal: PostStrategyGoal
    campaign_phase: CampaignPhase
    key_messages: List[str]


class EngagementMetrics(BaseModel):
    """Metrics for post engagement"""
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    clicks: int = 0
    sentiment_score: float = 0.0
    engagement_rate: float = 0.0
    virality_score: float = 0.0
    platform_specific_metrics: Dict[str, Any] = Field(default_factory=dict)


class SocialPost(BaseModel):
    """Model for social media posts"""
    id: int
    campaign_id: int
    platform_type: str
    content: str
    post_stage: str
    post_style: str
    post_type: str
    status: str = "draft"
    scheduled_time: datetime
    created_at: datetime
    last_updated: Optional[datetime] = None
    published_at: Optional[datetime] = None
    embeddings: Optional[List[float]] = None
    engagement_metrics: Optional[Dict[str, Any]] = None
    post_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class PostAnalytics(BaseModel):
    """Analytics for social media posts"""
    post_id: int
    campaign_id: int
    platform_type: PlatformType
    total_engagement: int
    engagement_rate: float
    virality_score: float
    sentiment_score: float
    best_performing_time: Optional[datetime] = None
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)
    content_performance: Dict[str, float] = Field(default_factory=dict)


class PostRecommendation(BaseModel):
    """Recommendations for post optimization"""
    post_id: int
    suggested_improvements: List[str]
    audience_insights: Dict[str, Any]
    content_suggestions: List[str]
    timing_recommendations: Dict[str, Any]
    engagement_predictions: Dict[str, float]


class TestVariant(BaseModel):
    """Model for A/B test variants"""
    variant_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    created_at: datetime
    is_active: bool = True
    sample_size: int = 100
    current_sample: int = 0


class TestResult(BaseModel):
    """Model for A/B test results"""
    variant_id: str
    campaign_id: int
    impressions: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue: Decimal = Decimal('0.0')
    cost: Decimal = Decimal('0.0')
    roi: float = 0.0
    confidence_level: float = 0.0
    is_significant: bool = False


class BudgetAllocation(BaseModel):
    """Model for budget allocation strategy"""
    platform: PlatformType
    percentage: float
    daily_budget: Decimal
    max_cpc: Decimal
    target_roi: float
    current_spend: Decimal = Decimal('0.0')
    current_roi: float = 0.0


class PlatformError(GenerationError):
    """Exception for platform-specific errors"""
    pass


class SchedulingError(GenerationError):
    """Exception for post scheduling errors"""
    pass
