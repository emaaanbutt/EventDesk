from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, Optional
import re
from enum import Enum
from typing import Literal

class UserRole(str, Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"

class UserBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Full name of the user"
    )

    email: EmailStr =  Field(
        ...,
        description="User email address."
    )


    @field_validator("email")
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise ValueError("Email cannot be empty.")

        return value

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password for the user account."
    )

    role: Literal['organizer', 'attendee'] = Field(default='attendee')

    @field_validator("password")
    def validate_password(cls, value:str) -> str:
        if len(value)<8 or len(value)>128:
            raise ValueError("Passowrd must be in the range of 8 to 128 characters.")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")

        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_+-]", value):
            raise ValueError("Password must contain at least one special character.")

        return value

    model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            extra="forbid",
        )


class UserResponse(UserBase):
    id:int
    role:UserRole
    is_active:bool

    model_config = ConfigDict(
                from_attributes=True)



model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            extra="forbid",
        )


class UserLogin(BaseModel):
    email: EmailStr 
    password: str
    @field_validator("email")
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise ValueError("Email cannot be empty.")

        return value

    model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            extra="forbid",
        )