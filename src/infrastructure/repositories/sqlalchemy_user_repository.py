from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session

from src.domain.entities.user import User, UserRole
from src.domain.ports.user_repository import UserRepository
from src.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def save(self, user: User) -> User:
        model = UserModel(
            id=str(user.id),
            name=user.name,
            role_title=user.role_title,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        model = self._session.query(UserModel).filter(UserModel.id == str(user_id)).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[User]:
        model = self._session.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def find_all(self) -> list[User]:
        models = self._session.query(UserModel).order_by(UserModel.created_at.asc()).all()
        return [self._to_entity(m) for m in models]

    def update(self, user: User) -> User:
        model = self._session.query(UserModel).filter(UserModel.id == str(user.id)).first()
        if not model:
            raise ValueError("User not found")
        model.name = user.name
        model.role_title = user.role_title
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.role = user.role.value
        model.is_active = user.is_active
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, user_id: UUID) -> bool:
        model = self._session.query(UserModel).filter(UserModel.id == str(user_id)).first()
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def count_admins(self) -> int:
        return self._session.query(UserModel).filter(
            UserModel.role == "admin", UserModel.is_active == True
        ).count()

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=UUID(model.id),
            name=model.name,
            role_title=model.role_title,
            email=model.email,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
        )