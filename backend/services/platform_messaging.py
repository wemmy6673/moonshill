from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from tweepy import Client as TweepyClient
from aiogram import Bot
from aiogram.types import InputFile
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.orm import Session
from config.settings import get_settings
from services.logging import init_logger
from schemas.generation import PlatformType, PostStatus
from models.generation import SocialPost
from models.campaigns import Campaign, CampaignSettings
from models.platform_connections import PlatformConnection, ManagedTelegramBot


logger = init_logger()
settings = get_settings()

MAX_PUBLISH_RETRIES = 3  # Define max retries


class PlatformClientError(Exception):
    """Custom exception for platform client errors."""

    def __init__(self, platform: PlatformType, message: str, original_exception: Optional[Exception] = None):
        self.platform = platform
        self.message = message
        self.original_exception = original_exception
        super().__init__(f"[{platform.value}] {message}")


class PlatformClient(ABC):
    """Abstract base class for platform-specific clients."""

    def __init__(self, platform_type: PlatformType):
        self.platform_type = platform_type
        self.logger = logger

    @abstractmethod
    async def send_message(self, target_id: Union[str, int], text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a text message to the specified target (e.g., user, channel, group)."""
        pass

    @abstractmethod
    async def send_media_message(self, target_id: Union[str, int], text: str, media_path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a message with media to the specified target."""
        pass

    @abstractmethod
    async def reply_to_comment(self, original_message_id: str, text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Replies to a specific comment or message."""
        pass

    @abstractmethod
    async def get_message_metrics(self, message_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Fetches metrics for a specific message."""
        pass


class TwitterClient(PlatformClient):
    """Twitter specific client using Tweepy with OAuth 2.0 User Context (Bearer Token)."""

    def __init__(self, user_bearer_token: str):
        super().__init__(PlatformType.TWITTER)
        if not user_bearer_token:
            raise PlatformClientError(self.platform_type, "Twitter User Bearer Token is not provided.")

        try:
            self.client_v2 = TweepyClient(
                bearer_token=user_bearer_token,
                wait_on_rate_limit=True
            )
            self.logger.info("Tweepy client (v2 using user OAuth 2.0 bearer token) initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Tweepy client with bearer token: {e}")
            raise PlatformClientError(self.platform_type, f"Tweepy client (bearer token) initialization failed: {e}", e)

    async def send_message(self, target_id: Union[str, int], text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a tweet using the authenticated user's context via bearer token.
           target_id is not used by tweepy.Client.create_tweet for this purpose."""
        self.logger.info(f"Attempting to send tweet: {text[:50]}...")
        try:
            response = self.client_v2.create_tweet(text=text)
            if response and response.data:
                self.logger.info(f"Tweet sent successfully. ID: {response.data['id']}")
                return {"id": response.data["id"], "text": response.data["text"]}
            self.logger.warning(f"Tweet sending possibly failed, response: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to send tweet: {e}")
            raise PlatformClientError(self.platform_type, f"Failed to send tweet: {e}", e)

    async def send_media_message(self, target_id: Union[str, int], text: str, media_path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a tweet with media. This method needs to be adapted for Twitter API v2 media uploads.
           Tweepy.Client does not have a direct media_upload method like the v1.1 API object.
           You would typically use the /2/media/upload endpoint directly.
        """
        self.logger.error("send_media_message for Twitter is not fully implemented for OAuth 2.0 v2 media uploads yet.")
        raise NotImplementedError(
            "Twitter send_media_message requires custom implementation for v2 media upload endpoint using OAuth 2.0 bearer token."
        )

    async def reply_to_comment(self, original_message_id: str, text: str, **kwargs) -> Optional[Dict[str, Any]]:
        self.logger.info(f"Attempting to reply to tweet ID {original_message_id} with text: {text[:50]}...")
        try:
            response = self.client_v2.create_tweet(
                text=text,
                in_reply_to_tweet_id=original_message_id
            )
            if response and response.data:
                self.logger.info(f"Successfully replied to tweet {original_message_id}. Reply ID: {response.data['id']}")
                return {"id": response.data["id"], "text": response.data["text"], "in_reply_to_tweet_id": original_message_id}
            self.logger.warning(f"Replying to tweet possibly failed, response: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to reply to tweet {original_message_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Failed to reply to tweet {original_message_id}: {e}", e)

    async def get_message_metrics(self, message_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Fetches metrics for a specific tweet using v2 API."""
        self.logger.info(f"Fetching metrics for tweet ID: {message_id}")
        try:
            response = self.client_v2.get_tweet(
                message_id,
                tweet_fields=[
                    "public_metrics", "created_at", "author_id", "conversation_id",
                    "entities", "geo", "lang", "possibly_sensitive", "source"
                ],
            )
            if response and response.data:
                metrics = response.data.get("public_metrics", {})
                self.logger.info(f"Metrics for tweet {message_id}: {metrics}")
                return {
                    "id": str(response.data.get("id")),
                    "text": str(response.data.get("text")),
                    "created_at": str(response.data.get("created_at")),
                    "author_id": str(response.data.get("author_id")),
                    "impression_count": metrics.get("impression_count", 0),
                    "like_count": metrics.get("like_count", 0),
                    "reply_count": metrics.get("reply_count", 0),
                    "retweet_count": metrics.get("retweet_count", 0),
                    "quote_count": metrics.get("quote_count", 0),
                }
            self.logger.warning(f"Fetching metrics for tweet {message_id} possibly failed, response: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get metrics for tweet {message_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Failed to get metrics for tweet {message_id}: {e}", e)


class TelegramClient(PlatformClient):
    """Telegram specific client using Aiogram."""

    def __init__(self, bot_token: str):
        super().__init__(PlatformType.TELEGRAM)
        if not bot_token:
            raise PlatformClientError(self.platform_type, "Telegram Bot Token is not configured.")
        try:
            self.bot = Bot(token=bot_token)
            self.logger.info("Aiogram Bot initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Aiogram Bot: {e}")
            raise PlatformClientError(self.platform_type, f"Aiogram Bot initialization failed: {e}", e)

    async def send_message(self, target_id: Union[str, int], text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a message to a Telegram chat (user, group, or channel)."""
        self.logger.info(f"Attempting to send Telegram message to {target_id}: {text[:50]}...")
        try:
            parse_mode = kwargs.get("parse_mode", "MarkdownV2")
            message = await self.bot.send_message(
                chat_id=target_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=kwargs.get("disable_web_page_preview", False)
            )
            self.logger.info(f"Telegram message sent successfully to {target_id}. Message ID: {message.message_id}")
            return {
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "text": message.text
            }
        except TelegramAPIError as e:
            self.logger.error(f"Failed to send Telegram message to {target_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Telegram API error: {e}", e)
        except Exception as e:
            self.logger.error(f"Unexpected error sending Telegram message to {target_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Unexpected error: {e}", e)

    async def send_media_message(self, target_id: Union[str, int], text: str, media_path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a photo message to a Telegram chat with a caption."""
        self.logger.info(f"Attempting to send Telegram media message to {target_id}, media: {media_path}, caption: {text[:50]}...")
        try:
            parse_mode = kwargs.get("parse_mode", "MarkdownV2")
            photo = InputFile(media_path)
            message = await self.bot.send_photo(
                chat_id=target_id,
                photo=photo,
                caption=text,
                parse_mode=parse_mode
            )
            self.logger.info(f"Telegram media message sent successfully to {target_id}. Message ID: {message.message_id}")
            return {
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "caption": message.caption,
                "photo_id": message.photo[-1].file_id if message.photo else None
            }
        except TelegramAPIError as e:
            self.logger.error(f"Failed to send Telegram media message to {target_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Telegram API error sending media: {e}", e)
        except Exception as e:
            self.logger.error(f"Unexpected error sending Telegram media message to {target_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Unexpected error sending media: {e}", e)

    async def reply_to_comment(self, original_message_id: str, text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Replies to a specific message in a Telegram chat. Requires chat_id in kwargs."""
        chat_id = kwargs.get("chat_id")
        if not chat_id:
            raise PlatformClientError(self.platform_type, "chat_id is required in kwargs to reply to a Telegram message.")

        self.logger.info(f"Attempting to reply to Telegram message ID {original_message_id} in chat {chat_id} with text: {text[:50]}...")
        try:
            parse_mode = kwargs.get("parse_mode", "MarkdownV2")
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=int(original_message_id),
                parse_mode=parse_mode
            )
            self.logger.info(f"Successfully replied to Telegram message {original_message_id} in chat {chat_id}. Reply ID: {message.message_id}")
            return {
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "text": message.text,
                "replied_to_message_id": message.reply_to_message.message_id if message.reply_to_message else None
            }
        except TelegramAPIError as e:
            self.logger.error(f"Failed to reply to Telegram message {original_message_id} in chat {chat_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Telegram API error replying: {e}", e)
        except Exception as e:
            self.logger.error(f"Unexpected error replying to Telegram message {original_message_id} in chat {chat_id}: {e}")
            raise PlatformClientError(self.platform_type, f"Unexpected error replying: {e}", e)

    async def get_message_metrics(self, message_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Telegram Bot API does not directly provide detailed public metrics like tweet impressions or likes for arbitrary messages.
           This method could be used to fetch basic message info or extended if specific bot-user interaction data is stored elsewhere."""
        chat_id = kwargs.get("chat_id")
        self.logger.warning(
            f"Fetching metrics for Telegram message ID {message_id} (in chat {chat_id}) is not directly supported for public view/like counts by standard Bot API."
        )
        return {
            "message_id": message_id,
            "status": "Metrics not directly available via standard Bot API for public interactions. Interaction data must be tracked by the bot."
        }

    async def close(self):
        """Gracefully close the bot session."""
        if self.bot and self.bot.session:
            await self.bot.session.close()
            self.logger.info("Aiogram Bot session closed.")


class PlatformMessagingService:
    """Utility class to interact with different social media platforms using static methods."""

    @staticmethod
    async def _publish_to_twitter(db: Session, scheduled_post: SocialPost, campaign: Campaign, retry_count: int):
        logger.info(f"Attempting to publish to Twitter for post ID: {scheduled_post.id}")
        # Ensure post_metadata exists
        if scheduled_post.post_metadata is None:  # Should have been initialized by publish_post
            scheduled_post.post_metadata = {}

        twitter_connection = (
            db.query(PlatformConnection)
            .filter(
                PlatformConnection.campaign_id == campaign.id,
                PlatformConnection.platform_type == PlatformType.TWITTER,
                PlatformConnection.is_connected == True,
                PlatformConnection.access_token.isnot(None)
            )
            .order_by(PlatformConnection.created_at.desc())
            .first()
        )

        if not (twitter_connection and twitter_connection.access_token):
            reason = "No active/complete Twitter connection (OAuth 2.0 Bearer Token)"
            user_reason = "Could not connect to Twitter. Please check your platform connections for this campaign."
            logger.warning(f"{reason} for campaign {campaign.id}, post {scheduled_post.id}")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return

        logger.info(f"Found Twitter connection ID: {twitter_connection.id} for campaign {campaign.id}")
        try:
            twitter_client = TwitterClient(user_bearer_token=twitter_connection.access_token)
            media_path = scheduled_post.post_metadata.get("media_path") if scheduled_post.post_metadata else None
            message_response = None

            if media_path:
                logger.info(f"Twitter: Post {scheduled_post.id} has media_path: {media_path}")
                try:
                    message_response = await twitter_client.send_media_message(
                        target_id="me", text=scheduled_post.content, media_path=media_path
                    )
                except NotImplementedError:
                    logger.error(f"Twitter: send_media_message not implemented. Post {scheduled_post.id}. Falling back to text-only.")
                    # This specific error doesn't mean a user-facing failure of the *text* post yet.
                    message_response = await twitter_client.send_message(target_id="me", text=scheduled_post.content)
                except Exception as media_e:
                    logger.error(f"Twitter: Error during send_media_message for post {scheduled_post.id}: {media_e}. Falling back to text-only.")
                    # This specific error doesn't mean a user-facing failure of the *text* post yet.
                    message_response = await twitter_client.send_message(target_id="me", text=scheduled_post.content)
            else:
                message_response = await twitter_client.send_message(target_id="me", text=scheduled_post.content)

            if message_response and message_response.get('id'):
                tweet_id = message_response.get('id')
                logger.info(f"Twitter: Successfully posted. Tweet ID: {tweet_id} for post {scheduled_post.id}")
                current_metadata = scheduled_post.post_metadata or {}
                current_metadata["twitter_message_id"] = tweet_id
                current_metadata.pop("failure_reason", None)  # Clear previous failure reasons on success
                current_metadata.pop("user_readable_failure_reason", None)
                db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                    "post_metadata": current_metadata,
                    "status": PostStatus.PUBLISHED
                })
            else:
                reason = f"Failed to send tweet. API Response: {message_response}"
                user_reason = "The post could not be sent to Twitter at this time. The platform may be temporarily unavailable or there might be an issue with the content."
                logger.warning(f"Twitter: {reason} for post {scheduled_post.id}.")
                scheduled_post.post_metadata["failure_reason"] = reason
                scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
                scheduled_post.post_metadata["retry_count"] = retry_count + 1
                db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                    "status": PostStatus.FAILED,
                    "post_metadata": scheduled_post.post_metadata
                })
            db.commit()

        except PlatformClientError as e:
            reason = f"PlatformClientError: {e}"
            user_reason = "An error occurred while communicating with Twitter. Please try again later or check Twitter's status."
            logger.error(f"Twitter: {reason} for post {scheduled_post.id}")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
        except Exception as e:
            reason = f"Unexpected error: {e}"
            user_reason = "An unexpected technical issue occurred while trying to publish to Twitter. Please try again later."
            logger.error(f"Twitter: {reason} for post {scheduled_post.id}")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()

    @staticmethod
    async def _publish_to_telegram(db: Session, scheduled_post: SocialPost, campaign: Campaign, retry_count: int):
        logger.info(f"Attempting to publish to Telegram for post ID: {scheduled_post.id}")
        if scheduled_post.post_metadata is None:
            scheduled_post.post_metadata = {}

        if not campaign.managed_telegram_bot_id:
            reason = "No managed_telegram_bot_id for campaign"
            user_reason = "Telegram bot is not configured for this campaign."
            logger.warning(f"Telegram: {reason} {campaign.id}. Post {scheduled_post.id} set to FAILED.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return

        bot_config = db.query(ManagedTelegramBot).filter(ManagedTelegramBot.id == campaign.managed_telegram_bot_id).first()
        if not (bot_config and bot_config.bot_token):
            reason = f"Bot config/token not found for managed_id {campaign.managed_telegram_bot_id}"
            user_reason = "Telegram bot configuration is incomplete or missing. Please check the platform connections for this campaign."
            logger.warning(f"Telegram: {reason}. Post {scheduled_post.id} set to FAILED.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return

        if not campaign.telegram_chat_ids:
            reason = "No telegram_chat_ids configured for campaign"
            user_reason = "No target Telegram chats are configured for this campaign."
            logger.warning(f"Telegram: {reason} {campaign.id}. Post {scheduled_post.id} set to FAILED.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return

        logger.info(f"Telegram: Found bot config for campaign {campaign.id}. Sending to chats: {campaign.telegram_chat_ids}")
        telegram_client = None
        try:
            telegram_client = TelegramClient(bot_token=bot_config.bot_token)
            sent_ids = scheduled_post.post_metadata.get("telegram_message_ids", {}) if scheduled_post.post_metadata else {}
            success_count = 0
            total_chats = len(campaign.telegram_chat_ids)
            chat_errors = []  # Store errors for individual chats

            for chat_id in campaign.telegram_chat_ids:
                try:
                    response = await telegram_client.send_message(target_id=chat_id, text=scheduled_post.content)
                    if response and response.get('message_id'):
                        msg_id = response.get('message_id')
                        logger.info(f"Telegram: Successfully sent to chat {chat_id}. Message ID: {msg_id} for post {scheduled_post.id}")
                        sent_ids[str(chat_id)] = msg_id
                        success_count += 1
                    else:
                        err_msg = f"Failed to send to chat {chat_id}. Response: {response}"
                        logger.warning(f"Telegram: {err_msg} for post {scheduled_post.id}.")
                        chat_errors.append(err_msg)
                except Exception as e_chat:
                    err_msg = f"Error sending to chat {chat_id}: {e_chat}"
                    logger.error(f"Telegram: {err_msg} for post {scheduled_post.id}")
                    chat_errors.append(err_msg)

            current_metadata = scheduled_post.post_metadata or {}
            if success_count > 0:
                current_metadata["telegram_message_ids"] = sent_ids
                status = PostStatus.PUBLISHED if success_count == total_chats else PostStatus.PARTIALLY_PUBLISHED
                current_metadata.pop("failure_reason", None)  # Clear previous general failure reasons on partial/full success
                current_metadata.pop("user_readable_failure_reason", None)
                if chat_errors:
                    current_metadata["partial_failure_reasons"] = chat_errors  # Store specific chat errors
                db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                    "post_metadata": current_metadata, "status": status
                })
                logger.info(f"Telegram: Post {scheduled_post.id} status updated to {status.value}. Message IDs: {sent_ids}")
            else:
                reason = "No messages successfully sent to any Telegram chat."
                user_reason = "The post could not be sent to any configured Telegram chats."
                if chat_errors:
                    reason += f" Errors: {'; '.join(chat_errors)}"
                    user_reason += " There were issues sending to one or more chats."
                logger.warning(f"Telegram: {reason} for post {scheduled_post.id}. Status set to FAILED.")
                current_metadata["failure_reason"] = reason
                current_metadata["user_readable_failure_reason"] = user_reason
                current_metadata["retry_count"] = retry_count + 1
                db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                    "status": PostStatus.FAILED,
                    "post_metadata": current_metadata
                })
            db.commit()

        except PlatformClientError as e:
            reason = f"PlatformClientError: {e}"
            user_reason = "An error occurred while communicating with Telegram. Please try again later or check Telegram's status."
            logger.error(f"Telegram: {reason} for post {scheduled_post.id}")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
        except Exception as e:
            reason = f"Unexpected error: {e}"
            user_reason = "An unexpected technical issue occurred while trying to publish to Telegram. Please try again later."
            logger.error(f"Telegram: {reason} for post {scheduled_post.id}")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post.id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
        finally:
            if telegram_client and telegram_client.bot and telegram_client.bot.session:
                await telegram_client.close()

    @staticmethod
    async def publish_post(db: Session, scheduled_post_id: int):
        """Fetches a scheduled post and delegates publishing to platform-specific methods,
           handling emergency stops and retry limits."""
        scheduled_post = db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).first()
        if not scheduled_post:
            logger.error(f"PublishPost: Scheduled post not found for ID {scheduled_post_id}. Cannot publish.")
            return

        if scheduled_post.status == PostStatus.PUBLISHED:
            logger.info(f"PublishPost: Post ID {scheduled_post_id} is already published. Skipping.")
            return

        if scheduled_post.status == PostStatus.CANCELLED:
            logger.info(f"PublishPost: Post ID {scheduled_post_id} is already cancelled. Skipping.")
            return

        if scheduled_post.status not in [PostStatus.SCHEDULED, PostStatus.DRAFT]:
            logger.info(f"PublishPost: Post ID {scheduled_post_id} is not scheduled or draft. Skipping.")
            return

        if scheduled_post.post_metadata is None:
            scheduled_post.post_metadata = {}

        campaign = db.query(Campaign).filter(Campaign.id == scheduled_post.campaign_id).first()
        if not campaign:
            reason = "Campaign not found for post"
            user_reason = "The campaign associated with this post could not be found."
            logger.error(f"PublishPost: {reason} (ID: {scheduled_post.campaign_id}) for post {scheduled_post.id}. Post set to FAILED.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return

        campaign_settings = db.query(CampaignSettings).filter(CampaignSettings.campaign_id == campaign.id).first()
        if campaign_settings and campaign_settings.emergency_stop_activated:
            reason = "Emergency stop activated for campaign"
            user_reason = "Publishing has been paused for this campaign due to an emergency stop."
            logger.info(f"PublishPost: {reason} {campaign.id}. Cancelling post {scheduled_post.id}.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = scheduled_post.post_metadata.get("retry_count", 0)
            db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({
                "status": PostStatus.CANCELLED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return
        elif not campaign_settings:
            logger.warning(f"PublishPost: CampaignSettings not found for campaign {campaign.id}. Proceeding without emergency stop check.")

        retry_count = scheduled_post.post_metadata.get("retry_count", 0)
        if retry_count >= MAX_PUBLISH_RETRIES:
            reason = f"Max retries ({MAX_PUBLISH_RETRIES}) reached"
            user_reason = f"The post has failed to publish after {MAX_PUBLISH_RETRIES} attempts and will not be retried."
            logger.warning(f"PublishPost: Post ID {scheduled_post_id} {reason}. Skipping.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({
                "status": PostStatus.CANCELLED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return

        logger.info(
            f"PublishPost: Processing post ID: {scheduled_post.id} (Attempt: {retry_count + 1}) for campaign {campaign.id}, platform: {scheduled_post.platform_type}")

        try:
            post_platform_type = PlatformType(scheduled_post.platform_type)
        except ValueError:
            reason = f"Invalid platform type: {scheduled_post.platform_type}"
            user_reason = f"The platform '{scheduled_post.platform_type}' is not recognized by the system."
            logger.error(f"PublishPost: {reason} for post {scheduled_post_id}. Post set to FAILED.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
            return

        if post_platform_type == PlatformType.TWITTER:
            await PlatformMessagingService._publish_to_twitter(db, scheduled_post, campaign, retry_count)
        elif post_platform_type == PlatformType.TELEGRAM:
            await PlatformMessagingService._publish_to_telegram(db, scheduled_post, campaign, retry_count)
        else:
            reason = f"Unsupported platform: {post_platform_type.value}"
            user_reason = f"Publishing to '{post_platform_type.value}' is not currently supported."
            logger.warning(f"PublishPost: {reason} for post {scheduled_post_id}. Post set to FAILED.")
            scheduled_post.post_metadata["failure_reason"] = reason
            scheduled_post.post_metadata["user_readable_failure_reason"] = user_reason
            scheduled_post.post_metadata["retry_count"] = retry_count + 1
            db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({
                "status": PostStatus.FAILED,
                "post_metadata": scheduled_post.post_metadata
            })
            db.commit()
