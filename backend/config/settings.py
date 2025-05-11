from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    """ Application Settings """

    display_name: str = "MoonShill"
    app_name:  str = "MoonShill"
    debug:  bool = True

    # logging config
    log_file_path: str = "app.log"

    # browser config
    cors_allow_origins: list[str] = ["http://localhost:5173"]
    frontend_url: str = "http://localhost:5173"

    # database config
    db_url: str = "postgresql://u0:password@localhost:5432/db10"
    redis_url: str = "redis://redis:6379"
    use_mock_db: bool = False

    # security
    jwt_secret: str = "yudwwddW"
    jwt_expiry: int = 48
    password_salt: str = "salty"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache()
def get_settings():
    return Settings()
