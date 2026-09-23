from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: Literal["HS256"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(gt=0)

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL


settings = Settings()
