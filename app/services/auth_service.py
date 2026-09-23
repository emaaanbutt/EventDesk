from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, decode_token, hash_token, verify_password
from app.models.users import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthTokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    @staticmethod
    async def register_user(payload: UserCreate, db: AsyncSession) -> AuthTokenResponse:
        existing_user = await UserRepository.get_by_email(payload.email, db)
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already exists")

        user = await UserRepository.create_user(payload, db)
        return await AuthService._issue_tokens(user, db)

    @staticmethod
    async def login_user(payload: UserLogin, db: AsyncSession) -> AuthTokenResponse:
        user = await UserRepository.get_by_email(payload.email, db)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active or user.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        return await AuthService._issue_tokens(user, db)

    @staticmethod
    async def refresh_tokens(payload: RefreshTokenRequest, db: AsyncSession) -> AuthTokenResponse:
        decoded = decode_token(payload.refresh_token, expected_type="refresh")
        if decoded is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        try:
            user_id = UUID(decoded["sub"])
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Invalid refresh token") from None
        user = await UserRepository.get_by_id(user_id, db)
        if user is None or not user.is_active or user.deleted_at is not None:
            raise HTTPException(status_code=401, detail="User account unavailable")

        token_hash = hash_token(payload.refresh_token)
        if not await RefreshTokenRepository.consume(token_hash, user.id, db):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or revoked")
        return await AuthService._issue_tokens(user, db)

    @staticmethod
    async def logout(refresh_token: str, db: AsyncSession) -> dict[str, str]:
        decoded = decode_token(refresh_token, expected_type="refresh")
        if decoded is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        try:
            user_id = UUID(decoded["sub"])
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Invalid refresh token") from None
        token_hash = hash_token(refresh_token)
        if not await RefreshTokenRepository.consume(token_hash, user_id, db):
            raise HTTPException(status_code=401, detail="Refresh token is invalid or revoked")
        return {"message": "Logged out successfully"}

    @staticmethod
    async def _issue_tokens(user: User, db: AsyncSession) -> AuthTokenResponse:
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        await RefreshTokenRepository.create(user.id, refresh_token, db)

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
