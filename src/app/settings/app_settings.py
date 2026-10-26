from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseSettings):
    aws_region: str
    sqs_endpoint_url: str | None = None
    sqs_queue_url: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_app_settings() -> _AppSettings:
    return _AppSettings()
