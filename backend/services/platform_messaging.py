from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, List
from tweepy import Client as TweepyClient, Media, API as TweepyAPI, OAuth1UserHandler
from aiogram import Bot
from aiogram.types import InputFile
from aiogram.exceptions import TelegramAPIError

from config.settings import get_settings
from services.logging import init_logger
from schemas.generation import PlatformType  # Assuming PlatformType enum exists

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
    """Twitter specific client using Tweepy."""

    def __init__(self):
        super().__init__(PlatformType.TWITTER)
        if not all([
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET_KEY,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        ]):
            raise PlatformClientError(self.platform_type, "Twitter API credentials are not fully configured.")

        try:
            # For v2 API (tweeting, metrics)
            self.client_v2 = TweepyClient(
                bearer_token=settings.TWITTER_BEARER_TOKEN,  # Needed for some v2 endpoints if not using user context for all
                consumer_key=settings.TWITTER_API_KEY,
                consumer_secret=settings.TWITTER_API_SECRET_KEY,
                access_token=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            # For v1.1 API (media uploads)
            auth_v1 = OAuth1UserHandler(
                settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET_KEY,
                settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET
            )
            self.api_v1 = TweepyAPI(auth_v1, wait_on_rate_limit=True)
            self.logger.info("Tweepy clients (v1.1 and v2) initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Tweepy clients: {e}")
            raise PlatformClientError(self.platform_type, f"Tweepy client initialization failed: {e}", e)

    async def send_message(self, target_id: Union[str, int], text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a tweet. target_id is not directly used for sending a basic tweet, uses authenticated user context."""
        self.logger.info(f"Attempting to send tweet: {text[:50]}...")
        try:
            # user_auth=True might be needed if client_v2 was initialized with only bearer_token for user context actions
            response = self.client_v2.create_tweet(text=text, user_auth=True)
            if response and response.data:
                self.logger.info(f"Tweet sent successfully. ID: {response.data['id']}")
                return {"id": response.data["id"], "text": response.data["text"]}
            self.logger.warning(f"Tweet sending possibly failed, response: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to send tweet: {e}")
            raise PlatformClientError(self.platform_type, f"Failed to send tweet: {e}", e)

    async def send_media_message(self, target_id: Union[str, int], text: str, media_path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Sends a tweet with an image. target_id is not directly used, uses authenticated user context."""
        self.logger.info(f"Attempting to send tweet with media: {media_path}, text: {text[:50]}...")
        try:
            # Upload media using v1.1 API
            media = self.api_v1.media_upload(filename=media_path)
            if not media or not media.media_id_string:
                raise PlatformClientError(self.platform_type, "Failed to upload media to Twitter.")
            media_id = media.media_id_string
            self.logger.info(f"Media uploaded successfully to Twitter. Media ID: {media_id}")

            # Send tweet with media_id using v2 API
            response = self.client_v2.create_tweet(text=text, media_ids=[media_id], user_auth=True)
            if response and response.data:
                self.logger.info(f"Tweet with media sent successfully. ID: {response.data['id']}")
                return {"id": response.data["id"], "text": response.data["text"], "media_ids": [media_id]}
            self.logger.warning(f"Tweet with media sending possibly failed, response: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to send tweet with media: {e}")
            raise PlatformClientError(self.platform_type, f"Failed to send tweet with media: {e}", e)

    async def reply_to_comment(self, original_message_id: str, text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Replies to a specific tweet."""
        self.logger.info(f"Attempting to reply to tweet ID {original_message_id} with text: {text[:50]}...")
        try:
            response = self.client_v2.create_tweet(
                text=text,
                in_reply_to_tweet_id=original_message_id,
                user_auth=True
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
                user_auth=True  # May not be needed if bearer token has right permissions
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
                    # "bookmark_count": metrics.get("bookmark_count", 0), # Requires specific access
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

    def __init__(self):
        self.logger = logger
        self.twitter_client: Optional[TwitterClient] = None
        self.telegram_client: Optional[TelegramClient] = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initializes platform clients based on available settings."""
        try:
            if all([
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET_KEY,
                settings.TWITTER_ACCESS_TOKEN,
                settings.TWITTER_ACCESS_TOKEN_SECRET
            ]):
                self.twitter_client = TwitterClient()
                self.logger.info("Twitter client initialized successfully.")
            else:
                self.logger.warning("Twitter API credentials not fully configured. Twitter client not initialized.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {e}")

        try:
            if settings.TELEGRAM_BOT_TOKEN:
                self.telegram_client = TelegramClient(settings.TELEGRAM_BOT_TOKEN)
                self.logger.info("Telegram client initialized successfully.")
            else:
                self.logger.warning("Telegram Bot Token not configured. Telegram client not initialized.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram client: {e}")

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

# Example usage (for testing, to be removed or placed in a test file)


async def main():
    # This assumes you have PlatformType defined in schemas.generation
    # and settings properly configured.
    # from schemas.generation import PlatformType

    service = PlatformMessagingService()

    # Example: Sending a tweet (if configured)
    # if service.twitter_client:
    #     try:
    #         tweet_response = await service.send_message(
    #             platform_type=PlatformType.TWITTER,
    #             target_id="me", # Tweepy uses user context, target_id might not be needed for posting.
    #             text="Hello from my new PlatformMessagingService! #Python #API"
    #         )
    #         if tweet_response:
    #             logger.info(f"Tweet sent successfully: ID {tweet_response.get('id')}")
    #             tweet_id = str(tweet_response.get('id'))
    #             if tweet_id:
    #                 metrics = await service.get_message_metrics(PlatformType.TWITTER, tweet_id)
    #                 logger.info(f"Tweet metrics: {metrics}")
    #     except PlatformClientError as e:
    #         logger.error(f"Twitter operation failed: {e}")
    #     except Exception as e:
    #         logger.error(f"An unexpected error occurred with Twitter: {e}")

    # Example: Sending a Telegram message (if configured)
    # if service.telegram_client:
    #     try:
    #         # Replace YOUR_TELEGRAM_CHAT_ID with an actual chat ID (user, group, or channel)
    #         # Ensure the bot has permissions to send messages to this chat_id.
    #         # For channels, the bot needs to be an administrator with posting rights.
    #         # For groups, the bot needs to be a member.
    #         # For users, they must have initiated a chat with the bot first.
    #         chat_id = settings.TELEGRAM_TEST_CHAT_ID # Fetch from settings or hardcode for testing
    #         if chat_id:
    #              message_response = await service.send_message(
    #                  platform_type=PlatformType.TELEGRAM,
    #                  target_id=chat_id, # User ID, Group ID (negative number), or Channel ID (e.g., '@channelusername')
    #                  text="Hello from PlatformMessagingService via Telegram!"
    #              )
    #              if message_response:
    #                  logger.info(f"Telegram message sent successfully: ID {message_response.get('message_id')}")
    #         else:
    #             logger.warning("TELEGRAM_TEST_CHAT_ID not set. Skipping Telegram send message test.")
    #     except PlatformClientError as e:
    #         logger.error(f"Telegram operation failed: {e}")
    #     except Exception as e:
    #         logger.error(f"An unexpected error occurred with Telegram: {e}")

if __name__ == "__main__":
    import asyncio
    # Make sure to define or import PlatformType before running this
    # Example:
    # from enum import Enum
    # class PlatformType(str, Enum):
    #     TWITTER = "twitter"
    #     TELEGRAM = "telegram"
    #     DISCORD = "discord" # etc.

    # This main function is for demonstration.
    # You'll need to have your settings (API keys, tokens) configured.
    # asyncio.run(main())
    logger.info("PlatformMessagingService structure defined. Implement client methods next.")
