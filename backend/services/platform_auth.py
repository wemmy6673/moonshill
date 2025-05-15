from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import tweepy
import secrets
import json
from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from models.platform_connections import PlatformConnection
from schemas.platform_connections import PlatformType
from config.settings import get_settings
from utils.pure_funcs import get_now
settings = get_settings()


class PlatformAuthService:
    def __init__(self, db: Session):
        self.db = db

        # Twitter OAuth 2.0 settings
        self.twitter_client_id = settings.twitter_client_id
        self.twitter_client_secret = settings.twitter_client_secret

        # Discord OAuth2 settings
        self.discord_client_id = settings.discord_client_id
        self.discord_client_secret = settings.discord_client_secret

        # Telegram settings
        self.telegram_bot_token = settings.telegram_bot_token

    def generate_state_token(self) -> str:
        """Generate a secure state token for CSRF protection"""
        return secrets.token_urlsafe(32)

    async def initiate_twitter_connection(self, callback_url: HttpUrl) -> Tuple[str, str]:
        """
        Initialize Twitter OAuth 2.0 flow
        Returns (auth_url, state_token)
        """
        oauth2_user_handler = tweepy.OAuth2UserHandler(
            client_id=self.twitter_client_id,
            client_secret=self.twitter_client_secret,
            redirect_uri=str(callback_url),
            scope=['tweet.read', 'tweet.write', 'users.read', 'offline.access']
        )

        state = self.generate_state_token()
        auth_url = oauth2_user_handler.get_authorization_url()

        return auth_url, state

    async def verify_twitter_callback(
        self,
        code: str,
        workspace_id: int,
        campaign_id: int,
        state: str,
        expected_state: str
    ) -> PlatformConnection:
        """Verify Twitter OAuth callback and store connection"""
        if state != expected_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state token"
            )

        try:
            oauth2_user_handler = tweepy.OAuth2UserHandler(
                client_id=self.twitter_client_id,
                client_secret=self.twitter_client_secret
            )

            # Get access token
            access_token = oauth2_user_handler.fetch_token(code)

            # Initialize client with access token
            client = tweepy.Client(access_token['access_token'])

            # Get user info
            user = client.get_me()

            # Create or update platform connection
            platform_conn = self.db.query(PlatformConnection).filter(
                PlatformConnection.workspace_id == workspace_id,
                PlatformConnection.campaign_id == campaign_id,
                PlatformConnection.platform == PlatformType.TWITTER
            ).first()

            if not platform_conn:
                platform_conn = PlatformConnection(
                    workspace_id=workspace_id,
                    campaign_id=campaign_id,
                    platform=PlatformType.TWITTER
                )
                self.db.add(platform_conn)

            # Update connection details
            platform_conn.is_connected = True
            platform_conn.connected_at = get_now()
            platform_conn.platform_user_id = str(user.data.id)
            platform_conn.platform_username = user.data.username
            platform_conn.access_token = access_token['access_token']
            platform_conn.refresh_token = access_token.get('refresh_token')
            platform_conn.token_expires_at = get_now() + timedelta(seconds=access_token['expires_in'])
            platform_conn.platform_metadata = {
                'name': user.data.name,
                'verified': user.data.verified,
                'profile_image_url': user.data.profile_image_url
            }

            self.db.commit()
            self.db.refresh(platform_conn)

            return platform_conn

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to verify Twitter connection: {str(e)}"
            )

    async def initiate_telegram_connection(self, callback_url: HttpUrl) -> Tuple[str, str]:
        """
        Initialize Telegram OAuth flow
        For Telegram, we'll use the bot token flow
        """
        state = self.generate_state_token()

        # Telegram uses a different approach - we'll return a deep link to the bot
        auth_url = f"https://t.me/{settings.telegram_bot_username}?start={state}"

        return auth_url, state

    async def verify_telegram_callback(
        self,
        user_data: Dict,
        workspace_id: int,
        campaign_id: int,
        state: str,
        expected_state: str
    ) -> PlatformConnection:
        """Verify Telegram callback and store connection"""
        # Implementation will depend on your Telegram bot setup
        pass

    async def initiate_discord_connection(self, callback_url: HttpUrl) -> Tuple[str, str]:
        """
        Initialize Discord OAuth2 flow
        Returns (auth_url, state_token)
        """
        state = self.generate_state_token()

        # Construct Discord OAuth2 URL
        discord_auth_url = (
            "https://discord.com/api/oauth2/authorize"
            f"?client_id={self.discord_client_id}"
            "&response_type=code"
            "&scope=identify%20bot"
            f"&state={state}"
            f"&redirect_uri={str(callback_url)}"
            "&permissions=2147483648"  # Adjust permissions as needed
        )

        return discord_auth_url, state

    async def verify_discord_callback(
        self,
        code: str,
        workspace_id: int,
        campaign_id: int,
        state: str,
        expected_state: str
    ) -> PlatformConnection:
        """Verify Discord OAuth callback and store connection"""
        # Implementation will be added in the next iteration
        pass
