from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import EmailStr, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(gt=0)
    EMAIL_BACKEND: Literal["brevo", "disabled"]
    BREVO_API_KEY: str | None = None
    BREVO_SENDER_EMAIL: EmailStr | None = None
    BREVO_SENDER_NAME: str | None = None
    REMINDER_HOURS_BEFORE: int = Field(gt=0)
    REMINDER_TIMEZONE: str

    @model_validator(mode="after")
    def validate_email_backend(self) -> "Settings":
        if self.EMAIL_BACKEND == "brevo" and not all(
            (self.BREVO_API_KEY, self.BREVO_SENDER_EMAIL, self.BREVO_SENDER_NAME)
        ):
            raise ValueError("Brevo credentials are required when EMAIL_BACKEND=brevo")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
