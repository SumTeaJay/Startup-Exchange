from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./startup_exchange.db"
    jwt_secret: str = "development-secret-change-me"
    jwt_expire_minutes: int = 60
    telegram_bot_token: str = ""
    telegram_init_data_max_age_seconds: int = 86400

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
