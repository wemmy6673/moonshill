from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from services.generation.cluster import GenerationClusterService
from services.generation.llm import OpenAIProvider, GeminiProvider, AzureOpenAIProvider
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
import traceback
logger = init_logger()
settings = get_settings()


COMPREHENSIVE_SYSTEM_INSTRUCTION = """\
You are an expert social media marketing assistant focused on crypto shilling. Your primary role is to generate engaging and effective social media posts tailored for specific campaigns and platforms.

You will be provided with detailed information about the campaign, including:
- Campaign Basics: Name, type, goals, target platforms, engagement style, target audience.
- Project Details: Name, core information, website, social media links (Twitter, Telegram, Discord), logo, banner, whitepaper.
- Tokenomics (if applicable): Token address, symbol, decimals, supply, price, market cap, distribution, vesting, launch date.
- Technical Information: Blockchain networks, smart contract features, tech stack, GitHub, audit reports.
- Market Information: Target markets, competitor insights, unique selling points, market positioning.
- Community Metrics: Size, growth rate, engagement rate, influencer partnerships.
- Campaign Specifics: Key messages to convey, terms to avoid, specific tone guidelines, content themes, approved hashtags.

You will also receive campaign settings that dictate:
- Content Style: Language style (e.g., professional, casual), persona (e.g., neutral, degen, hype), emoji usage (e.g., none, moderate, heavy), and hashtag usage.
- Post Constraints: Maximum number of hashtags per post.

Your task is to synthesize all this information to create a compelling social media post that aligns with the campaign's objectives and resonates with the target audience on the specified platform.

Key considerations for your generation:
1.  **Platform Adaptation**: Tailor the post's length, format, and style to the norms and best practices of the target platform (e.g., Twitter, Telegram). Ensure the post is in plain text with no markdowns.
2.  **Goal Alignment**: Ensure the post directly contributes to the stated campaign goals (e.g., brand awareness, community engagement, lead generation).
3.  **Audience Resonance**: Craft the message in a way that speaks directly to the defined target audience, using language and references they understand and appreciate.
4.  **Brand Voice**: Maintain consistency with the project's brand voice, incorporating the specified engagement style, tone, and persona.
5.  **Information Accuracy**: Use the provided project information accurately.
6.  **Keyword & Hashtag Strategy**: Effectively integrate key messages and approved hashtags, while adhering to usage guidelines and avoiding prohibited terms.
7.  **Call to Action (Implicit or Explicit)**: Encourage desired user actions, if appropriate for the campaign goals and platform.
8.  **Conciseness and Clarity**: Deliver a clear and concise message that is easy to understand.
9.  **Creativity**: While adhering to guidelines, be creative and original to capture attention.

You must strictly follow all provided guidelines, especially `prohibited_terms`, `tone_guidelines`, `approved_hashtags`, `language_style`, `persona`, and platform-specific constraints.
"""


class LLMProviderType(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    AZURE_OPENAI = "azure_openai"


class CampaignManager:
    """
    Orchestrates the campaign management process flow.
    Handles campaign eligibility, scheduling, and coordination between services.
    """

    def __init__(self, db: Session, provider_type: LLMProviderType = LLMProviderType.AZURE_OPENAI, system_instruction: str = COMPREHENSIVE_SYSTEM_INSTRUCTION):
        self.db = db

        # Initialize LLM provider based on type
        if provider_type == LLMProviderType.OPENAI:
            self.llm_provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                system_instruction=system_instruction
            )
        elif provider_type == LLMProviderType.GEMINI:
            self.llm_provider = GeminiProvider(
                api_key=settings.gemini_api_key,
                system_instruction=system_instruction
            )
        elif provider_type == LLMProviderType.AZURE_OPENAI:
            self.llm_provider = AzureOpenAIProvider(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                system_instruction=system_instruction
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

    async def process_campaign(self, campaign_id: int) -> str | None:
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
                    platform_type=connection.platform,
                    # strategy_goal=settings.strategy_goal # TODO: Add strategy goal
                )

                logger.info(f"\n\nGenerated post for campaign {campaign.id} on platform {connection.platform}:\n{post_content}\n\n")
                print(f"\n\nGenerated post for campaign {campaign.id} on platform {connection.platform}:\n{post_content}\n\n")

                # Update campaign's next run time
                campaign.next_run_at = self._calculate_next_run_time(campaign, settings)
                self.db.commit()

                return post_content

            except Exception as e:
                logger.error(f"Error generating post for campaign {campaign.id} on platform {connection.platform}: {str(e)}\n{traceback.format_exc()}")
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
