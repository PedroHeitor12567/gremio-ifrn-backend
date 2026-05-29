from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    impressions = relationship("ImpressionModel", back_populates="registered_by_user")


class ImpressionModel(Base):
    __tablename__ = "impressions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    person_name = Column(String, nullable=False)
    turma = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    registered_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    registered_by_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    registered_by_user = relationship("UserModel", back_populates="impressions")