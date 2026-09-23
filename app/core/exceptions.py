from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class AppError(Exception):
    """Base class for all application errors."""

    code: str = "APP_ERROR"
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None) -> None:
        self.message = message
        self.details = details or []
        super().__init__(message)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class ValidationAppError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 422


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = status.HTTP_409_CONFLICT


class EmailAlreadyExistsError(ConflictError):
    """Raised when a user attempts to create an account with an existing email."""

    def __init__(self) -> None:
        super().__init__(
            "Email already exists",
            details=[{"field": "email", "message": "Email already exists"}],
        )


class UserNotFoundError(NotFoundError):
    """Raised when a requested user cannot be found."""

    def __init__(self) -> None:
        super().__init__(
            "User not found",
            details=[{"field": "user_id", "message": "User does not exist"}],
        )
