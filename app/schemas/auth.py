from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class TokenPayload(BaseModel):
    sub: str
    type: str
    exp: int

    model_config = ConfigDict(from_attributes=True)
