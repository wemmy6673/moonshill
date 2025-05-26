from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, List
from tweepy import Client as TweepyClient, Media, API as TweepyAPI, OAuth1UserHandler
from aiogram import Bot
from aiogram.types import InputFile
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.orm import Session
from config.settings import get_settings
from services.logging import init_logger
from schemas.generation import PlatformType, PostStatus
from models.generation import SocialPost
from models.campaigns import Campaign
from models.platform_connections import PlatformConnection, ManagedTelegramBot

logger = init_logger()
settings = get_settings()


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
            # When TweepyClient is initialized with a user context bearer token,
            # user_auth=True is implied for operations like create_tweet.
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
        # Placeholder for future implementation:
        # 1. Upload media to /2/media/upload (e.g., using requests or another HTTP client)
        #    - This involves a multi-part form data request if file is large, or simple POST.
        #    - The request must be authorized with the user_bearer_token.
        #    - This endpoint returns a media_id.
        # 2. Call self.client_v2.create_tweet(text=text, media_ids=[media_id_from_step_1])

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
            # Specify which fields you want for the tweet
            # Full list: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
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
                # You can expand this to return more data from the response if needed
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
            # Determine parse_mode (MarkdownV2 or HTML)
            parse_mode = kwargs.get("parse_mode", "MarkdownV2")  # Default to MarkdownV2

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
                "photo_id": message.photo[-1].file_id if message.photo else None  # Get largest photo
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
        chat_id = kwargs.get("chat_id")  # Chat ID would be needed to identify the message context for some actions
        self.logger.warning(
            f"Fetching metrics for Telegram message ID {message_id} (in chat {chat_id}) is not directly supported for public view/like counts by standard Bot API.")
        # For example, you could check if a message exists or get its basic info if your bot sent it.
        # If you store interactions (e.g., button clicks, poll votes tied to a message_id) in your DB,
        # you could query that here.
        # This is a placeholder, as Telegram's bot API focuses on interactions rather than public broadcast metrics.
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
    """Service to interact with different social media platforms."""

    def __init__(self,
                 twitter_bearer_token: Optional[str] = None,
                 telegram_bot_token: Optional[str] = None):
        self.logger = logger
        self.twitter_client: Optional[TwitterClient] = None
        self.telegram_client: Optional[TelegramClient] = None
        self._initialize_clients(
            twitter_bearer_token=twitter_bearer_token,
            telegram_bot_token=telegram_bot_token
        )

    def _initialize_clients(self,
                            twitter_bearer_token: Optional[str] = None,
                            telegram_bot_token: Optional[str] = None):
        """Initializes platform clients based on available tokens."""
        if twitter_bearer_token:
            try:
                self.twitter_client = TwitterClient(user_bearer_token=twitter_bearer_token)
                self.logger.info("Twitter client initialized successfully for PlatformMessagingService instance (OAuth 2.0 User Bearer Token).")
            except Exception as e:
                self.logger.error(f"Failed to initialize Twitter client for PlatformMessagingService instance: {e}")
        else:
            self.logger.info("Twitter user bearer token not provided to PlatformMessagingService. Twitter client not initialized for this instance.")

        if telegram_bot_token:
            try:
                self.telegram_client = TelegramClient(telegram_bot_token)
                self.logger.info("Telegram client initialized successfully for PlatformMessagingService instance.")
            except Exception as e:
                self.logger.error(f"Failed to initialize Telegram client for PlatformMessagingService instance: {e}")
        else:
            self.logger.info("Telegram bot token not provided to PlatformMessagingService. Telegram client not initialized for this instance.")

    def _get_client(self, platform_type: PlatformType) -> PlatformClient:
        """Returns the appropriate client for the given platform type."""
        if platform_type == PlatformType.TWITTER:
            if not self.twitter_client:
                raise PlatformClientError(PlatformType.TWITTER, "Twitter client not initialized or configured.")
            return self.twitter_client
        elif platform_type == PlatformType.TELEGRAM:
            if not self.telegram_client:
                raise PlatformClientError(PlatformType.TELEGRAM, "Telegram client not initialized or configured.")
            return self.telegram_client
        else:
            raise NotImplementedError(f"Platform {platform_type.value} is not supported.")

    async def send_message(self, platform_type: PlatformType, target_id: Union[str, int], text: str, **kwargs) -> Optional[Dict[str, Any]]:
        client = self._get_client(platform_type)
        return await client.send_message(target_id, text, **kwargs)

    async def send_media_message(self, platform_type: PlatformType, target_id: Union[str, int], text: str, media_path: str, **kwargs) -> Optional[Dict[str, Any]]:
        client = self._get_client(platform_type)
        return await client.send_media_message(target_id, text, media_path, **kwargs)

    async def reply_to_comment(self, platform_type: PlatformType, original_message_id: str, text: str, **kwargs) -> Optional[Dict[str, Any]]:
        client = self._get_client(platform_type)
        return await client.reply_to_comment(original_message_id, text, **kwargs)

    async def get_message_metrics(self, platform_type: PlatformType, message_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        client = self._get_client(platform_type)
        return await client.get_message_metrics(message_id, **kwargs)

    @staticmethod
    async def publish_post(db: Session, scheduled_post_id: int):
        """Sends a scheduled social post to its designated platform(s) using campaign-specific credentials."""
        scheduled_post = db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).first()

        if not scheduled_post:
            logger.error(f"Scheduled post not found for ID {scheduled_post_id}")
            raise ValueError(f"Scheduled post not found for ID {scheduled_post_id}")

        campaign = db.query(Campaign).filter(Campaign.id == scheduled_post.campaign_id).first()
        if not campaign:
            logger.error(f"Campaign not found for scheduled post {scheduled_post_id} (campaign_id: {scheduled_post.campaign_id})")
            raise ValueError(f"Campaign not found for scheduled post {scheduled_post_id}")

        logger.info(f"Processing scheduled post ID: {scheduled_post.id} for campaign ID: {campaign.id} to platform: {scheduled_post.platform_type}")

        post_platform_type = PlatformType(scheduled_post.platform_type)  # Ensure it's an enum member

        if post_platform_type == PlatformType.TWITTER:
            twitter_connection = (
                db.query(PlatformConnection)
                .filter(
                    PlatformConnection.campaign_id == campaign.id,
                    PlatformConnection.platform_type == PlatformType.TWITTER,
                    PlatformConnection.is_connected == True,
                    PlatformConnection.access_token.isnot(None)  # This is the user's bearer token for OAuth 2.0
                )
                .order_by(PlatformConnection.created_at.desc())
                .first()
            )

            if twitter_connection and twitter_connection.access_token:
                logger.info(f"Found active Twitter connection ID: {twitter_connection.id} (using OAuth 2.0 Bearer Token) for campaign {campaign.id}")
                try:
                    twitter_client = TwitterClient(user_bearer_token=twitter_connection.access_token)

                    # Check if media is associated with the post (e.g., via post_metadata or a dedicated field)
                    media_path = scheduled_post.post_metadata.get("media_path") if scheduled_post.post_metadata else None
                    message_response = None

                    if media_path:
                        logger.info(f"Attempting to send tweet WITH MEDIA for post {scheduled_post.id}. Media path: {media_path}")
                        try:
                            # This will currently raise NotImplementedError as per TwitterClient.send_media_message
                            message_response = await twitter_client.send_media_message(
                                target_id="me",
                                text=scheduled_post.content,
                                media_path=media_path
                            )
                            logger.info(f"send_media_message for Twitter was called for post {scheduled_post.id}.")
                        except NotImplementedError as nie:
                            logger.error(
                                f"Twitter send_media_message is not implemented for v2 OAuth 2.0. Post {scheduled_post.id} will be sent without media if possible, or fail. Error: {nie}")
                            # Decide if you want to send without media or mark as failed
                            logger.info(
                                f"Falling back to sending tweet WITHOUT MEDIA for post {scheduled_post.id} due to send_media_message not being implemented.")
                            message_response = await twitter_client.send_message(target_id="me", text=scheduled_post.content)
                        except Exception as media_e:
                            logger.error(f"Error during Twitter send_media_message for post {scheduled_post.id}: {media_e}. Attempting to send as text-only.")
                            message_response = await twitter_client.send_message(target_id="me", text=scheduled_post.content)
                    else:
                        logger.info(f"Attempting to send tweet WITHOUT MEDIA for post {scheduled_post.id}.")
                        message_response = await twitter_client.send_message(target_id="me", text=scheduled_post.content)

                    if message_response and message_response.get('id'):
                        tweet_id = message_response.get('id')
                        logger.info(f"Tweet (text or fallback) sent successfully: ID {tweet_id} for scheduled post {scheduled_post.id}")
                        current_metadata = scheduled_post.post_metadata or {}
                        current_metadata["twitter_message_id"] = tweet_id
                        db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({
                            "post_metadata": current_metadata,
                            "status": PostStatus.PUBLISHED
                        })
                        db.commit()
                    else:
                        logger.warning(f"Failed to send tweet for scheduled post {scheduled_post.id}. Response: {message_response}")
                        db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                        db.commit()
                except PlatformClientError as e:
                    logger.error(f"Twitter client error for campaign {campaign.id}, post {scheduled_post.id}: {e}")
                    db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                    db.commit()
                except Exception as e:
                    logger.error(f"Unexpected error sending tweet for campaign {campaign.id}, post {scheduled_post.id}: {e}")
                    db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                    db.commit()
            else:
                logger.warning(
                    f"No active or complete Twitter connection (with OAuth 2.0 Bearer Token) found for campaign {campaign.id} for post {scheduled_post.id}")
                db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                db.commit()

        elif post_platform_type == PlatformType.TELEGRAM:
            if not campaign.managed_telegram_bot_id:
                logger.warning(f"Campaign {campaign.id} does not have a managed_telegram_bot_id. Skipping Telegram post {scheduled_post.id}.")
                db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                db.commit()
                return

            telegram_bot_config = db.query(ManagedTelegramBot).filter(ManagedTelegramBot.id == campaign.managed_telegram_bot_id).first()

            if not telegram_bot_config or not telegram_bot_config.bot_token:
                logger.warning(
                    f"Telegram bot configuration or token not found for managed_telegram_bot_id: {campaign.managed_telegram_bot_id} (Campaign: {campaign.id}). Skipping post {scheduled_post.id}."
                )
                db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                db.commit()
                return

            if not campaign.telegram_chat_ids:  # Assuming this is a list of target chat IDs
                logger.warning(f"No Telegram chat IDs configured for campaign {campaign.id}. Skipping Telegram post {scheduled_post.id}.")
                db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                db.commit()
                return

            logger.info(f"Found Telegram bot config for campaign {campaign.id}. Attempting to send to chat IDs: {campaign.telegram_chat_ids}")
            telegram_client = None  # Define for finally block
            try:
                telegram_client = TelegramClient(bot_token=telegram_bot_config.bot_token)
                sent_message_ids = scheduled_post.post_metadata.get("telegram_message_ids", {}) if scheduled_post.post_metadata else {}
                success_count = 0
                total_chats = len(campaign.telegram_chat_ids)

                for chat_id in campaign.telegram_chat_ids:
                    try:
                        message_response = await telegram_client.send_message(target_id=chat_id, text=scheduled_post.content)
                        if message_response and message_response.get('message_id'):
                            msg_id = message_response.get('message_id')
                            logger.info(f"Telegram message sent successfully to chat {chat_id}: ID {msg_id} for post {scheduled_post.id}")
                            sent_message_ids[str(chat_id)] = msg_id
                            success_count += 1
                        else:
                            logger.warning(f"Failed to send Telegram message for post {scheduled_post.id} to chat {chat_id}. Response: {message_response}")
                    except PlatformClientError as e_chat:
                        logger.error(f"Telegram client error sending to chat {chat_id} for post {scheduled_post.id}: {e_chat}")
                    except Exception as e_gen_chat:
                        logger.error(f"Unexpected error sending to Telegram chat {chat_id} for post {scheduled_post.id}: {e_gen_chat}")

                if success_count > 0:
                    current_metadata = scheduled_post.post_metadata or {}
                    current_metadata["telegram_message_ids"] = sent_message_ids
                    update_payload = {"post_metadata": current_metadata}
                    if success_count == total_chats:
                        update_payload["status"] = PostStatus.PUBLISHED
                    else:
                        update_payload["status"] = PostStatus.PARTIALLY_PUBLISHED

                    db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update(update_payload)
                    db.commit()
                    logger.info(f"Updated Telegram message IDs for scheduled post {scheduled_post.id}: {sent_message_ids}")
                else:
                    logger.warning(f"No Telegram messages were successfully sent for post {scheduled_post.id} for campaign {campaign.id}")
                    db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                    db.commit()

            except PlatformClientError as e:
                logger.error(f"Telegram client setup error for campaign {campaign.id}, post {scheduled_post.id}: {e}")
                db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                db.commit()
            except Exception as e:
                logger.error(f"Unexpected error processing Telegram post for campaign {campaign.id}, post {scheduled_post.id}: {e}")
                db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
                db.commit()
            finally:
                if telegram_client and telegram_client.bot and telegram_client.bot.session:
                    await telegram_client.close()  # Gracefully close session
        else:
            logger.warning(
                f"Platform type {scheduled_post.platform_type} for post {scheduled_post.id} is not currently handled by send_scheduled_post_to_platforms."
            )
            db.query(SocialPost).filter(SocialPost.id == scheduled_post_id).update({"status": PostStatus.FAILED})
            db.commit()
