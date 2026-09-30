from __future__ import annotations

import logging
from uuid import UUID

from jwt import PyJWTError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    InternalServiceError,
    PermissionDeniedError,
    ServiceUnavailableError,
    UnauthenticatedError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.enums import Role
from app.models.users import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthTokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    async def register_user(payload: UserCreate, db: AsyncSession) -> AuthTokenResponse:
        existing_user = await UserRepository.get_by_email(payload.email, db)
        if existing_user:
            raise ConflictError(detail="Email already exists")

        try:
            user = await UserRepository.create_user(
                payload.name, payload.email, hash_password(payload.password), Role(payload.role), db
            )
        except IntegrityError:
            await db.rollback()
            if await UserRepository.get_by_email(payload.email, db):
                raise ConflictError(detail="Email already exists") from None
            raise

        return await AuthService._issue_tokens(user, db)

    @staticmethod
    async def login_user(payload: UserLogin, db: AsyncSession) -> AuthTokenResponse:
        user = await UserRepository.get_by_email(payload.email, db)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise UnauthenticatedError(
                detail="Invalid email or password",
            )
        if not user.is_active or user.deleted_at is not None:
            raise PermissionDeniedError(
                detail="User account is inactive",
            )
        return await AuthService._issue_tokens(user, db)

    @staticmethod
    async def refresh_tokens(payload: RefreshTokenRequest, db: AsyncSession) -> AuthTokenResponse:
        decoded = decode_token(payload.refresh_token, expected_type="refresh")
        if decoded is None:
            raise UnauthenticatedError(detail="Invalid or expired refresh token")

        try:
            user_id = UUID(decoded["sub"])
        except (ValueError, TypeError):
            raise UnauthenticatedError(detail="Invalid refresh token") from None
        user = await UserRepository.get_by_id(user_id, db)
        if user is None or not user.is_active or user.deleted_at is not None:
            raise UnauthenticatedError(detail="User account unavailable")

        token_hash = hash_token(payload.refresh_token)
        if not await RefreshTokenRepository.consume(token_hash, user.id, db):
            raise UnauthenticatedError(
                detail="Refresh token is invalid or revoked",
            )
        return await AuthService._issue_tokens(user, db)

    @staticmethod
    async def logout(refresh_token: str, db: AsyncSession) -> dict[str, str]:
        decoded = decode_token(refresh_token, expected_type="refresh")
        if decoded is None:
            raise UnauthenticatedError(detail="Invalid refresh token")

        try:
            user_id = UUID(decoded["sub"])
        except (ValueError, TypeError):
            raise UnauthenticatedError(detail="Invalid refresh token") from None
        token_hash = hash_token(refresh_token)
        if not await RefreshTokenRepository.consume(token_hash, user_id, db):
            raise UnauthenticatedError(detail="Refresh token is invalid or revoked")
        await db.commit()
        return {"message": "Logged out successfully"}

    @staticmethod
    async def _issue_tokens(user: User, db: AsyncSession) -> AuthTokenResponse:
        try:
            access_token = create_access_token(str(user.id))
            refresh_token = create_refresh_token(str(user.id))
        except PyJWTError:
            await db.rollback()
            logger.exception("Could not sign authentication tokens")
            raise InternalServiceError(detail="Could not issue tokens") from None

        try:
            await RefreshTokenRepository.create(user.id, refresh_token, db)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            logger.exception("Could not save authentication session")
            raise ServiceUnavailableError(detail="Could not start authentication session") from None

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
