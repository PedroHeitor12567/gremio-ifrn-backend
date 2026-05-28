from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.adapters.schemas.impression_schema import (
    CreateImpressionSchema,
    ImpressionResponse,
    DashboardResponse,
    ReportResponse,
)
from src.application.dtos.impression_dto import CreateImpressionDTO
from src.application.use_cases.impression_use_cases import (
    CreateImpressionUseCase,
    ListImpressionsUseCase,
    DeleteImpressionUseCase,
    GetDashboardUseCase,
    GetWeeklyReportUseCase,
    GetMonthlyReportUseCase,
)
from src.infrastructure.database.connection import get_session
from src.infrastructure.repositories.sqlalchemy_impression_repository import (
    SQLAlchemyImpressionRepository,
)

router = APIRouter(prefix="/impressions", tags=["impressions"])


def get_repository(session: Session = Depends(get_session)):
    return SQLAlchemyImpressionRepository(session)


@router.post("/", response_model=ImpressionResponse, status_code=201)
def create_impression(
    body: CreateImpressionSchema,
    repository=Depends(get_repository),
):
    dto = CreateImpressionDTO(
        person_name=body.person_name,
        turma=body.turma,
        value=body.value,
    )
    result = CreateImpressionUseCase(repository).execute(dto)
    return ImpressionResponse(
        id=result.id,
        person_name=result.person_name,
        turma=result.turma,
        value=result.value,
        created_at=result.created_at,
    )


@router.get("/", response_model=list[ImpressionResponse])
def list_impressions(repository=Depends(get_repository)):
    results = ListImpressionsUseCase(repository).execute()
    return [
        ImpressionResponse(
            id=r.id,
            person_name=r.person_name,
            turma=r.turma,
            value=r.value,
            created_at=r.created_at,
        )
        for r in results
    ]


@router.delete("/{impression_id}", status_code=204)
def delete_impression(impression_id: UUID, repository=Depends(get_repository)):
    deleted = DeleteImpressionUseCase(repository).execute(impression_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Impression not found")


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(repository=Depends(get_repository)):
    result = GetDashboardUseCase(repository).execute()
    return DashboardResponse(
        total_impressions=result.total_impressions,
        total_value=result.total_value,
        average_value=result.average_value,
        impressions_by_turma=result.impressions_by_turma,
        value_by_turma=result.value_by_turma,
        recent_impressions=[
            ImpressionResponse(
                id=r.id,
                person_name=r.person_name,
                turma=r.turma,
                value=r.value,
                created_at=r.created_at,
            )
            for r in result.recent_impressions
        ],
    )


@router.get("/reports/weekly", response_model=ReportResponse)
def get_weekly_report(repository=Depends(get_repository)):
    result = GetWeeklyReportUseCase(repository).execute()
    return _build_report_response(result)


@router.get("/reports/monthly", response_model=ReportResponse)
def get_monthly_report(repository=Depends(get_repository)):
    result = GetMonthlyReportUseCase(repository).execute()
    return _build_report_response(result)


def _build_report_response(result) -> ReportResponse:
    return ReportResponse(
        period_start=result.period_start,
        period_end=result.period_end,
        total_impressions=result.total_impressions,
        total_value=result.total_value,
        average_value=result.average_value,
        impressions_by_turma=result.impressions_by_turma,
        value_by_turma=result.value_by_turma,
        impressions_by_day=result.impressions_by_day,
        impressions=[
            ImpressionResponse(
                id=r.id,
                person_name=r.person_name,
                turma=r.turma,
                value=r.value,
                created_at=r.created_at,
            )
            for r in result.impressions
        ],
    )