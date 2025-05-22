from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from services.generation.cluster import GenerationClusterService
from services.generation.llm import LLMProvider, OpenAIProvider, GeminiProvider
from services.generation.antidetection import AntiDetectionService
from models.campaigns import Campaign, CampaignSettings
from models.platform_connections import PlatformConnection
from sqlalchemy.orm import Session
from services.logging import init_logger
from services.generation.social_post_history import SocialPostHistoryService
from schemas.enums import CampaignStatus
from services.market_data import MarketDataService
from models.generation import SocialPost
from config.settings import get_settings
from enum import Enum

logger = init_logger()
settings = get_settings()


class LLMProviderType(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class CampaignManager:
    """
    Orchestrates the campaign management process flow.
    Handles campaign eligibility, scheduling, and coordination between services.
    """

    def __init__(self, db: Session, provider_type: LLMProviderType = LLMProviderType.OPENAI):
        self.db = db

        # Initialize LLM provider based on type
        if provider_type == LLMProviderType.OPENAI:
            self.llm_provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                system_instruction=settings.openai_system_instruction
            )
        else:
            self.llm_provider = GeminiProvider(
                api_key=settings.gemini_api_key,
                system_instruction=settings.gemini_system_instruction
            )

        self.generation_service = GenerationClusterService(db, self.llm_provider)
        self.social_post_history = SocialPostHistoryService(db)
        self.market_data_service = MarketDataService()
        self.anti_detection = AntiDetectionService()
        logger.info(f"Initialized CampaignManager with {provider_type.value} provider")

    async def __aenter__(self):
        await self.generation_service.__aenter__()
        await self.market_data_service.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.generation_service.__aexit__(exc_type, exc_val, exc_tb)
        await self.market_data_service.__aexit__(exc_type, exc_val, exc_tb)

    async def process_eligible_campaigns(self) -> List[Campaign]:
        """
        Process all eligible campaigns and generate posts for them.
        Returns list of processed campaigns.
        """
        eligible_campaigns = self.fetch_eligible_campaigns()
        processed_campaigns = []

        for campaign in eligible_campaigns:
            if await self.check_campaign_is_eligible(campaign):
                try:
                    await self.process_campaign(campaign.id)
                    processed_campaigns.append(campaign)
                except Exception as e:
                    logger.error(f"Error processing campaign {campaign.id}: {str(e)}")
                    continue

        return processed_campaigns

    async def process_campaign(self, campaign_id: int) -> None:
        """
        Process a single campaign and generate posts for all connected platforms.
        """
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found, skipping")
            return

        settings = self.db.query(CampaignSettings).filter(CampaignSettings.campaign_id == campaign_id).first()
        if not settings:
            logger.error(f"Campaign {campaign_id} has no settings, skipping")
            return

        # Get platform connections
        platform_connections = self.db.query(PlatformConnection).filter(
            PlatformConnection.campaign_id == campaign.id,
            PlatformConnection.is_connected == True
        ).all()

        if not platform_connections:
            logger.warning(f"Campaign {campaign_id} has no connected platforms, skipping")
            return

        # Process each platform
        for connection in platform_connections:
            try:
                # Generate post for this platform
                post_content = await self.generation_service.generate_social_post(
                    campaign=campaign,
                    campaign_settings=settings,
                    platform_type=connection.platform_type,
                    strategy_goal=settings.strategy_goal
                )

                logger.info(f"Generated post for campaign {campaign.id} on platform {connection.platform_type}: {post_content}")

                # TODO: Add platform-specific posting logic here
                # This would integrate with the actual social media platforms

                # Update campaign's next run time
                campaign.next_run_at = self._calculate_next_run_time(campaign, settings)
                self.db.commit()

            except Exception as e:
                logger.error(f"Error generating post for campaign {campaign.id} on platform {connection.platform_type}: {str(e)}")
                continue

    def fetch_eligible_campaigns(self) -> List[Campaign]:
        """Fetch all campaigns that are eligible for processing."""
        return self.db.query(Campaign).filter(
            Campaign.is_active == True,
            Campaign.is_paused == False,
            Campaign.status == CampaignStatus.RUNNING,
            Campaign.next_run_at <= datetime.now()
        ).all()

    async def check_campaign_is_eligible(self, campaign: Campaign) -> bool:
        """Check if a campaign is eligible for processing."""
        if campaign.workspace.is_deleted:
            logger.info(f"Campaign {campaign.id} workspace is deleted, skipping")
            return False

        if not campaign.workspace.is_active:
            logger.info(f"Campaign {campaign.id} workspace is not active, skipping")
            return False

        settings = self.db.query(CampaignSettings).filter(CampaignSettings.campaign_id == campaign.id).first()
        if not settings:
            logger.error(f"Campaign {campaign.id} has no settings, skipping")
            return False

        if settings.emergency_stop_enabled:
            logger.info(f"Campaign {campaign.id} has emergency stop enabled, skipping")
            return False

        platform_connections = self.db.query(PlatformConnection).filter(
            PlatformConnection.campaign_id == campaign.id,
            PlatformConnection.is_connected == True
        ).all()

        if not platform_connections:
            logger.error(f"Campaign {campaign.id} has no connected platforms, skipping")
            return False

        if campaign.status != CampaignStatus.RUNNING:
            logger.error(f"Campaign {campaign.id} is not running, skipping")
            return False

        if campaign.next_run_at > datetime.now():
            logger.info(f"Campaign {campaign.id} is not due to run yet, skipping")
            return False

        return True

    def _calculate_next_run_time(self, campaign: Campaign, settings: CampaignSettings) -> datetime:
        """
        Calculate the next run time for a campaign based on its settings and anti-detection patterns.
        Takes into account the maximum number of posts per day and adds random silence periods.
        """
        now = datetime.now()

        # Calculate base interval between posts based on posts per day
        posts_per_day = settings.max_daily_posts
        if posts_per_day <= 0:
            raise ValueError(f"Invalid posts_per_day value: {posts_per_day}")

        # Calculate minimum hours between posts
        min_hours_between_posts = 24 / posts_per_day

        # Calculate base next run time
        next_run = now + timedelta(hours=min_hours_between_posts)

        # Add random silence using anti-detection service
        # Using hours as the unit since we're dealing with daily post limits
        next_run = self.anti_detection.add_random_silence(
            next_post_time=next_run,
            unit='hours',
            min_val=1,
            max_val=int(min_hours_between_posts * 2)  # Allow up to 2x the base interval
        )

        # Ensure we don't exceed posts per day
        posts_today = self.db.query(SocialPost).filter(
            SocialPost.campaign_id == campaign.id,
            SocialPost.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()

        if posts_today >= posts_per_day:
            # If we've hit the daily limit, schedule for tomorrow
            next_run = next_run.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        return next_run
