from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict
from decimal import Decimal


class BasePydanticModel(BaseModel):
    """Base model with camelCase configuration"""
    model_config = SettingsConfigDict(
        populate_by_name=True
    )


class PricingStrategy(str, Enum):
    """Available pricing strategies"""
    GROWTH = "growth"  # Focus on growth and adoption
    PREMIUM = "premium"  # Focus on premium features and exclusivity
    VALUE = "value"  # Focus on value and ROI


class Feature(BasePydanticModel):
    """Model for pricing tier features"""
    name: str
    description: str
    is_highlighted: bool = Field(default=False, alias="isHighlighted")
    is_limited: bool = Field(default=False, alias="isLimited")
    limit_value: Optional[int] = Field(default=None, alias="limitValue")

    model_config = SettingsConfigDict(
        populate_by_name=True
    )


class PricingTier(BasePydanticModel):
    """Model for pricing tier"""
    name: str
    description: str
    base_price: Decimal = Field(alias="basePrice")
    price: Decimal
    billing_period: str = Field(default="month", alias="billingPeriod")
    features: List[Feature]
    is_popular: bool = Field(default=False, alias="isPopular")
    is_enterprise: bool = Field(default=False, alias="isEnterprise")
    max_campaigns: int = Field(alias="maxCampaigns")
    max_posts_per_day: int = Field(alias="maxPostsPerDay")
    max_platforms: int = Field(alias="maxPlatforms")
    ai_creativity_level: int = Field(default=1, alias="aiCreativityLevel")
    priority_support: bool = Field(default=False, alias="prioritySupport")
    custom_branding: bool = Field(default=False, alias="customBranding")
    analytics_depth: str = Field(default="basic", alias="analyticsDepth")

    model_config = SettingsConfigDict(
        populate_by_name=True
    )

    def adjust_price(self, percentage: float) -> None:
        """Adjust the price by a percentage"""
        adjustment_factor = Decimal(str(1 + (percentage / 100)))
        self.price = (self.base_price * adjustment_factor).quantize(Decimal('0.01'))


class PricingResponse(BasePydanticModel):
    """Response model for pricing endpoint"""
    strategy: str = Field(description="Current pricing strategy (growth, premium, or value)")
    price_adjustment: float = Field(
        default=0.0,
        description="Percentage adjustment applied to prices (-100 to 100)",
        alias="priceAdjustment"
    )
    tiers: Dict[str, PricingTier] = Field(
        description="Dictionary of pricing tiers with their features and limits"
    )

    model_config = SettingsConfigDict(
        populate_by_name=True
    )


# Growth Strategy - Focus on adoption and scaling
GROWTH_TIERS = {
    "starter": PricingTier(
        name="Starter",
        description="Perfect for small projects and testing",
        base_price=Decimal("49.99"),
        price=Decimal("49.99"),
        features=[
            Feature(name="Basic AI Generation", description="Standard AI post generation", is_highlighted=True),
            Feature(name="2 Social Platforms", description="Connect up to 2 social platforms", is_limited=True, limit_value=2),
            Feature(name="3 Campaigns", description="Run up to 3 campaigns", is_limited=True, limit_value=3),
            Feature(name="10 Posts/Day", description="Generate up to 10 posts per day across all platforms", is_limited=True, limit_value=10),
            Feature(name="Basic Analytics", description="Basic engagement metrics"),
        ],
        max_campaigns=3,
        max_posts_per_day=10,
        max_platforms=2,
        ai_creativity_level=1
    ),
    "growth": PricingTier(
        name="Growth",
        description="Ideal for growing communities",
        base_price=Decimal("149.99"),
        price=Decimal("149.99"),
        features=[
            Feature(name="Advanced AI Generation", description="Enhanced AI capabilities", is_highlighted=True),
            Feature(name="5 Social Platforms", description="Connect up to 5 social platforms", is_limited=True, limit_value=5),
            Feature(name="10 Campaigns", description="Run up to 10 campaigns", is_limited=True, limit_value=10),
            Feature(name="50 Posts/Day", description="Generate up to 50 posts per day across all platforms", is_limited=True, limit_value=50),
            Feature(name="Advanced Analytics", description="Detailed engagement metrics"),
            Feature(name="Priority Support", description="Faster response times", is_highlighted=True),
        ],
        is_popular=True,
        max_campaigns=10,
        max_posts_per_day=50,
        max_platforms=5,
        ai_creativity_level=2,
        priority_support=True
    ),
    "scale": PricingTier(
        name="Scale",
        description="For serious community builders",
        base_price=Decimal("499.99"),
        price=Decimal("499.99"),
        features=[
            Feature(name="Premium AI Generation", description="Highest quality AI generation", is_highlighted=True),
            Feature(name="All Platforms", description="Connect all supported platforms"),
            Feature(name="Unlimited Campaigns", description="Run as many campaigns as you need"),
            Feature(name="200 Posts/Day", description="Generate up to 200 posts per day across all platforms", is_limited=True, limit_value=200),
            Feature(name="Enterprise Analytics", description="Advanced analytics and insights"),
            Feature(name="24/7 Priority Support", description="Round-the-clock support", is_highlighted=True),
            Feature(name="Custom Branding", description="White-label solution"),
        ],
        is_enterprise=True,
        max_campaigns=-1,  # Unlimited
        max_posts_per_day=200,
        max_platforms=-1,  # Unlimited
        ai_creativity_level=3,
        priority_support=True,
        custom_branding=True,
        analytics_depth="enterprise"
    )
}

# Premium Strategy - Focus on exclusivity and high-end features
PREMIUM_TIERS = {
    "basic": PricingTier(
        name="Basic",
        description="Essential features for beginners",
        base_price=Decimal("99.99"),
        price=Decimal("99.99"),
        features=[
            Feature(name="Standard AI Generation", description="Basic AI capabilities"),
            Feature(name="3 Social Platforms", description="Connect up to 3 platforms", is_limited=True, limit_value=3),
            Feature(name="3 Campaigns", description="Run up to 3 campaigns", is_limited=True, limit_value=3),
            Feature(name="20 Posts/Day", description="Generate up to 20 posts per day across all platforms", is_limited=True, limit_value=20),
            Feature(name="Basic Analytics", description="Essential metrics"),
        ],
        max_campaigns=3,
        max_posts_per_day=20,
        max_platforms=3,
        ai_creativity_level=1
    ),
    "professional": PricingTier(
        name="Professional",
        description="For serious content creators",
        base_price=Decimal("299.99"),
        price=Decimal("299.99"),
        features=[
            Feature(name="Advanced AI Generation", description="Enhanced AI capabilities", is_highlighted=True),
            Feature(name="All Platforms", description="Connect all supported platforms"),
            Feature(name="15 Campaigns", description="Run up to 15 campaigns", is_limited=True, limit_value=15),
            Feature(name="100 Posts/Day", description="Generate up to 100 posts per day across all platforms", is_limited=True, limit_value=100),
            Feature(name="Advanced Analytics", description="Detailed insights"),
            Feature(name="Priority Support", description="Faster response times", is_highlighted=True),
        ],
        is_popular=True,
        max_campaigns=15,
        max_posts_per_day=100,
        max_platforms=-1,
        ai_creativity_level=2,
        priority_support=True
    ),
    "enterprise": PricingTier(
        name="Enterprise",
        description="For large organizations",
        base_price=Decimal("999.99"),
        price=Decimal("999.99"),
        features=[
            Feature(name="Premium AI Generation", description="Highest quality AI generation", is_highlighted=True),
            Feature(name="Unlimited Everything", description="No limits on any feature"),
            Feature(name="Custom Solutions", description="Tailored to your needs", is_highlighted=True),
            Feature(name="Enterprise Analytics", description="Advanced analytics and insights"),
            Feature(name="24/7 Priority Support", description="Round-the-clock support", is_highlighted=True),
            Feature(name="Custom Branding", description="White-label solution"),
            Feature(name="Dedicated Account Manager", description="Personal support", is_highlighted=True),
        ],
        is_enterprise=True,
        max_campaigns=-1,
        max_posts_per_day=-1,
        max_platforms=-1,
        ai_creativity_level=3,
        priority_support=True,
        custom_branding=True,
        analytics_depth="enterprise"
    )
}

# Value Strategy - Focus on ROI and practical benefits
VALUE_TIERS = {
    "essential": PricingTier(
        name="Essential",
        description="Everything you need to get started",
        base_price=Decimal("79.99"),
        price=Decimal("79.99"),
        features=[
            Feature(name="Smart AI Generation", description="Efficient AI post generation", is_highlighted=True),
            Feature(name="3 Social Platforms", description="Connect up to 3 platforms", is_limited=True, limit_value=3),
            Feature(name="3 Campaigns", description="Run up to 3 campaigns", is_limited=True, limit_value=3),
            Feature(name="30 Posts/Day", description="Generate up to 30 posts per day across all platforms", is_limited=True, limit_value=30),
            Feature(name="Basic Analytics", description="Essential metrics"),
        ],
        max_campaigns=3,
        max_posts_per_day=30,
        max_platforms=3,
        ai_creativity_level=1
    ),
    "business": PricingTier(
        name="Business",
        description="Perfect for growing businesses",
        base_price=Decimal("199.99"),
        price=Decimal("199.99"),
        features=[
            Feature(name="Advanced AI Generation", description="Enhanced AI capabilities", is_highlighted=True),
            Feature(name="All Platforms", description="Connect all supported platforms"),
            Feature(name="15 Campaigns", description="Run up to 15 campaigns", is_limited=True, limit_value=15),
            Feature(name="100 Posts/Day", description="Generate up to 100 posts per day across all platforms", is_limited=True, limit_value=100),
            Feature(name="Advanced Analytics", description="Detailed insights"),
            Feature(name="Priority Support", description="Faster response times", is_highlighted=True),
        ],
        is_popular=True,
        max_campaigns=15,
        max_posts_per_day=100,
        max_platforms=-1,
        ai_creativity_level=2,
        priority_support=True
    ),
    "premium": PricingTier(
        name="Premium",
        description="Maximum value for serious users",
        base_price=Decimal("399.99"),
        price=Decimal("399.99"),
        features=[
            Feature(name="Premium AI Generation", description="Highest quality AI generation", is_highlighted=True),
            Feature(name="Unlimited Campaigns", description="Run as many campaigns as you need"),
            Feature(name="300 Posts/Day", description="Generate up to 300 posts per day across all platforms", is_limited=True, limit_value=300),
            Feature(name="Enterprise Analytics", description="Advanced analytics and insights"),
            Feature(name="24/7 Priority Support", description="Round-the-clock support", is_highlighted=True),
            Feature(name="Custom Branding", description="White-label solution"),
        ],
        is_enterprise=True,
        max_campaigns=-1,
        max_posts_per_day=300,
        max_platforms=-1,
        ai_creativity_level=3,
        priority_support=True,
        custom_branding=True,
        analytics_depth="enterprise"
    )
}

# Map of all pricing strategies
PRICING_STRATEGIES = {
    PricingStrategy.GROWTH: GROWTH_TIERS,
    PricingStrategy.PREMIUM: PREMIUM_TIERS,
    PricingStrategy.VALUE: VALUE_TIERS
}
