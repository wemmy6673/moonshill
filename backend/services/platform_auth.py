from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import tweepy
import secrets
import base64
import json
from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from models.platform_connections import PlatformConnection
from schemas.platform_connections import PlatformType
from config.settings import get_settings
from utils.pure_funcs import get_now
from services.logging import init_logger

settings = get_settings()
logger = init_logger()


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

    async def initiate_twitter_connection(self, callback_url: HttpUrl, campaign_id: int, workspace_id: int) -> str:
        """
        Initialize Twitter OAuth 2.0 flow
        Returns auth_url
        """
        logger.info(f"Initiating Twitter connection for callback_url: {callback_url}")
        nonce = self.generate_state_token()

        scope = ['tweet.read', 'tweet.write', 'offline.access', 'follows.read']

        platform_conn = PlatformConnection(
            workspace_id=workspace_id,
            campaign_id=campaign_id,
            platform=PlatformType.TWITTER,
            nonce=nonce,
            scope=' '.join(scope),
            redirect_uri=str(callback_url)
        )
        self.db.add(platform_conn)
        self.db.commit()
        self.db.refresh(platform_conn)

        oauth2_user_handler = tweepy.OAuth2UserHandler(
            client_id=self.twitter_client_id,
            client_secret=self.twitter_client_secret,
            redirect_uri=str(callback_url),
            scope=scope,
        )

        state = base64.urlsafe_b64encode(json.dumps({
            "nonce": nonce,
            "campaign_id": campaign_id,
            "connection_id": platform_conn.id,
            # "verifier": oauth2_user_handler.code_verifier
        }).encode('utf-8')).decode('utf-8')

        oauth2_user_handler.state = state

        auth_url = oauth2_user_handler.get_authorization_url()

        return auth_url

    async def verify_twitter_callback(
        self,
        auth_res_url: HttpUrl,
        workspace_id: int,
        state: str,
    ) -> PlatformConnection:
        """Verify Twitter OAuth callback and store connection"""

        try:
            logger.info(f"Verifying Twitter callback for workspace_id: {workspace_id}")

            decoded_state = json.loads(base64.urlsafe_b64decode(state.encode('utf-8')).decode('utf-8'))

            if not all(key in decoded_state for key in ["nonce", "campaign_id", "connection_id"]):
                logger.error("Required keys not found in decoded state, returning 400")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state token"
                )

            platform_conn = self.db.query(PlatformConnection).filter(
                PlatformConnection.id == decoded_state.get("connection_id"),
                PlatformConnection.nonce == decoded_state.get("nonce"),
                PlatformConnection.campaign_id == decoded_state.get("campaign_id"),
                PlatformConnection.platform == PlatformType.TWITTER,
                PlatformConnection.workspace_id == workspace_id
            ).first()

            if not platform_conn:
                logger.error("Platform connection not found, returning 400")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state token"
                )

        except Exception as e:
            logger.error(f"Failed to decode state: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode state: {str(e)}"
            )

        try:
            oauth2_user_handler = tweepy.OAuth2UserHandler(
                client_id=self.twitter_client_id,
                client_secret=self.twitter_client_secret,
                redirect_uri=platform_conn.redirect_uri,
                scope=platform_conn.scope.split(' '),

            )

            oauth2_user_handler.code_verifier = decoded_state.get("verifier")

            # Get access token
            access_token = oauth2_user_handler.fetch_token(str(auth_res_url))

            # Initialize client with access token
            client = tweepy.Client(access_token["access_token"])

            # Get user info
            user = client.get_me()

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
            logger.error(f"Failed to verify Twitter connection: {str(e)}")
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
    ) -> PlatformConnection:
        """Verify Discord OAuth callback and store connection"""
        # Implementation will be added in the next iteration
        pass
