from typing import Tuple
from datetime import timedelta
import tweepy
import secrets
import base64
import json
from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from models.platform_connections import PlatformConnection, ManagedTelegramBot
from models.campaigns import Campaign
from schemas.platform_connections import PlatformType
from schemas.enums import CampaignStatus
from config.settings import get_settings
from utils.pure_funcs import get_now
from services.logging import init_logger
from authlib.integrations.requests_client import OAuth2Session
import base64
import hashlib
import secrets
import json
from urllib.parse import urlparse, parse_qs

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

    def generate_pkce(self):
        verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip("=")
        return verifier, challenge

    async def initiate_twitter_connection(self, callback_url: HttpUrl, campaign_id: int, workspace_id: int) -> str:
        """
        Initialize Twitter OAuth 2.0 flow
        Returns auth_url
        """
        logger.info(f"Initiating Twitter connection for callback_url: {callback_url}")
        nonce = self.generate_state_token()

        AUTHORIZE_URL = "https://twitter.com/i/oauth2/authorize"

        scope = ['tweet.read', 'tweet.write', 'offline.access', 'follows.read', 'users.read']

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

        verifier, challenge = self.generate_pkce()

        state = base64.urlsafe_b64encode(json.dumps({
            "nonce": nonce,
            "campaign_id": campaign_id,
            "connection_id": platform_conn.id,
            "verifier": verifier,
        }).encode('utf-8')).decode('utf-8')

        client = OAuth2Session(
            client_id=self.twitter_client_id,
            client_secret=self.twitter_client_secret,
            redirect_uri=str(callback_url),
            scope=scope,
            code_challenge=challenge,
            code_challenge_method="S256",
        )

        auth_url = client.create_authorization_url(AUTHORIZE_URL, state=state, code_verifier=verifier)[0]

        logger.info(f"Twitter auth URL: {auth_url}")

        return auth_url

    async def verify_twitter_callback(
        self,
        auth_res_url: HttpUrl,
        workspace_id: int,
        state: str,
    ) -> PlatformConnection:
        """Verify Twitter OAuth callback and store connection"""

        TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

        try:
            logger.info(f"Verifying Twitter callback for workspace_id: {workspace_id}")

            decoded_state = json.loads(base64.urlsafe_b64decode(state.encode('utf-8')).decode('utf-8'))

            if not all(key in decoded_state for key in ["nonce", "campaign_id", "connection_id", "verifier"]):
                logger.error("Required keys not found in decoded state, returning 400")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state token"
                )

            platform_conn = self.db.query(PlatformConnection).filter(
                PlatformConnection.id == int(decoded_state.get("connection_id")),
                PlatformConnection.nonce == decoded_state.get("nonce"),
                PlatformConnection.campaign_id == int(decoded_state.get("campaign_id")),
                PlatformConnection.platform == PlatformType.TWITTER,
                PlatformConnection.workspace_id == workspace_id,
                PlatformConnection.is_connected == False
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
            client = OAuth2Session(
                client_id=self.twitter_client_id,
                client_secret=self.twitter_client_secret,
                redirect_uri=platform_conn.redirect_uri,
                scope=platform_conn.scope.split(' '),
                code_challenge=decoded_state.get("verifier"),
                code_challenge_method="S256",
            )

            parsed = urlparse(str(auth_res_url))
            params = parse_qs(parsed.query)
            code = params["code"][0]

            # Get access token
            access_token = client.fetch_token(TOKEN_URL, authorization_response=str(auth_res_url), state=state,
                                              code_verifier=decoded_state.get("verifier"), code=code)

            # Initialize client with access token
            client = tweepy.Client(bearer_token=access_token["access_token"], consumer_key=self.twitter_client_id, consumer_secret=self.twitter_client_secret)

            # Get user info
            # user = client.get_me()

            # Update connection details
            platform_conn.is_connected = True
            platform_conn.connected_at = get_now()
            # platform_conn.platform_user_id = str(user.data.id)
            # platform_conn.platform_username = user.data.username
            platform_conn.access_token = access_token['access_token']
            platform_conn.refresh_token = access_token.get('refresh_token')
            platform_conn.token_expires_at = get_now() + timedelta(seconds=access_token['expires_in'])
            # platform_conn.platform_metadata = {
            #     'name': user.data.name,
            #     'verified': user.data.verified,
            #     'profile_image_url': user.data.profile_image_url
            # }

            self.db.commit()
            self.db.refresh(platform_conn)

            # delete other platform conn apart from this one
            self.db.query(PlatformConnection).filter(
                PlatformConnection.workspace_id == workspace_id,
                PlatformConnection.campaign_id == platform_conn.campaign_id,
                PlatformConnection.platform == PlatformType.TWITTER,
                PlatformConnection.id != platform_conn.id
            ).delete()

            return platform_conn

        except Exception as e:
            logger.error(f"Failed to verify Twitter connection: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to verify Twitter connection: {str(e)}"
            )

    async def initiate_telegram_connection(self, workspace_id: int, campaign_id: int, callback_url: HttpUrl) -> int:
        """
        Allocate a Telegram bot to a campaign
        """

        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.workspace_id == workspace_id
        ).first()

        if not campaign:
            logger.error(f"Campaign not found for campaign_id: {campaign_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign id"
            )

        if campaign.status not in [CampaignStatus.PENDING, CampaignStatus.PAUSED]:
            logger.error(f"Cannot connect to campaign that is not pending or paused for campaign_id: {campaign_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only connect to campaigns that are pending or paused"
            )

        if campaign.managed_telegram_bot_id:
            logger.error(f"Campaign already has a managed telegram bot for campaign_id: {campaign_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign already has a managed telegram bot"
            )

        # Get all available bots
        subq = (
            select(
                ManagedTelegramBot.id,
                func.count(Campaign.id).label('campaign_count')
            ).outerjoin(ManagedTelegramBot.connected_campaigns)
            .group_by(ManagedTelegramBot.id)
        ).subquery()

        available_bot = (
            self.db.query(ManagedTelegramBot)
            .join(subq, ManagedTelegramBot.id == subq.c.id)
            .filter(
                ManagedTelegramBot.is_active == True,
                ManagedTelegramBot.is_exclusive == False,
                subq.c.campaign_count < ManagedTelegramBot.max_campaigns
            )
            .order_by(ManagedTelegramBot.last_assigned_at.asc())
            .first()
        )

        if not available_bot:
            logger.error(f"No available bots found for campaign {campaign_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available bots found, please try again later"
            )

        # Create a new platform connection
        platform_conn = PlatformConnection(
            workspace_id=workspace_id,
            campaign_id=campaign_id,
            platform=PlatformType.TELEGRAM,
            nonce=self.generate_state_token(),
            scope='',
            redirect_uri=str(callback_url)
        )
        self.db.add(platform_conn)
        self.db.commit()
        self.db.refresh(platform_conn)

        state = base64.urlsafe_b64encode(json.dumps({
            "nonce": platform_conn.nonce,
            "campaign_id": campaign_id,
            "connection_id": platform_conn.id,
            "bot_id": available_bot.id
        }).encode('utf-8')).decode('utf-8')

        auth_url = f"{settings.frontend_url}/platforms/telegram?state={state}"

        return auth_url

    async def verify_telegram_callback(self,  state: str, workspace_id: int, ) -> PlatformConnection:

        try:
            decoded_state = json.loads(base64.urlsafe_b64decode(state.encode('utf-8')).decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to decode state: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode state: {str(e)}"
            )

        if not all(key in decoded_state for key in ["nonce", "campaign_id", "connection_id", "bot_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state token"
            )
        campaign = self.db.query(Campaign).filter(
            Campaign.id == decoded_state.get("campaign_id"),
            Campaign.workspace_id == workspace_id
        ).first()

        if not campaign:
            logger.error(f"Campaign not found for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign id"
            )

        platform_conn = self.db.query(PlatformConnection).filter(
            PlatformConnection.nonce == decoded_state.get("nonce"),
            PlatformConnection.platform == PlatformType.TELEGRAM,
            PlatformConnection.workspace_id == workspace_id,
            PlatformConnection.campaign_id == int(decoded_state.get("campaign_id")),
            PlatformConnection.id == int(decoded_state.get("connection_id"))
        ).first()

        if not platform_conn:

            logger.error(f"Connection not found for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state token"
            )

        bot = self.db.query(ManagedTelegramBot).filter(
            ManagedTelegramBot.id == decoded_state.get("bot_id")
        ).first()

        if not bot:
            logger.error(f"Bot not found for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bot id"
            )

        if campaign.status not in [CampaignStatus.PENDING, CampaignStatus.PAUSED]:
            logger.error(f"Cannot connect to campaign that is not pending or paused for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only connect to campaigns that are pending or paused"
            )

        if len(bot.connected_campaigns) >= bot.max_campaigns:
            logger.error(f"Bot is already connected to the maximum number of campaigns for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bot is already connected to the maximum number of campaigns"
            )

        if bot.is_exclusive:
            logger.error(f"Bot is exclusive for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bot is exclusive and cannot be connected to another campaign"
            )

        if campaign.id in [campaign.id for campaign in bot.connected_campaigns]:
            logger.error(f"Bot is already connected to this campaign for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bot is already connected to this campaign"
            )

        if not bot.is_active:
            logger.error(f"Bot is not active for state token {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bot is not active "
            )

        # Update bot details

        campaign.managed_telegram_bot_id = bot.id
        bot.last_assigned_at = get_now()

        # Update connection details
        platform_conn.is_connected = True
        platform_conn.connected_at = get_now()
        platform_conn.platform_user_id = str(bot.id)
        platform_conn.platform_username = bot.bot_username

        self.db.commit()
        self.db.refresh(platform_conn)
        self.db.refresh(bot)

        # delete other platform conn apart from this one
        self.db.query(PlatformConnection).filter(
            PlatformConnection.workspace_id == workspace_id,
            PlatformConnection.campaign_id == platform_conn.campaign_id,
            PlatformConnection.platform == PlatformType.TELEGRAM,
            PlatformConnection.id != platform_conn.id
        ).delete()

        self.db.commit()

        return platform_conn

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
