from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.auth import AuthTokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> AuthTokenResponse:
    return await AuthService.register_user(payload, db)


@router.post("/login", response_model=AuthTokenResponse)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> AuthTokenResponse:
    return await AuthService.login_user(payload, db)


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh_tokens(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> AuthTokenResponse:
    return await AuthService.refresh_tokens(payload, db)


@router.post("/logout")
async def logout_user(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    return await AuthService.logout(payload.refresh_token, db)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role.value,
    }
