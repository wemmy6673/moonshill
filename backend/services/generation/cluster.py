from typing import List, Dict, Optional, Any, Union, Tuple
from datetime import datetime
from services.logging import init_logger
from config.settings import get_settings
from models.campaigns import Campaign, CampaignSettings
from models.generation import (
    SocialPost, PostAnalytics, PostPerformance,
    EngagementPattern
)
from schemas.campaigns import campaign_from_db_to_schema
from sqlalchemy.orm import Session
import random
from services.generation.llm import LLMProvider
from services.generation.antidetection import AntiDetectionService
from services.generation.engagement_learning import EngagementLearningService
from services.market_data import MarketDataService, MarketData, TrendingTopic
from schemas.generation import (
    PlatformType, PostStage, PostStyle, PostType,
    PostStrategyGoal, CampaignPhase, PlatformPrompt, PersonaPrompt,
    ProjectInfoPrompt, TrendingHooksPrompt, StrategyPrompt, PromptComponent
)
from schemas.enums import CampaignTimeline
from services.generation.social_post_history import SocialPostHistoryService

logger = init_logger()
settings = get_settings()


# Prompt Component Weights - Adjusted based on crypto marketing priorities
WEIGHTS_DISTRIBUTION = {
    "project_info": 3.0,    # Critical context for token/project details
    "market_data": 2.9,     # Real-time market performance
    "platform": 2.8,        # Platform-specific optimization
    "memory": 2.5,          # Context and continuity
    "strategy": 2.4,        # Campaign alignment
    "performance": 2.3,     # Historical success patterns
    "trending": 2.2,        # Market trends and sentiment
    "persona": 1.8,         # Voice consistency
    "time_awareness": 1.5,  # Timing optimization
}

# Platform-specific constraints for crypto content
PLATFORM_CONSTRAINTS = {
    PlatformType.TWITTER: {
        "max_length": 280,
        "optimal_length": 240,
        "max_hashtags": 3,
        "optimal_hashtags": 2,
        "style_guide": "Concise, impactful calls to action, strong hooks",
        "link_position": "end",
        "cashtag_enabled": True
    },
    PlatformType.TELEGRAM: {
        "max_length": 4096,
        "optimal_length": 800,
        "max_hashtags": 5,
        "optimal_hashtags": 3,
        "style_guide": "Detailed analysis, community updates, price action",
        "link_position": "flexible",
        "formatting": "markdown"
    },
    PlatformType.DISCORD: {
        "max_length": 2000,
        "optimal_length": 600,
        "max_hashtags": 0,
        "optimal_hashtags": 0,
        "style_guide": "Technical updates, trading signals, community engagement",
        "link_position": "body",
        "formatting": "discord_markdown"
    }
}

# Post style patterns by campaign phase for crypto
PHASE_STYLE_PATTERNS = {
    CampaignPhase.EARLY: {
        "tone": "bullish and informative",
        "focus": "tokenomics and utility",
        "cta_strength": "soft",
        "price_emphasis": "low",
        "community_focus": "high",
        "technical_detail": "medium"
    },
    CampaignPhase.MID: {
        "tone": "confident and momentum-building",
        "focus": "growth metrics and adoption",
        "cta_strength": "moderate",
        "price_emphasis": "medium",
        "community_focus": "high",
        "technical_detail": "high"
    },
    CampaignPhase.LATE: {
        "tone": "urgent and fomo-inducing",
        "focus": "price action and volume",
        "cta_strength": "strong",
        "price_emphasis": "high",
        "community_focus": "medium",
        "technical_detail": "low"
    }
}

# Engagement thresholds for performance evaluation
ENGAGEMENT_THRESHOLDS = {
    "high": {
        "engagement_rate": 0.05,
        "virality_score": 0.8,
        "sentiment_score": 0.7
    },
    "medium": {
        "engagement_rate": 0.02,
        "virality_score": 0.5,
        "sentiment_score": 0.5
    },
    "low": {
        "engagement_rate": 0.01,
        "virality_score": 0.3,
        "sentiment_score": 0.3
    }
}


class GenerationClusterService:
    """Service for AI social post generation with modular prompt engine."""

    def __init__(self, db: Session, llm_provider: LLMProvider):
        self.logger = init_logger()
        self.db = db
        self.llm_provider = llm_provider
        self.social_post_history = SocialPostHistoryService(db)
        self.anti_detection = AntiDetectionService()
        self.engagement_learning = EngagementLearningService(db)
        self.market_data_service = MarketDataService()

    # Context Management Methods
    async def __aenter__(self):
        await self.market_data_service.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.market_data_service.__aexit__(exc_type, exc_val, exc_tb)

    # Main Generation Method
    async def generate_social_post(
        self,
        campaign: Campaign,
        campaign_settings: CampaignSettings,
        platform_type: PlatformType,
        strategy_goal: PostStrategyGoal = PostStrategyGoal.AWARENESS,
        trending_hooks: Optional[List[str]] = None
    ) -> Tuple[str, int]:
        """Generate a social post using the modular prompt engine with memory and continuity."""

        # Initialize context with market data
        context = await self._initialize_generation_context(
            campaign=campaign,
            platform_type=platform_type
        )

        # Build components with market awareness
        components = await self._build_all_components(
            campaign=campaign,
            settings=campaign_settings,
            platform_type=platform_type,
            strategy_goal=strategy_goal,
            trending_hooks=trending_hooks,
            context=context
        )

        # Generate and process post with engagement optimization
        post_content, post_id = await self._generate_and_process_post(
            components=components,
            campaign=campaign,
            settings=campaign_settings,
            platform_type=platform_type,
            context=context
        )

        return post_content, post_id

    async def _initialize_generation_context(
        self,
        campaign: Campaign,
        platform_type: PlatformType
    ) -> Dict[str, Any]:
        """Initialize generation context with market data and performance metrics."""

        # Get market context
        market_context = await self.market_data_service.get_campaign_market_data_context(
            token_address=campaign.project_token_address,
            blockchain=campaign.blockchain_networks[0] if campaign.blockchain_networks else None,
            keywords=[campaign.project_name, campaign.project_token_symbol] if hasattr(campaign, 'project_token_symbol') else [campaign.project_name]
        )

        # Get post history and performance
        recent_posts = await self.social_post_history.get_recent_posts(campaign.id)
        successful_patterns = await self._analyze_post_performance(campaign.id, recent_posts)

        # Get time context
        time_context = self._get_time_context()

        return {
            "market_data": market_context.market_data,
            "trending_topics": market_context.trending_topics,
            "recent_posts": recent_posts,
            "successful_patterns": successful_patterns,
            "time_context": time_context,
            "platform_constraints": PLATFORM_CONSTRAINTS[platform_type]
        }

    async def _analyze_post_performance(self, campaign_id: int, recent_posts: List[SocialPost]) -> Dict[str, Any]:
        """Analyze post performance with detailed metrics."""
        performance_data = {}

        for post in recent_posts:
            # Get analytics
            analytics = self.db.query(PostAnalytics).filter(
                PostAnalytics.post_id == post.id
            ).first()

            # Get performance metrics
            performance = self.db.query(PostPerformance).filter(
                PostPerformance.post_id == post.id
            ).first()

            if analytics and performance:
                performance_level = self._determine_performance_level(
                    engagement_rate=performance.engagement_rate,
                    virality_score=performance.virality_score,
                    sentiment_score=performance.sentiment_score
                )

                # Store successful patterns
                if performance_level in ["high", "medium"]:
                    self._store_engagement_pattern(
                        campaign_id=campaign_id,
                        post=post,
                        performance_metrics={
                            "engagement_rate": performance.engagement_rate,
                            "virality_score": performance.virality_score,
                            "sentiment_score": performance.sentiment_score
                        }
                    )

        return performance_data

    def _determine_performance_level(
        self,
        engagement_rate: float,
        virality_score: float,
        sentiment_score: float
    ) -> str:
        """Determine post performance level based on metrics."""
        for level, thresholds in ENGAGEMENT_THRESHOLDS.items():
            if (
                engagement_rate >= thresholds["engagement_rate"] and
                virality_score >= thresholds["virality_score"] and
                sentiment_score >= thresholds["sentiment_score"]
            ):
                return level
        return "low"

    async def _store_engagement_pattern(
        self,
        campaign_id: int,
        post: SocialPost,
        performance_metrics: Dict[str, float]
    ) -> None:
        """Store successful engagement patterns."""
        pattern = EngagementPattern(
            campaign_id=campaign_id,
            pattern_type=post.post_style,
            pattern_value=post.content[:100],  # Store first 100 chars as pattern
            success_rate=performance_metrics["engagement_rate"],
            sample_size=1
        )
        self.db.add(pattern)
        self.db.commit()

    # Component Building Methods
    async def _build_persona_component(self, settings: CampaignSettings) -> PersonaPrompt:
        """Build the persona component of the prompt"""
        persona_content = f"""PERSONA GUIDELINES
        
Role: {settings.persona} voice
Language Style: {settings.language_style}
Emoji Usage: {settings.emoji_usage}

Additional Style Notes:
- Use {settings.language_style} language consistently
- Maintain {settings.persona} personality throughout
- Include emojis: {settings.emoji_usage} frequency
- Match {settings.risk_level} risk level in messaging
- Follow {settings.compliance_check_level} compliance standards

Key Behavioral Traits:
- Engagement Style: {settings.engagement_style if hasattr(settings, 'engagement_style') else 'balanced'}
- Community Focus: {'high' if settings.auto_reply else 'moderate'}
- Formality: {settings.language_style}
"""

        return PersonaPrompt(
            persona_type=settings.persona,
            tone_guidelines=settings.language_style,
            emoji_usage=settings.emoji_usage,
            content=persona_content,
            weight=WEIGHTS_DISTRIBUTION["persona"]
        )

    async def _build_project_info_component(
        self,
        campaign: Campaign,
        market_context: Dict[str, Any]
    ) -> ProjectInfoPrompt:
        """Build the project information component of the prompt"""
        campaign_schema = campaign_from_db_to_schema(campaign)

        market_info = {}
        if campaign_schema.market_info:
            market_info = campaign_schema.market_info.model_dump(exclude_none=True, exclude_unset=True)
        if market_context:
            market_info.update(market_context)

        tokenomics = campaign_schema.tokenomics.model_dump(exclude_none=True, exclude_unset=True) if campaign_schema.tokenomics else {}
        tech_info = campaign_schema.technical_info.model_dump(exclude_none=True, exclude_unset=True) if campaign_schema.technical_info else {}

        project_content = f"""PROJECT INFORMATION

Basic Information:
- Name: {campaign_schema.project_name}
- Description: {campaign_schema.project_info}
- Website: {campaign_schema.project_website or "N/A"}

Social Media:
- Twitter: {campaign_schema.project_twitter or "N/A"}
- Telegram: {campaign_schema.project_telegram or "N/A"}
- Discord: {campaign_schema.project_discord or "N/A"}

Tokenomics:
- Token Address: {tokenomics.get('token_address', 'N/A')}
- Symbol: {tokenomics.get('token_symbol', 'N/A')}
- Supply: {tokenomics.get('token_supply', 'N/A')}
- Current Price: {tokenomics.get('token_current_price', 'N/A')}
- Market Cap: {tokenomics.get('market_cap', 'N/A')}
- Launch Date: {tokenomics.get('token_launch_date', 'N/A')}

Technical Details:
- Blockchain Networks: {', '.join(tech_info.get('blockchain_networks', ['N/A']))}
- Smart Contract Features: {', '.join(tech_info.get('smart_contract_features', ['N/A']))}
- Technology Stack: {', '.join(tech_info.get('technology_stack', ['N/A']))}
- Audit Status: {', '.join(tech_info.get('audit_reports', ['Pending']))}

Market Information:
- Target Markets: {', '.join(market_info.get('target_markets', ['Global']))}
- Market Position: {market_info.get('market_positioning', 'N/A')}
- Competitor Analysis: {market_info.get('competitor_analysis', 'N/A')}


Project Resources:
- Whitepaper: {campaign_schema.project_whitepaper or "N/A"}
- GitHub: {tech_info.get('github_repository', 'N/A')}
- Documentation: {tech_info.get('documentation', 'N/A')}

Market Context:
{market_context}
"""

        return ProjectInfoPrompt(
            project_name=campaign_schema.project_name,
            project_info=campaign_schema.project_info,
            tokenomics=tokenomics,
            technical_info=tech_info,
            market_info=market_info,
            content=project_content,
            weight=WEIGHTS_DISTRIBUTION["project_info"]
        )

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
            weight=WEIGHTS_DISTRIBUTION["time_awareness"]
        )

    async def _build_memory_component(
        self,
        recent_posts: List[Any],
        stage_posts: List[Any],
        current_stage: PostStage
    ) -> PromptComponent:
        """Build the memory component of the prompt"""
        # Format recent posts with timestamps and engagement metrics
        recent_context = []
        for post in recent_posts:
            engagement = f"(👍 {getattr(post, 'likes', 0)} | 💬 {getattr(post, 'comments', 0)} | 🔄 {getattr(post, 'shares', 0)})"
            timestamp = getattr(post, 'created_at', datetime.now()).strftime("%Y-%m-%d %H:%M")
            recent_context.append(
                f"[{timestamp}] {post.post_stage} Post {engagement}:\n{post.content}\n"
            )

        # Format stage-specific posts with performance metrics
        stage_context = []
        for post in stage_posts:
            performance = "High" if getattr(post, 'engagement_rate', 0) > 0.05 else "Medium" if getattr(post, 'engagement_rate', 0) > 0.02 else "Low"
            stage_context.append(
                f"{post.post_stage} Post (Performance: {performance}):\n{post.content}\n"
            )

        memory_content = f"""POST HISTORY AND CONTEXT

Current Stage: {current_stage.value}

Recent Post History:
{chr(10).join(recent_context) if recent_context else "No recent posts"}

Previous {current_stage.value} Stage Posts:
{chr(10).join(stage_context) if stage_context else f"No previous {current_stage.value} posts"}

Content Guidelines:
1. Maintain Consistency:
   - Build upon themes from recent posts
   - Keep brand voice consistent
   - Reference previous successful elements

2. Avoid Repetition:
   - Don't repeat exact phrases or hooks
   - Vary emotional appeals
   - Use fresh examples/analogies

3. Progress the Narrative:
   - Advance the story from previous posts
   - Build upon established concepts
   - Introduce new angles appropriately

4. Engagement Optimization:
   - Learn from high-performing posts
   - Adapt successful formats
   - Maintain what works, improve what doesn't
"""

        return PromptComponent(
            content=memory_content,
            weight=WEIGHTS_DISTRIBUTION["memory"]
        )

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
            weight=WEIGHTS_DISTRIBUTION["performance"]
        )

    async def _build_platform_component(
        self,
        platform_type: PlatformType,
        settings: CampaignSettings
    ) -> PlatformPrompt:
        """Build the platform-specific component of the prompt"""
        platform_settings = settings.platform_settings.get(platform_type, {})
        constraints = PLATFORM_CONSTRAINTS[platform_type]

        platform_content = f"""PLATFORM GUIDELINES

Platform: {platform_type}
Style Guide: {constraints['style_guide']}

Content Constraints:
- Maximum Length: {constraints['max_length']} characters
- Optimal Length: {constraints['optimal_length']} characters
- Maximum Hashtags: {constraints['max_hashtags']}
- Optimal Hashtags: {constraints['optimal_hashtags']}

Platform Settings:
- Cross Posting: {'Enabled' if settings.cross_posting else 'Disabled'}
- Engagement Hours: {settings.engagement_hours.get('start', '09:00')} to {settings.engagement_hours.get('end', '21:00')} {settings.engagement_hours.get('timezone', 'UTC')}


Custom Platform Settings:
{platform_settings}
"""

        return PlatformPrompt(
            platform_type=platform_type,
            platform_settings=platform_settings,
            content=platform_content,
            weight=WEIGHTS_DISTRIBUTION["platform"]
        )

    async def _build_trending_hooks_component(
        self,
        trending_topics: List[Union[str, TrendingTopic]]
    ) -> TrendingHooksPrompt:
        """Build the trending hooks component with market trends."""
        formatted_topics = []
        hashtags = []

        for topic in trending_topics:
            if isinstance(topic, TrendingTopic):
                formatted_topics.append({
                    "name": topic.name,
                    "volume": topic.volume,
                    "sentiment": topic.sentiment,
                    "source": topic.source
                })
                hashtags.append(f"#{topic.name.replace(' ', '')}")
            else:
                formatted_topics.append({"name": topic})
                hashtags.append(f"#{topic.replace(' ', '')}")

        trending_content = f"""TRENDING TOPICS & MARKET SENTIMENT

Current Trending Topics:
{chr(10).join(f"- {topic['name']}" + (f" (Volume: {topic['volume']:,}, Sentiment: {topic['sentiment']:.2f})" if 'volume' in topic else "") for topic in formatted_topics)}

Relevant Hashtags:
{chr(10).join(f"- {tag}" for tag in hashtags)}

Instructions:
- Incorporate trending topics naturally
- Use hashtags strategically
- Maintain authenticity while leveraging trends
- Ensure trend relevance to project/token
- Consider sentiment when referencing trends
"""

        return TrendingHooksPrompt(
            trending_topics=[t["name"] for t in formatted_topics],
            relevant_hashtags=hashtags,
            content=trending_content,
            weight=WEIGHTS_DISTRIBUTION["trending"]
        )

    async def _build_strategy_component(
        self,
        campaign: Campaign,
        strategy_goal: PostStrategyGoal,
        market_data: Optional[MarketData] = None
    ) -> StrategyPrompt:
        """Build the strategy component with market awareness."""
        campaign_phase = self._determine_campaign_phase(campaign)
        phase_pattern = PHASE_STYLE_PATTERNS[campaign_phase]

        # Format market performance if available
        market_performance = ""
        if market_data:
            price_change = market_data.price_change_24h
            volume_change = market_data.volume_24h
            market_performance = f"""
Market Performance:
- Price: ${market_data.price:.8f}
- 24h Change: {price_change:+.2f}%
- 24h Volume: ${volume_change:,.2f}
- Market Cap: ${market_data.market_cap:,.2f}
"""

        strategy_content = f"""CAMPAIGN STRATEGY

Goal: {strategy_goal.value}
Campaign Phase: {campaign_phase.value}
Current Focus: {phase_pattern['focus']}
Tone: {phase_pattern['tone']}
CTA Strength: {phase_pattern['cta_strength']}
Price Emphasis: {phase_pattern['price_emphasis']}
Technical Detail: {phase_pattern['technical_detail']}

{market_performance}

Key Messages:
{chr(10).join(f"- {msg}" for msg in (campaign.key_messages or []))}

Unique Selling Points:
{chr(10).join(f"- {usp}" for usp in (campaign.unique_selling_points or []))}

Content Guidelines:
{campaign.content_guidelines if campaign.content_guidelines else "No specific content guidelines provided"}

Prohibited Terms:
{chr(10).join(f"- {term}" for term in (campaign.prohibited_terms or []))}

Target Audience:
{chr(10).join(f"- {audience}" for audience in campaign.target_audience)}

Market Positioning:
{campaign.market_positioning if campaign.market_positioning else "Standard market positioning"}
"""

        return StrategyPrompt(
            goal=strategy_goal,
            campaign_phase=campaign_phase,
            key_messages=campaign.key_messages or [],
            content=strategy_content,
            weight=WEIGHTS_DISTRIBUTION["strategy"]
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

    async def _build_all_components(
        self,
        campaign: Campaign,
        settings: CampaignSettings,
        platform_type: PlatformType,
        strategy_goal: PostStrategyGoal,
        trending_hooks: Optional[List[str]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build all prompt components with market awareness."""

        # Determine post stage and style
        stage = await self._determine_post_stage(campaign, context["recent_posts"])
        campaign_phase = self._determine_campaign_phase(campaign)
        post_style = await self._determine_post_style(campaign_phase, context["successful_patterns"])

        # Get stage-specific posts
        stage_posts = await self.social_post_history.get_stage_posts(campaign.id, stage)

        # Build components
        persona = await self._build_persona_component(settings)
        project_info = await self._build_project_info_component(campaign, context["market_data"])
        platform = await self._build_platform_component(platform_type, settings)
        trending = await self._build_trending_hooks_component(trending_hooks or context["trending_topics"])
        strategy = await self._build_strategy_component(campaign, strategy_goal, context["market_data"])
        memory = await self._build_memory_component(context["recent_posts"], stage_posts, stage)
        time_awareness = await self._build_time_awareness_component(context["time_context"])
        performance = await self._build_performance_instructions(context["successful_patterns"], post_style)

        # Combine components
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

        return {
            "prompt": prompt,
            "components": {
                "persona": persona,
                "project_info": project_info,
                "platform": platform,
                "trending": trending,
                "strategy": strategy,
                "memory": memory,
                "performance": performance,
                "time_awareness": time_awareness
            },
            "metadata": {
                "stage": stage,
                "campaign_phase": campaign_phase,
                "post_style": post_style,
                "platform_type": platform_type
            }
        }

    async def _generate_and_process_post(
        self,
        components: Dict[str, Any],
        campaign: Campaign,
        settings: CampaignSettings,
        platform_type: PlatformType,
        context: Dict[str, Any]
    ) -> str:
        """Generate and process a social post with engagement optimization."""

        logger.info(f"\n\nGenerating post with prompt: {components['prompt']}\n\n")

        # Generate initial content
        post_content = await self.llm_provider.generate(components["prompt"])

        # Apply platform-specific formatting
        post_content = self._apply_platform_formatting(
            content=post_content,
            platform_type=platform_type,
            constraints=context["platform_constraints"]
        )

        # Apply anti-detection patterns
        post_content = self.anti_detection.apply_human_like_patterns(
            post_content,
            intensity=settings.ai_creativity_level
        )

        # Store post with analytics setup
        post_id = await self._store_post_with_analytics(
            campaign_id=campaign.id,
            platform_type=platform_type,
            content=post_content,
            metadata=components["metadata"]
        )

        return post_content, post_id

    async def _store_post_with_analytics(
        self,
        campaign_id: int,
        platform_type: PlatformType,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Store post with analytics tracking setup."""
        # Create post

        post = await self.social_post_history.add_social_post(
            campaign_id=campaign_id,
            platform_type=platform_type,
            content=content,
            post_stage=metadata["stage"],
            post_style=metadata["post_style"],
            post_type=PostType.TEXT,
            scheduled_time=self.anti_detection.add_random_silence(datetime.now(), unit="minutes", min_val=1, max_val=10),
            post_metadata={
                "campaign_phase": metadata["campaign_phase"],
                "platform_constraints": PLATFORM_CONSTRAINTS[platform_type]
            }
        )

        # Setup analytics tracking
        analytics = PostAnalytics(
            post_id=post.id,
            campaign_id=campaign_id,
            platform_type=platform_type
        )
        self.db.add(analytics)

        # Setup performance tracking
        performance = PostPerformance(
            post_id=post.id,
            campaign_id=campaign_id,
            platform_type=platform_type,
            content=content,
            post_stage=metadata["stage"].value,
            post_style=metadata["post_style"].value,
            created_at=datetime.now(),
            engagement_metrics={
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "views": 0,
                "clicks": 0,
                "sentiment_score": 0.0,
                "engagement_rate": 0.0,
                "virality_score": 0.0,
                "platform_specific_metrics": {}
            },
            virality_score=0.0,
            engagement_rate=0.0,
            sentiment_score=0.0
        )
        self.db.add(performance)

        # Commit changes
        self.db.commit()

        logger.info(f"Post {post.id} created successfully")

        return post.id

    def _apply_platform_formatting(
        self,
        content: str,
        platform_type: PlatformType,
        constraints: Dict[str, Any]
    ) -> str:
        """Apply platform-specific formatting rules."""
        formatted_content = content

        # Apply length constraints
        # if len(formatted_content) > constraints["max_length"]:
        #     formatted_content = formatted_content[:constraints["optimal_length"]] + "..."

        # Apply platform-specific formatting
        if platform_type == PlatformType.TELEGRAM:
            # Use markdown
            formatted_content = formatted_content.replace("**", "*")  # Bold
            formatted_content = formatted_content.replace("__", "_")  # Italic
        elif platform_type == PlatformType.DISCORD:
            # Use Discord markdown
            formatted_content = formatted_content.replace("*", "**")  # Make bold more visible

        return formatted_content

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
