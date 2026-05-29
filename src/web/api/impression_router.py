from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.web.schemas.impression_schema import (
    CreateImpressionSchema, ImpressionResponse, DashboardResponse, ReportResponse,
)
from src.application.dtos.impression_dto import CreateImpressionDTO
from src.application.use_cases.impression_use_cases import (
    CreateImpressionUseCase, ListImpressionsUseCase, DeleteImpressionUseCase,
    GetDashboardUseCase, GetWeeklyReportUseCase, GetMonthlyReportUseCase,
)
from src.web.api.auth_middleware import get_current_user, require_admin
from src.infrastructure.database.connection import get_session
from src.infrastructure.repositories.sqlalchemy_impression_repository import SQLAlchemyImpressionRepository
from src.domain.entities.user import User

router = APIRouter(prefix="/impressions", tags=["impressions"])


def get_repo(session: Session = Depends(get_session)):
    return SQLAlchemyImpressionRepository(session)


def _map(r) -> ImpressionResponse:
    return ImpressionResponse(
        id=r.id, person_name=r.person_name, turma=r.turma,
        value=r.value, registered_by_id=r.registered_by_id,
        registered_by_name=r.registered_by_name, created_at=r.created_at,
    )


@router.post("/", response_model=ImpressionResponse, status_code=201)
def create_impression(
    body: CreateImpressionSchema,
    current_user: User = Depends(get_current_user),
    repo=Depends(get_repo),
):
    dto = CreateImpressionDTO(
        person_name=body.person_name,
        turma=body.turma,
        value=body.value,
        registered_by_id=current_user.id,
        registered_by_name=current_user.name,
    )
    return _map(CreateImpressionUseCase(repo).execute(dto))


@router.get("/", response_model=list[ImpressionResponse])
def list_impressions(current_user: User = Depends(get_current_user), repo=Depends(get_repo)):
    return [_map(r) for r in ListImpressionsUseCase(repo).execute()]


@router.delete("/{impression_id}", status_code=204)
def delete_impression(
    impression_id: UUID,
    current_user: User = Depends(require_admin),
    repo=Depends(get_repo),
):
    if not DeleteImpressionUseCase(repo).execute(impression_id):
        raise HTTPException(status_code=404, detail="Impression not found")


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(current_user: User = Depends(get_current_user), repo=Depends(get_repo)):
    result = GetDashboardUseCase(repo).execute()
    return DashboardResponse(
        total_impressions=result.total_impressions,
        total_value=result.total_value,
        average_value=result.average_value,
        impressions_by_turma=result.impressions_by_turma,
        value_by_turma=result.value_by_turma,
        recent_impressions=[_map(r) for r in result.recent_impressions],
    )


@router.get("/reports/weekly", response_model=ReportResponse)
def weekly_report(current_user: User = Depends(get_current_user), repo=Depends(get_repo)):
    return _build_report_response(GetWeeklyReportUseCase(repo).execute())


@router.get("/reports/monthly", response_model=ReportResponse)
def monthly_report(current_user: User = Depends(get_current_user), repo=Depends(get_repo)):
    return _build_report_response(GetMonthlyReportUseCase(repo).execute())


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
        impressions=[_map(r) for r in result.impressions],
    )