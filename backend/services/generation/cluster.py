from typing import List, Dict, Optional, Any, Protocol, Tuple, Union
from datetime import datetime
from services.logging import init_logger
from config.settings import get_settings
from models.campaigns import Campaign, CampaignSettings
from sqlalchemy.orm import Session
import random
from services.generation.llm import LLMProvider
from services.generation.antidetection import AntiDetectionService
from services.generation.engagement_learning import EngagementLearningService
from services.market_data import MarketDataService
from schemas.generation import (
    PlatformType, PostStage, PostStyle, PostType,
    PostStrategyGoal, CampaignPhase, PlatformPrompt, PersonaPrompt,
    ProjectInfoPrompt, TrendingHooksPrompt, StrategyPrompt, PromptComponent
)
from schemas.enums import CampaignTimeline
from services.generation.social_post_history import SocialPostHistoryService

logger = init_logger()
settings = get_settings()


class GenerationClusterService:
    """
    Service for AI social post generation with modular prompt engine.
    Handles post generation, A/B testing, and engagement optimization.
    """

    def __init__(self, db: Session, llm_provider: LLMProvider):
        self.logger = init_logger()
        self.db = db
        self.llm_provider = llm_provider
        self.social_post_history = SocialPostHistoryService(db)
        self.anti_detection = AntiDetectionService()
        self.engagement_learning = EngagementLearningService(db)
        self.market_data_service = MarketDataService()

    async def __aenter__(self):
        await self.market_data_service.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.market_data_service.__aexit__(exc_type, exc_val, exc_tb)

    async def generate_social_post(
        self,
        campaign: Campaign,
        campaign_settings: CampaignSettings,
        platform_type: PlatformType,
        strategy_goal: PostStrategyGoal,
        trending_hooks: Optional[List[str]] = None
    ) -> str:
        """
        Generate a social post using the modular prompt engine with memory and continuity.
        """
        # Get post history for context
        recent_posts = await self.social_post_history.get_recent_posts(campaign.id)

        # Analyze performance of recent posts
        successful, unsuccessful = await self.engagement_learning.analyze_performance(campaign.id)
        successful_patterns = await self.engagement_learning.get_successful_patterns(successful)

        # Get market data and time context
        market_context = await self._get_market_data_context(campaign)
        time_context = self._get_time_context()

        # Determine post stage based on campaign phase and history
        stage = await self._determine_post_stage(
            campaign,
            recent_posts
        )

        # Get stage-specific posts for context
        stage_posts = await self.social_post_history.get_stage_posts(campaign.id, stage)

        # Determine post style based on campaign phase and successful patterns
        campaign_phase = self._determine_campaign_phase(campaign)
        post_style = await self._determine_post_style(
            campaign_phase,
            successful_patterns
        )

        # Build prompt components
        persona = await self._build_persona_component(campaign_settings)
        project_info = await self._build_project_info_component(campaign, market_context)
        platform = await self._build_platform_component(platform_type, campaign_settings)
        trending = await self._build_trending_hooks_component(trending_hooks)
        strategy = await self._build_strategy_component(campaign, strategy_goal)
        memory = await self._build_memory_component(recent_posts, stage_posts, stage)
        time_awareness = await self._build_time_awareness_component(time_context)

        # Add performance-based instructions
        performance = await self._build_performance_instructions(
            successful_patterns,
            post_style
        )

        # Combine components into final prompt
        prompt = await self._combine_prompt_components(
            persona=persona,
            project_info=project_info,
            platform=platform,
            trending=trending,
            strategy=strategy,
            memory=memory,
            performance=performance,
            time_awareness=time_awareness
        )

        # Generate post content using LLM
        post_content = await self.llm_provider.generate(prompt)

        # Apply anti-detection patterns
        post_content = self.anti_detection.apply_human_like_patterns(
            post_content,
            intensity=campaign_settings.ai_creativity_level
        )

        # Get embeddings for the generated post
        embeddings = await self.llm_provider.get_embeddings(post_content)

        # Store post in history
        await self.social_post_history.add_social_post(
            campaign_id=campaign.id,
            platform_type=platform_type,
            content=post_content,
            post_stage=stage,
            post_style=post_style,
            post_type=PostType.TEXT,  # Default to text
            embeddings=embeddings
        )

        return post_content

    async def _get_market_data_context(self, campaign: Campaign) -> Dict[str, Any]:
        """Get market data context for the campaign"""
        return await self.market_data_service.get_campaign_market_data_context(
            campaign.project_token_address,
            campaign.blockchain_networks[0] if campaign.blockchain_networks else None
        ).model_dump(exclude_none=True, exclude_unset=True)

    def _get_time_context(self) -> Dict[str, Any]:
        """Get current time context"""
        now = datetime.now()
        return {
            "current_date": now.strftime("%Y-%m-%d"),
            "current_time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "is_weekend": now.weekday() >= 5,
            "hour_of_day": now.hour,
            "season": self._get_season(now),
        }

    def _get_season(self, date: datetime) -> str:
        """Determine the current season based on the date."""
        month = date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    async def _build_time_awareness_component(self, time_context: Dict[str, Any]) -> PromptComponent:
        """Build time awareness component of the prompt"""
        content = f"""Time Context:
- Current Date: {time_context['current_date']}
- Current Time: {time_context['current_time']}
- Day of Week: {time_context['day_of_week']}
- Season: {time_context['season']}
- Is Weekend: {'Yes' if time_context['is_weekend'] else 'No'}

Instructions:
- Consider time-appropriate content and tone
- Adjust engagement style based on time of day
- Consider seasonal relevance in content
"""

        return PromptComponent(
            content=content,
            weight=1.0
        )

    async def _build_project_info_component(
        self,
        campaign: Campaign,
        market_context: Dict[str, Any]
    ) -> ProjectInfoPrompt:
        """Build the project information component of the prompt"""
        return ProjectInfoPrompt(
            project_name=campaign.project_name,
            project_info=campaign.project_info,
            tokenomics=campaign.tokenomics,
            technical_info=campaign.technical_info,
            market_info={**campaign.market_info, **market_context} if campaign.market_info else market_context,
            content=f"""Project: {campaign.project_name}
Info: {campaign.project_info}
Market Data: {market_context}"""
        )

    async def _determine_post_stage(
        self,
        campaign: Campaign,
        recent_posts: List[Any]
    ) -> PostStage:
        """Determine the appropriate post stage based on campaign phase and history"""
        campaign_phase = self._determine_campaign_phase(campaign)

        # Count posts by stage
        stage_counts = {}
        for post in recent_posts:
            stage_counts[post.post_stage] = stage_counts.get(post.post_stage, 0) + 1

        # Determine stage based on campaign phase and post distribution
        if campaign_phase == CampaignPhase.EARLY:
            if stage_counts.get(PostStage.INTRO, 0) < 2:
                return PostStage.INTRO
            elif stage_counts.get(PostStage.HYPE, 0) < 3:
                return PostStage.HYPE
            else:
                return PostStage.MEME

        elif campaign_phase == CampaignPhase.MID:
            if stage_counts.get(PostStage.DEEP_DIVE, 0) < 2:
                return PostStage.DEEP_DIVE
            elif stage_counts.get(PostStage.HYPE, 0) < 3:
                return PostStage.HYPE
            else:
                return PostStage.MEME

        else:  # LATE phase
            if stage_counts.get(PostStage.CTA, 0) < 2:
                return PostStage.CTA
            elif stage_counts.get(PostStage.DEEP_DIVE, 0) < 2:
                return PostStage.DEEP_DIVE
            else:
                return PostStage.HYPE

    async def _build_memory_component(
        self,
        recent_posts: List[Any],
        stage_posts: List[Any],
        current_stage: PostStage
    ) -> PromptComponent:
        """Build the memory component of the prompt"""
        # Format recent posts
        recent_context = "\n".join([
            f"Recent post ({post.post_stage}): {post.content}"
            for post in recent_posts
        ])

        # Format stage-specific posts
        stage_context = "\n".join([
            f"Previous {post.post_stage} post: {post.content}"
            for post in stage_posts
        ])

        content = f"""Post History Context:
Current Stage: {current_stage}

Recent Posts:
{recent_context}

Previous {current_stage} Posts:
{stage_context}

Instructions:
- Ensure post progression and avoid repeating ideas
- Build upon previous posts while maintaining consistency
- Vary the style and approach while staying within the current stage
"""

        return PromptComponent(
            content=content,
            weight=1.2  # Give memory component higher weight
        )

    def _determine_campaign_phase(self, campaign: Campaign) -> CampaignPhase:
        """Determine the current phase of the campaign"""
        now = datetime.now()
        start_date = campaign.campaign_start_date

        # Calculate campaign duration
        duration = now - start_date

        # Determine phase based on campaign timeline
        if campaign.campaign_timeline == CampaignTimeline.ONE_WEEK:
            if duration.days < 2:
                return CampaignPhase.EARLY
            elif duration.days < 5:
                return CampaignPhase.MID
            else:
                return CampaignPhase.LATE

        elif campaign.campaign_timeline == CampaignTimeline.TWO_WEEKS:
            if duration.days < 4:
                return CampaignPhase.EARLY
            elif duration.days < 10:
                return CampaignPhase.MID
            else:
                return CampaignPhase.LATE

        elif campaign.campaign_timeline == CampaignTimeline.ONE_MONTH:
            if duration.days < 10:
                return CampaignPhase.EARLY
            elif duration.days < 20:
                return CampaignPhase.MID
            else:
                return CampaignPhase.LATE

        elif campaign.campaign_timeline == CampaignTimeline.TWO_MONTHS:
            if duration.days < 20:
                return CampaignPhase.EARLY
            elif duration.days < 40:
                return CampaignPhase.MID
            else:
                return CampaignPhase.LATE

        elif campaign.campaign_timeline == CampaignTimeline.THREE_MONTHS:
            if duration.days < 30:
                return CampaignPhase.EARLY
            elif duration.days < 60:
                return CampaignPhase.MID
            else:
                return CampaignPhase.LATE

        elif campaign.campaign_timeline == CampaignTimeline.SIX_MONTHS:
            if duration.days < 60:
                return CampaignPhase.EARLY
            elif duration.days < 120:
                return CampaignPhase.MID
            else:
                return CampaignPhase.LATE

        else:  # ONE_YEAR or longer
            if duration.days < 120:
                return CampaignPhase.EARLY
            elif duration.days < 240:
                return CampaignPhase.MID
            else:
                return CampaignPhase.LATE

    async def _determine_post_style(
        self,
        campaign_phase: CampaignPhase,
        successful_patterns: Dict[str, Any]
    ) -> PostStyle:
        """Determine post style based on campaign phase and successful patterns"""
        if not successful_patterns:
            return self.anti_detection.generate_message_style(campaign_phase)

        # Get style distribution from successful patterns
        style_distribution = successful_patterns.get('styles', {})

        if style_distribution:
            # Weight random choice by success distribution
            styles = list(style_distribution.keys())
            weights = list(style_distribution.values())
            return random.choices(styles, weights=weights, k=1)[0]
        else:
            return self.anti_detection.generate_message_style(campaign_phase)

    async def _build_performance_instructions(
        self,
        successful_patterns: Dict[str, Any],
        style: PostStyle
    ) -> PromptComponent:
        """Build instructions based on successful patterns"""
        if not successful_patterns:
            return PromptComponent(content="", weight=0.0)

        # Get successful style-specific patterns
        style_success_rate = successful_patterns.get('styles', {}).get(style, 0)

        # Get top performing embeddings
        top_embeddings = successful_patterns.get('top_embeddings', [])

        content = f"""
        Performance Insights:
        - This style has a {style_success_rate:.1%} success rate
        - Aim to match the tone and style of previous successful posts
        - Consider timing and engagement patterns
        """

        if top_embeddings:
            content += "\n- Use similar semantic patterns to successful posts"

        return PromptComponent(
            content=content,
            weight=1.2  # Give performance insights high weight
        )

    async def _build_persona_component(self, settings: CampaignSettings) -> PersonaPrompt:
        """Build the persona component of the prompt"""
        return PersonaPrompt(
            persona_type=settings.persona,
            tone_guidelines=settings.language_style,
            emoji_usage=settings.emoji_usage,
            content=f"Act as a {settings.persona} with {settings.emoji_usage} emoji usage and {settings.language_style} language style."
        )

    async def _build_platform_component(
        self,
        platform_type: PlatformType,
        settings: CampaignSettings
    ) -> PlatformPrompt:
        """Build the platform-specific component of the prompt"""
        platform_settings = settings.platform_settings.get(platform_type, {})
        return PlatformPrompt(
            platform_type=platform_type,
            platform_settings=platform_settings,
            content=f"Platform: {platform_type}\nSettings: {platform_settings}"
        )

    async def _build_trending_hooks_component(
        self,
        trending_hooks: Optional[List[str]]
    ) -> TrendingHooksPrompt:
        """Build the trending hooks component of the prompt"""
        if not trending_hooks:
            trending_hooks = []
        return TrendingHooksPrompt(
            trending_topics=trending_hooks,
            relevant_hashtags=[f"#{hook.replace(' ', '')}" for hook in trending_hooks],
            content=f"Trending topics: {', '.join(trending_hooks)}"
        )

    async def _build_strategy_component(
        self,
        campaign: Campaign,
        strategy_goal: PostStrategyGoal
    ) -> StrategyPrompt:
        """Build the strategy component of the prompt"""
        campaign_phase = self._determine_campaign_phase(campaign)
        return StrategyPrompt(
            goal=strategy_goal,
            campaign_phase=campaign_phase,
            key_messages=campaign.key_messages or [],
            content=f"Goal: {strategy_goal}\nPhase: {campaign_phase}\nKey Messages: {', '.join(campaign.key_messages or [])}"
        )

    async def _combine_prompt_components(
        self,
        persona: PersonaPrompt,
        project_info: ProjectInfoPrompt,
        platform: PlatformPrompt,
        trending: TrendingHooksPrompt,
        strategy: StrategyPrompt,
        memory: PromptComponent,
        performance: PromptComponent,
        time_awareness: PromptComponent
    ) -> str:
        """Combine all prompt components into a final prompt"""
        components = [
            persona,
            project_info,
            platform,
            trending,
            strategy,
            memory,
            performance,
            time_awareness
        ]

        # Sort components by weight
        components.sort(key=lambda x: x.weight, reverse=True)

        # Combine components into final prompt
        prompt = "\n\n".join(comp.content for comp in components)

        return prompt
