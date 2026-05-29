from datetime import timedelta, datetime
from uuid import UUID

from src.application.dtos.impression_dto import CreateImpressionDTO, ImpressionResponseDTO, DashboardSummaryDTO, ReportDTO
from src.domain.entities.impression import Impression
from src.domain.ports.impression_repository import ImpressionRepository


def _to_response(impression: Impression) -> ImpressionResponseDTO:
    return ImpressionResponseDTO(
        id=impression.id,
        person_name=impression.person_name,
        turma=impression.turma,
        value=impression.value,
        registered_by_id=impression.registered_by_id,
        registered_by_name=impression.registered_by_name,
        created_at=impression.created_at,
    )

class CreateImpressionUseCase:
    def __init__(self, repository: ImpressionRepository):
        self.repository = repository

    def execute(self, dto:CreateImpressionDTO) -> ImpressionResponseDTO:
        impression = Impression(
            person_name=dto.person_name,
            turma=dto.turma.strip().upper(),
            value=dto.value,
            registered_by_id=dto.registered_by_id,
            registered_by_name=dto.registered_by_name,
        )

        saved = self.repository.save(impression)
        return _to_response(saved)

class ListImpressionsUseCase:
    def __init__(self, repository: ImpressionRepository):
        self._repository = repository

    def execute(self) -> list[ImpressionResponseDTO]:
        impressions = self._repository.find_all()
        return [_to_response(i) for i in impressions]


class DeleteImpressionUseCase:
    def __init__(self, repository: ImpressionRepository):
        self._repository = repository

    def execute(self, impression_id: UUID) -> bool:
        return self._repository.delete(impression_id)


class GetDashboardUseCase:
    def __init__(self, repository: ImpressionRepository):
        self._repository = repository

    def execute(self) -> DashboardSummaryDTO:
        impressions = self._repository.find_all()

        total_impressions = len(impressions)
        total_value = sum(i.value for i in impressions)
        average_value = total_value / total_impressions if total_impressions > 0 else 0.0

        impressions_by_turma: dict[str, int] = {}
        value_by_turma: dict[str, float] = {}

        for imp in impressions:
            impressions_by_turma[imp.turma] = impressions_by_turma.get(imp.turma, 0) + 1
            value_by_turma[imp.turma] = value_by_turma.get(imp.turma, 0.0) + imp.value

        recent = sorted(impressions, key=lambda i: i.created_at, reverse=True)[:10]

        return DashboardSummaryDTO(
            total_impressions=total_impressions,
            total_value=total_value,
            average_value=average_value,
            impressions_by_turma=impressions_by_turma,
            value_by_turma=value_by_turma,
            recent_impressions=[_to_response(i) for i in recent],
        )

class GetWeeklyReportUseCase:
    def __init__(self, repository: ImpressionRepository):
        self._repository = repository

    def execute(self) -> ReportDTO:
        end = datetime.now()
        start = end - timedelta(days=7)
        return _build_report(self._repository, start, end)


class GetMonthlyReportUseCase:
    def __init__(self, repository: ImpressionRepository):
        self._repository = repository

    def execute(self) -> ReportDTO:
        today = datetime.now()
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Último dia do mês
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(seconds=1)
        return _build_report(self._repository, start, end)


def _build_report(repository: ImpressionRepository, start: datetime, end: datetime) -> ReportDTO:
    impressions = repository.find_by_period(start, end)
    total_impressions = len(impressions)
    total_value = sum(i.value for i in impressions)
    average_value = total_value / total_impressions if total_impressions > 0 else 0.0

    impressions_by_turma: dict[str, int] = {}
    value_by_turma: dict[str, float] = {}
    impressions_by_day: dict[str, float] = {}

    for imp in impressions:
        impressions_by_turma[imp.turma] = impressions_by_turma.get(imp.turma, 0) + 1
        value_by_turma[imp.turma] = value_by_turma.get(imp.turma, 0.0) + imp.value
        day_key = imp.created_at.strftime("%Y-%m-%d")
        impressions_by_day[day_key] = impressions_by_day.get(day_key, 0.0) + imp.value

    return ReportDTO(
        period_start=start,
        period_end=end,
        total_impressions=total_impressions,
        total_value=total_value,
        average_value=average_value,
        impressions_by_turma=impressions_by_turma,
        value_by_turma=value_by_turma,
        impressions_by_day=impressions_by_day,
        impressions=[_to_response(i) for i in impressions],
    )