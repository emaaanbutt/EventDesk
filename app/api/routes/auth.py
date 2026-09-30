from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, DbSession, get_db
from app.schemas.auth import AuthTokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(get_db)])


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: DbSession) -> AuthTokenResponse:
    return await AuthService.register_user(payload, db)


@router.post("/login", response_model=AuthTokenResponse)
async def login_user(payload: UserLogin, db: DbSession) -> AuthTokenResponse:
    return await AuthService.login_user(payload, db)


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh_tokens(payload: RefreshTokenRequest, db: DbSession) -> AuthTokenResponse:
    return await AuthService.refresh_tokens(payload, db)


@router.post("/logout")
async def logout_user(payload: RefreshTokenRequest, db: DbSession) -> dict[str, str]:
    return await AuthService.logout(payload.refresh_token, db)


@router.get("/me")
async def get_me(current_user: CurrentUser) -> dict[str, str]:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role.value,
    }
