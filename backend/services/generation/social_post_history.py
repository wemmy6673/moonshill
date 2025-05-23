from typing import Optional, List, Dict, Any
from sqlalchemy import desc
from datetime import datetime
from services.logging import init_logger
from config.settings import get_settings
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session
from models.generation import SocialPost
from schemas.generation import PlatformType, PostStage, PostStyle, PostType, PostStatus
import traceback

logger = init_logger()
settings = get_settings()


class SocialPostHistoryService:
    """Service for managing social media post history across platforms"""

    def __init__(self, db: Session):
        self.db = db
        logger.info("Initialized SocialPostHistoryService")

    async def add_social_post(
        self,
        campaign_id: int,
        platform_type: PlatformType,
        content: str,
        post_stage: PostStage,
        post_style: PostStyle,
        post_type: PostType,
        scheduled_time: Optional[datetime] = None,
        embeddings: Optional[List[float]] = None,
        post_metadata: Optional[Dict[str, Any]] = None
    ) -> SocialPost:
        """Add a new social media post to history"""
        try:
            logger.info(f"Adding social post for campaign {campaign_id} on platform {platform_type}")
            logger.debug(f"Post stage: {post_stage}, style: {post_style}, type: {post_type}")

            social_post = SocialPost(
                campaign_id=campaign_id,
                platform_type=platform_type,
                content=content,
                post_stage=post_stage,
                post_style=post_style,
                post_type=post_type,
                status=PostStatus.DRAFT,
                scheduled_time=scheduled_time or datetime.now(),
                created_at=datetime.now(),
                embeddings=embeddings,
                post_metadata=post_metadata or {}
            )

            self.db.add(social_post)
            self.db.commit()
            self.db.refresh(social_post)

            logger.info(f"Successfully added social post with ID: {social_post.id}")
            return social_post

        except sqlalchemy_exc.SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error adding social post: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to add social post to history: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error adding social post: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Unexpected error adding social post: {str(e)}")

    async def get_recent_posts(
        self,
        campaign_id: int,
        platform_type: Optional[PlatformType] = None,
        limit: int = 5
    ) -> List[SocialPost]:
        """Get recent social posts for a campaign, optionally filtered by platform"""
        try:
            logger.info(f"Getting recent posts for campaign {campaign_id}, platform: {platform_type}, limit: {limit}")

            query = self.db.query(SocialPost)\
                .filter(SocialPost.campaign_id == campaign_id)

            if platform_type:
                query = query.filter(SocialPost.platform_type == platform_type)

            posts = query\
                .order_by(desc(SocialPost.created_at))\
                .limit(limit)\
                .all()

            logger.info(f"Retrieved {len(posts)} recent posts")
            return posts

        except sqlalchemy_exc.SQLAlchemyError as e:
            logger.error(f"Database error getting recent posts: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to get recent posts: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting recent posts: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Unexpected error getting recent posts: {str(e)}")

    async def get_stage_posts(
        self,
        campaign_id: int,
        post_stage: PostStage,
        platform_type: Optional[PlatformType] = None,
        limit: int = 3
    ) -> List[SocialPost]:
        """Get recent posts for a specific stage, optionally filtered by platform"""
        try:
            logger.info(f"Getting {post_stage} stage posts for campaign {campaign_id}")

            query = self.db.query(SocialPost)\
                .filter(
                    SocialPost.campaign_id == campaign_id,
                    SocialPost.post_stage == post_stage
            )

            if platform_type:
                query = query.filter(SocialPost.platform_type == platform_type)

            posts = query\
                .order_by(desc(SocialPost.created_at))\
                .limit(limit)\
                .all()

            logger.info(f"Retrieved {len(posts)} {post_stage} stage posts")
            return posts

        except sqlalchemy_exc.SQLAlchemyError as e:
            logger.error(f"Database error getting stage posts: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to get stage posts: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting stage posts: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Unexpected error getting stage posts: {str(e)}")

    async def get_scheduled_posts(
        self,
        campaign_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[SocialPost]:
        """Get posts scheduled between start_time and end_time"""
        try:
            logger.info(f"Getting scheduled posts for campaign {campaign_id} between {start_time} and {end_time}")

            posts = self.db.query(SocialPost)\
                .filter(
                    SocialPost.campaign_id == campaign_id,
                    SocialPost.scheduled_time >= start_time,
                    SocialPost.scheduled_time <= end_time
            )\
                .order_by(SocialPost.scheduled_time)\
                .all()

            logger.info(f"Retrieved {len(posts)} scheduled posts")
            return posts

        except sqlalchemy_exc.SQLAlchemyError as e:
            logger.error(f"Database error getting scheduled posts: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to get scheduled posts: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting scheduled posts: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Unexpected error getting scheduled posts: {str(e)}")

    async def update_post_status(
        self,
        post_id: int,
        status: PostStatus,
        engagement_metrics: Optional[Dict[str, Any]] = None
    ) -> SocialPost:
        """Update the status and engagement metrics of a post"""
        try:
            logger.info(f"Updating status for post {post_id} to {status}")

            post = self.db.query(SocialPost)\
                .filter(SocialPost.id == post_id)\
                .first()

            if not post:
                raise Exception(f"Post {post_id} not found")

            post.status = status
            if engagement_metrics:
                post.engagement_metrics = engagement_metrics
                post.last_updated = datetime.now()

            self.db.commit()
            self.db.refresh(post)

            logger.info(f"Successfully updated post {post_id} status to {status}")
            return post

        except sqlalchemy_exc.SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating post status: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Failed to update post status: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error updating post status: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Unexpected error updating post status: {str(e)}")
