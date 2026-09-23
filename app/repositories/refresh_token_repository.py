from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_token
from app.models.refresh_tokens import RefreshToken


class RefreshTokenRepository:
    @staticmethod
    async def create(user_id: uuid.UUID | str, raw_token: str, db: AsyncSession) -> RefreshToken:
        token_hash = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
            revoked_at=None,
        )
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return refresh_token

    @staticmethod
    async def get_by_hash(token_hash: str, db: AsyncSession) -> RefreshToken | None:
        result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        return result.scalar_one_or_none()

    @staticmethod
    async def revoke_by_hash(token_hash: str, db: AsyncSession) -> None:
        refresh_token = await RefreshTokenRepository.get_by_hash(token_hash, db)
        if refresh_token is None:
            return
        refresh_token.revoked_at = datetime.now(timezone.utc)
        await db.commit()

    @staticmethod
    async def consume(token_hash: str, user_id: uuid.UUID, db: AsyncSession) -> bool:
        result = await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.commit()
        return result.rowcount == 1

    @staticmethod
    async def revoke_all_for_user(user_id: uuid.UUID | str, db: AsyncSession) -> None:
        result = await db.execute(select(RefreshToken).where(RefreshToken.user_id == user_id))
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked_at = datetime.now(timezone.utc)
        await db.commit()
