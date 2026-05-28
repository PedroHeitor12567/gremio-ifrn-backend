from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ImpressionModel(Base):
    __tablename__ = "impressions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    person_name = Column(String, nullable=False)
    turma = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)