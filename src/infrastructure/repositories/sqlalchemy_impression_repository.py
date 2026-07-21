from datetime import datetime
from uuid import UUID
from typing import Optional

from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.impression import Impression
from src.domain.ports.impression_repository import ImpressionRepository
from src.infrastructure.database.models import ImpressionModel


class SQLAlchemyImpressionRepository(ImpressionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, impression: Impression) -> Impression:
        model = ImpressionModel(
            id=str(impression.id),
            person_name=impression.person_name,
            turma=impression.turma,
            value=impression.value,
            registered_by_id=str(impression.registered_by_id),
            registered_by_name=impression.registered_by_name,
            created_at=impression.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, impression_id: UUID) -> Optional[Impression]:
        result = await self._session.execute(
            select(ImpressionModel).where(ImpressionModel.id == str(impression_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[Impression]:
        result = await self._session.execute(
            select(ImpressionModel).order_by(ImpressionModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_by_period(self, start: datetime, end: datetime) -> list[Impression]:
        result = await self._session.execute(
            select(ImpressionModel)
            .where(ImpressionModel.created_at >= start, ImpressionModel.created_at <= end)
            .order_by(ImpressionModel.created_at.asc())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, impression_id: UUID) -> bool:
        result = await self._session.execute(
            select(ImpressionModel).where(ImpressionModel.id == str(impression_id))
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.execute(
            sql_delete(ImpressionModel).where(ImpressionModel.id == str(impression_id))
        )
        await self._session.commit()
        return True

    def _to_entity(self, model: ImpressionModel) -> Impression:
        return Impression(
            id=UUID(model.id),
            person_name=model.person_name,
            turma=model.turma,
            value=model.value,
            registered_by_id=UUID(model.registered_by_id),
            registered_by_name=model.registered_by_name,
            created_at=model.created_at,
        )
