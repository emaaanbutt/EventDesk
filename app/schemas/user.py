from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re

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

    role: str = Field(
        ...,
        description="Role of the user. Can be 'admin', 'organizer', or 'attendee'."
    )

    is_active: bool = Field(
        default=True,
        description="Indicates whether the user account is active."
    )  

    @field_validator("role")
    def validate_role(cls, value: str) -> str:
        valid_roles = {"admin", "organizer", "attendee"}
        if value not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}.")
        return value 

    @field_validator("email")
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise ValueError("Email cannot be empty.")

        return value

    def model_config(cls) -> ConfigDict:
            return ConfigDict(
                from_attributes=True,
                populate_by_name=True,
                extra="forbid",
            )


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_lenght=8,
        max_length=128,
        description="Password for the user account."
    )

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

    def model_config(cls) -> ConfigDict:
        return ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            extra="forbid",
        )


     