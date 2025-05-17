from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from functools import lru_cache
from pydantic import HttpUrl


class Settings(BaseSettings):

    """ Application Settings """

    display_name: str = "MoonShill"
    app_name:  str = "MoonShill"
    debug:  bool = True

    # logging config
    log_file_path: str = "app.log"

    # browser config
    cors_allow_origins: list[str] = ["http://localhost:5173", "https://moonshill.pages.dev"]
    frontend_url: str = "http://localhost:5173"

    # database config
    db_url: str = "postgresql://u0:password@localhost:5432/db10"
    redis_url: str = "redis://redis:6379"
    use_mock_db: bool = False

    # security
    jwt_secret: str = "yudwwddW"
    jwt_expiry: int = 48
    password_salt: str = "salty"

    # Base settings
    project_name: str = "MoonsHill"
    api_v1_str: str = "/api/v1"

    # JWT settings
    secret_key: str = "SECRET_KEY"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Twitter API settings
    twitter_client_id: str = "TWITTER_CLIENT_ID"
    twitter_client_secret: str = "TWITTER_CLIENT_SECRET"

    # Discord settings
    discord_client_id: str = "DISCORD_CLIENT_ID"
    discord_client_secret: str = "DISCORD_CLIENT_SECRET"

    # Telegram settings
    telegram_bot_token: str = "TELEGRAM_BOT_TOKEN"
    telegram_bot_username: str = "TELEGRAM_BOT_USERNAME"

    # CORS settings
    backend_cors_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
