from typing import Literal

from pydantic import Field, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: Literal["HS256"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(gt=0)
    BREVO_API_KEY: str = Field(min_length=1)
    BREVO_SENDER_EMAIL: EmailStr
    BREVO_SENDER_NAME: str = Field(min_length=1)
    REMINDER_HOURS_BEFORE: int = Field(gt=0)
    REMINDER_TIMEZONE: str

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL


settings = Settings()
