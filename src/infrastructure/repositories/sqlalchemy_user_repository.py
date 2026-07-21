from uuid import UUID
from typing import Optional

from sqlalchemy import select, delete as sql_delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User, UserRole
from src.domain.ports.user_repository import UserRepository
from src.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> User:
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
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(user_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[User]:
        result = await self._session.execute(
            select(UserModel).order_by(UserModel.created_at.asc())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(user.id))
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError("User not found")
        model.name = user.name
        model.role_title = user.role_title
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.role = user.role.value
        model.is_active = user.is_active
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(user_id))
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.execute(
            sql_delete(UserModel).where(UserModel.id == str(user_id))
        )
        await self._session.commit()
        return True

    async def count_admins(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(UserModel).where(
                UserModel.role == "admin", UserModel.is_active == True
            )
        )
        return result.scalar_one()

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
