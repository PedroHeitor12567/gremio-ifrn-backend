from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator


class CreateImpressionSchema(BaseModel):
    person_name: str
    turma: str
    value: float

    @field_validator("person_name", "turma")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("value")
    @classmethod
    def positive_value(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Value must be greater than zero")
        return v


class ImpressionResponse(BaseModel):
    id: UUID
    person_name: str
    turma: str
    value: float
    registered_by_id: UUID
    registered_by_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    total_impressions: int
    total_value: float
    average_value: float
    impressions_by_turma: dict[str, int]
    value_by_turma: dict[str, float]
    recent_impressions: list[ImpressionResponse]


class ReportResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_impressions: int
    total_value: float
    average_value: float
    impressions_by_turma: dict[str, int]
    value_by_turma: dict[str, float]
    impressions_by_day: dict[str, float]
    impressions: list[ImpressionResponse]