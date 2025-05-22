from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from sqlalchemy import ForeignKey, UniqueConstraint, Column, String, Float, Boolean, Integer, DateTime, Enum as SQLEnum, Text, Numeric
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from datetime import datetime
from utils.pure_funcs import get_now
from services.database import Base
from sqlalchemy.ext.declarative import declarative_base
from decimal import Decimal


class SocialPost(Base):
    """Model for social media posts"""
    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    platform_type: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    post_stage: Mapped[str] = mapped_column(String)
    post_style: Mapped[str] = mapped_column(String)
    post_type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="draft")
    scheduled_time: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    embeddings: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=True)
    engagement_metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
    post_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    campaign = relationship("Campaign", back_populates="posts")


class TestVariant(Base):
    """Model for A/B test variants"""
    __tablename__ = "test_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[str] = mapped_column(String, unique=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    parameters: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sample_size: Mapped[int] = mapped_column(Integer, default=100)
    current_sample: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    campaign = relationship("Campaign", back_populates="test_variants")
    test_results = relationship("TestResult", back_populates="variant")


class TestResult(Base):
    """Model for A/B test results"""
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("test_variants.variant_id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    roi: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_level: Mapped[float] = mapped_column(Float, default=0.0)
    is_significant: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)

    # Relationships
    variant = relationship("TestVariant", back_populates="test_results")
    campaign = relationship("Campaign", back_populates="test_results")


class BudgetAllocation(Base):
    """Model for budget allocation strategy"""
    __tablename__ = "budget_allocations"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    platform: Mapped[str] = mapped_column(String)
    percentage: Mapped[float] = mapped_column(Float)
    daily_budget: Mapped[float] = mapped_column(Float)
    max_cpc: Mapped[float] = mapped_column(Float)
    target_roi: Mapped[float] = mapped_column(Float)
    current_spend: Mapped[float] = mapped_column(Float, default=0.0)
    current_roi: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="budget_allocations")


class EngagementPattern(Base):
    """Model for storing successful engagement patterns"""
    __tablename__ = "engagement_patterns"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    pattern_type: Mapped[str] = mapped_column(String)  # stage, style, content_type
    pattern_value: Mapped[str] = mapped_column(String)
    success_rate: Mapped[float] = mapped_column(Float)
    sample_size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="engagement_patterns")

    __table_args__ = (
        UniqueConstraint('campaign_id', 'pattern_type', 'pattern_value', name='uq_pattern'),
    )


class PostAnalytics(Base):
    """Model for post analytics"""
    __tablename__ = "post_analytics"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("social_posts.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    platform_type: Mapped[str] = mapped_column(String)
    total_engagement: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    virality_score: Mapped[float] = mapped_column(Float, default=0.0)
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    best_performing_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    audience_demographics: Mapped[dict] = mapped_column(JSON, default=dict)
    content_performance: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    post = relationship("SocialPost", back_populates="analytics")
    campaign = relationship("Campaign", back_populates="post_analytics")


class PostRecommendation(Base):
    """Model for post recommendations"""
    __tablename__ = "post_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("social_posts.id"))
    suggested_improvements: Mapped[list[str]] = mapped_column(ARRAY(String))
    audience_insights: Mapped[dict] = mapped_column(JSON, default=dict)
    content_suggestions: Mapped[list[str]] = mapped_column(ARRAY(String))
    timing_recommendations: Mapped[dict] = mapped_column(JSON, default=dict)
    engagement_predictions: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_now)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    post = relationship("SocialPost", back_populates="recommendations")


class PostPerformance(Base):
    """Model for storing post performance data"""
    __tablename__ = "post_performance"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    platform_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    post_stage = Column(String, nullable=False)
    post_style = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    engagement_metrics = Column(JSON, nullable=False)
    embeddings = Column(JSON)
    virality_score = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    sentiment_score = Column(Float, default=0.0)

    # Relationships
    post = relationship("SocialPost", back_populates="performance")
    campaign = relationship("Campaign", back_populates="post_performances")

    def __repr__(self):
        return f"<PostPerformance(id={self.id}, post_id={self.post_id}, virality_score={self.virality_score})>"
