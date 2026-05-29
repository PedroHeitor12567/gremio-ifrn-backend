from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

@dataclass
class User:
    name: str
    role_title: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.email or not self.email.strip():
            raise ValueError("email cannot be empty")
        if not self.role_title or not self.role_title.strip():
            raise ValueError("role_title cannot be empty")
