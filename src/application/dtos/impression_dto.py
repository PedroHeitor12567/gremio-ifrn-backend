from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateImpressionDTO:
    person_name: str
    turma: str
    value: float
    registered_by_id: UUID
    registered_by_name: str

@dataclass
class ImpressionResponseDTO:
    id: UUID
    person_name: str
    turma: str
    value: float
    registered_by_id: UUID
    registered_by_name: str
    created_at: datetime

@dataclass
class DashboardSummaryDTO:
    total_impressions: int
    total_value: float
    average_value: float
    impressions_by_turma: dict[str, int]
    value_by_turma: dict[str, float]
    recent_impressions: list[ImpressionResponseDTO]

@dataclass
class ReportDTO:
    period_start: datetime
    period_end: datetime
    total_impressions: int
    total_value: float
    average_value: float
    impressions_by_turma: dict[str, int]
    value_by_turma: dict[str, float]
    impressions_by_day: dict[str, float]
    impressions: list[ImpressionResponseDTO]
