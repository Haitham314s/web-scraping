import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

if os.getenv("CQLENG_ALLOW_SCHEMA_MANAGEMENT") is None:
    os.environ["CQLENG_ALLOW_SCHEMA_MANAGEMENT"] = "1"


class Settings(BaseSettings):
    name: str
    db_client_id: str
    db_client_secret: str
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
