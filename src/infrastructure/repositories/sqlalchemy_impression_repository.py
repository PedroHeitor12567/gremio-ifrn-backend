from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.entities.impression import Impression
from src.domain.ports.impression_repository import ImpressionRepository
from src.infrastructure.database.models import ImpressionModel


class SQLAlchemyImpressionRepository(ImpressionRepository):
    def __init__(self, session: Session):
        self._session = session

    def save(self, impression: Impression) -> Impression:
        model = ImpressionModel(
            id=str(impression.id),
            person_name=impression.person_name,
            turma=impression.turma,
            value=impression.value,
            created_at=impression.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, impression_id: UUID) -> Impression | None:
        model = self._session.query(ImpressionModel).filter(
            ImpressionModel.id == str(impression_id)
        ).first()
        return self._to_entity(model) if model else None

    def find_all(self) -> list[Impression]:
        models = self._session.query(ImpressionModel).order_by(
            ImpressionModel.created_at.desc()
        ).all()
        return [self._to_entity(m) for m in models]

    def find_by_period(self, start: datetime, end: datetime) -> list[Impression]:
        models = self._session.query(ImpressionModel).filter(
            ImpressionModel.created_at >= start,
            ImpressionModel.created_at <= end,
        ).order_by(ImpressionModel.created_at.asc()).all()
        return [self._to_entity(m) for m in models]

    def delete(self, impression_id: UUID) -> bool:
        model = self._session.query(ImpressionModel).filter(
            ImpressionModel.id == str(impression_id)
        ).first()
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def _to_entity(self, model: ImpressionModel) -> Impression:
        return Impression(
            id=UUID(model.id),
            person_name=model.person_name,
            turma=model.turma,
            value=model.value,
            created_at=model.created_at,
        )