from typing import Dict, Any
from schemas.pricing import PricingStrategy, PRICING_STRATEGIES, PricingResponse, PricingTier
from services.logging import init_logger

logger = init_logger()


class PricingService:
    """Service for managing pricing strategies and tiers"""

    def __init__(self, pricing_strategy: PricingStrategy = PricingStrategy.GROWTH, price_adjustment: float = 0.0):
        self.current_strategy = pricing_strategy
        self.price_adjustment = price_adjustment
        logger.info(f"Initialized PricingService with strategy: {self.current_strategy} and price adjustment: {self.price_adjustment}%")

    def get_current_pricing(self) -> PricingResponse:
        """Get the current pricing strategy and tiers"""
        try:
            strategy = PricingStrategy(self.current_strategy)
            tiers = PRICING_STRATEGIES[strategy].copy()  # Create a copy to avoid modifying the original

            # Apply price adjustment to all tiers
            for tier in tiers.values():
                tier.adjust_price(self.price_adjustment)

            # Create and return the response model
            return PricingResponse(
                strategy=strategy.value,
                price_adjustment=self.price_adjustment,
                tiers={k: v.model_dump() for k, v in tiers.items()}
            )
        except Exception as e:
            logger.error(f"Error getting pricing: {str(e)}")
            raise

    def get_tier_limits(self, tier_name: str) -> Dict[str, Any]:
        """Get the limits for a specific tier"""
        try:
            strategy = PricingStrategy(self.current_strategy)
            tiers = PRICING_STRATEGIES[strategy]

            if tier_name not in tiers:
                raise ValueError(f"Invalid tier name: {tier_name}")

            tier = tiers[tier_name]
            return {
                "max_campaigns": tier.max_campaigns,
                "max_posts_per_day": tier.max_posts_per_day,
                "max_platforms": tier.max_platforms,
                "ai_creativity_level": tier.ai_creativity_level
            }
        except Exception as e:
            logger.error(f"Error getting tier limits: {str(e)}")
            raise

    def is_feature_available(self, tier_name: str, feature_name: str) -> bool:
        """Check if a feature is available in a specific tier"""
        try:
            strategy = PricingStrategy(self.current_strategy)
            tiers = PRICING_STRATEGIES[strategy]

            if tier_name not in tiers:
                raise ValueError(f"Invalid tier name: {tier_name}")

            tier = tiers[tier_name]
            return any(f.name == feature_name for f in tier.features)
        except Exception as e:
            logger.error(f"Error checking feature availability: {str(e)}")
            raise

    def set_price_adjustment(self, adjustment: float) -> None:
        """Set the price adjustment percentage for all tiers"""
        self.price_adjustment = adjustment
        logger.info(f"Price adjustment set to: {adjustment}%")
