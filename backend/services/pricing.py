from typing import Dict, Any, Optional
from schemas.pricing import PricingStrategy, PRICING_STRATEGIES, PricingResponse, PricingTier
from services.logging import init_logger
from config.settings import get_settings
from decimal import Decimal

logger = init_logger()
settings = get_settings()


class PricingService:
    """Service for managing pricing strategies and tiers"""

    def __init__(
        self,
        pricing_strategy: PricingStrategy = PricingStrategy.GROWTH,
        price_adjustment_percentage: Optional[float] = None,
        price_adjustment_amount: Optional[float] = None
    ):
        self.current_strategy = pricing_strategy
        self.price_adjustment_percentage = price_adjustment_percentage
        self.price_adjustment_amount = Decimal(price_adjustment_amount) if price_adjustment_amount is not None else None

        # Log initialization
        adjustment_info = []
        if price_adjustment_percentage is not None:
            adjustment_info.append(f"percentage: {price_adjustment_percentage}%")
        if price_adjustment_amount is not None:
            adjustment_info.append(f"amount: {price_adjustment_amount}")

        adjustment_str = " and ".join(adjustment_info) if adjustment_info else "no adjustment"
        logger.info(f"Initialized PricingService with strategy: {self.current_strategy} and {adjustment_str}")

    def get_current_pricing(self) -> PricingResponse:
        """Get the current pricing strategy and tiers"""
        try:
            strategy = PricingStrategy(self.current_strategy)
            tiers = PRICING_STRATEGIES[strategy].copy()  # Create a copy to avoid modifying the original

            # Apply price adjustments to all tiers
            for tier_key, tier in tiers.items():
                tier.adjust_price(
                    percentage=self.price_adjustment_percentage,
                    amount=self.price_adjustment_amount
                )
                # Generate price tag for each tier
                tier.generate_price_tag(
                    secret_key=settings.jwt_secret,
                    strategy=strategy.value,
                    tier_key=tier_key
                )

            # Create and return the response model
            return PricingResponse(
                strategy=strategy.value,
                price_adjustment_percentage=self.price_adjustment_percentage,
                price_adjustment_amount=self.price_adjustment_amount,
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

    def set_price_adjustment_percentage(self, percentage: float) -> None:
        """Set the percentage-based price adjustment for all tiers"""
        self.price_adjustment_percentage = percentage
        self.price_adjustment_amount = None
        logger.info(f"Price adjustment set to: {percentage}%")

    def set_price_adjustment_amount(self, amount: Decimal) -> None:
        """Set the amount-based price adjustment for all tiers"""
        self.price_adjustment_amount = amount
        self.price_adjustment_percentage = None
        logger.info(f"Price adjustment amount set to: {amount}")

    def validate_price_tag(self, price_tag: str) -> Dict[str, Any]:
        """
        Validate a price tag and return the pricing details if valid.

        Args:
            price_tag: The price tag to validate

        Returns:
            Dict containing validated pricing details or None if invalid
        """
        from schemas.pricing import PriceTag

        validated_tag = PriceTag.validate_price_tag(price_tag, settings.jwt_secret)
        if validated_tag:
            return validated_tag.model_dump()
        return None
