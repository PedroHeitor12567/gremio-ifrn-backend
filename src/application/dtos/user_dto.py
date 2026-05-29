from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.user import UserRole


@dataclass
class CreateUserDTO:
    name: str
    role_title: str
    email: str
    password: str
    role: UserRole = UserRole.USER

@dataclass
class UpdateUserDTO:
    user_id: UUID
    name: str
    role_title: str
    email: str
    role: UserRole
    is_active: bool
    password: str | None = None

@dataclass
class UserResponseDTO:
    id: UUID
    name: str
    role_title: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

@dataclass
class LoginDTO:
    email: str
    password: str

@dataclass
class TokenDTO:
    access_token: str
    token_type: str
    user: UserResponseDTO