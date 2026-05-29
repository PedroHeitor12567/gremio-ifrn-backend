from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator
from src.domain.entities.user import UserRole


class CreateUserSchema(BaseModel):
    name: str
    role_title: str
    email: str
    password: str
    role: UserRole = UserRole.USER

    @field_validator("name", "role_title", "email", "password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def min_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must have at least 6 characters")
        return v


class UpdateUserSchema(BaseModel):
    name: str
    role_title: str
    email: str
    role: UserRole
    is_active: bool
    password: str | None = None

    @field_validator("name", "role_title", "email")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class LoginSchema(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    role_title: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse