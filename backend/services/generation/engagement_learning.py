from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from models.generation import PostPerformance, SocialPost
from services.logging import init_logger
from config.settings import get_settings
import numpy as np
import traceback

settings = get_settings()
logger = init_logger()


class EngagementLearningService:
    """Service for learning from engagement metrics"""

    def __init__(self, db: Session):
        self.db = db
        self.performance_threshold = 0.6  # Minimum virality score to consider successful

    async def analyze_performance(
        self,
        campaign_id: int,
        limit: int = 100
    ) -> Tuple[List[PostPerformance], List[PostPerformance]]:
        """Analyze message performance and separate successful from unsuccessful messages"""
        try:
            # Get recent messages with engagement metrics
            messages = await self._get_recent_performance(campaign_id, limit)

            # Separate successful and unsuccessful messages
            successful = []
            unsuccessful = []

            for msg in messages:
                if msg.virality_score >= self.performance_threshold:
                    successful.append(msg)
                else:
                    unsuccessful.append(msg)

            logger.info(f"Analyzed {len(messages)} messages: {len(successful)} successful, {len(unsuccessful)} unsuccessful")
            return successful, unsuccessful

        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to analyze performance: {str(e)}")

    async def get_successful_patterns(
        self,
        successful_messages: List[PostPerformance]
    ) -> Dict[str, Any]:
        """Extract patterns from successful messages"""
        try:
            if not successful_messages:
                return {}

            patterns = {
                'stages': {},
                'styles': {},
                'common_phrases': [],
                'engagement_by_time': {},
                'top_embeddings': []
            }

            # Analyze stage distribution
            for msg in successful_messages:
                patterns['stages'][msg.post_stage] = patterns['stages'].get(msg.post_stage, 0) + 1
                patterns['styles'][msg.post_style] = patterns['styles'].get(msg.post_style, 0) + 1

                # Track engagement by time of day
                hour = msg.created_at.hour
                patterns['engagement_by_time'][hour] = patterns['engagement_by_time'].get(hour, 0) + \
                    msg.engagement_rate

            # Normalize stage and style distributions
            total = len(successful_messages)
            patterns['stages'] = {k: v/total for k, v in patterns['stages'].items()}
            patterns['styles'] = {k: v/total for k, v in patterns['styles'].items()}

            # Get top performing embeddings
            if successful_messages and any(msg.embeddings for msg in successful_messages):
                embeddings = np.array([msg.embeddings for msg in successful_messages if msg.embeddings])
                avg_embedding = np.mean(embeddings, axis=0)
                patterns['top_embeddings'] = avg_embedding.tolist()

            logger.info(f"Extracted patterns from {len(successful_messages)} successful messages")
            return patterns

        except Exception as e:
            logger.error(f"Error extracting patterns: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to extract patterns: {str(e)}")

    async def _get_recent_performance(
        self,
        campaign_id: int,
        limit: int
    ) -> List[PostPerformance]:
        """Get recent message performance data"""
        try:
            # Query performance data
            performances = self.db.query(PostPerformance)\
                .filter(PostPerformance.campaign_id == campaign_id)\
                .order_by(desc(PostPerformance.created_at))\
                .limit(limit)\
                .all()

            logger.info(f"Retrieved {len(performances)} recent performances")
            return performances

        except Exception as e:
            logger.error(f"Error getting recent performance: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to get recent performance: {str(e)}")

    async def create_performance_record(
        self,
        post: SocialPost,
        engagement_metrics: Dict[str, Any]
    ) -> PostPerformance:
        """Create a new performance record for a post"""
        try:
            performance = PostPerformance(
                post_id=post.id,
                campaign_id=post.campaign_id,
                platform_type=post.platform_type,
                content=post.content,
                post_stage=post.post_stage,
                post_style=post.post_style,
                created_at=post.created_at,
                engagement_metrics=engagement_metrics,
                embeddings=post.embeddings,
                virality_score=engagement_metrics.get('virality_score', 0.0),
                engagement_rate=engagement_metrics.get('engagement_rate', 0.0),
                sentiment_score=engagement_metrics.get('sentiment_score', 0.0)
            )

            self.db.add(performance)
            self.db.commit()
            self.db.refresh(performance)

            logger.info(f"Created performance record for post {post.id}")
            return performance

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating performance record: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to create performance record: {str(e)}")
