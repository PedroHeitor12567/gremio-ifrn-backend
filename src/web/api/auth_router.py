from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.web.schemas.user_schema import LoginSchema, TokenResponse, UserResponse, CreateUserSchema, UpdateUserSchema
from src.application.dtos.user_dto import LoginDTO, CreateUserDTO, UpdateUserDTO
from src.application.use_cases.auth_use_cases import (
    LoginUseCase, CreateUserUseCase, ListUsersUseCase, UpdateUserUseCase, DeleteUserUseCase
)
from src.web.api.auth_middleware import get_current_user, require_admin
from src.infrastructure.database.connection import get_session
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.domain.entities.user import User
from uuid import UUID

router = APIRouter(tags=["auth"])


def get_user_repo(session: Session = Depends(get_session)):
    return SQLAlchemyUserRepository(session)


@router.post("/auth/login", response_model=TokenResponse)
def login(body: LoginSchema, repo=Depends(get_user_repo)):
    try:
        result = LoginUseCase(repo).execute(LoginDTO(email=body.email, password=body.password))
        return TokenResponse(
            access_token=result.access_token,
            token_type=result.token_type,
            user=UserResponse(
                id=result.user.id,
                name=result.user.name,
                role_title=result.user.role_title,
                email=result.user.email,
                role=result.user.role,
                is_active=result.user.is_active,
                created_at=result.user.created_at,
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        role_title=current_user.role_title,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.get("/admin/users", response_model=list[UserResponse])
def list_users(admin=Depends(require_admin), repo=Depends(get_user_repo)):
    results = ListUsersUseCase(repo).execute()
    return [UserResponse(
        id=r.id, name=r.name, role_title=r.role_title,
        email=r.email, role=r.role, is_active=r.is_active, created_at=r.created_at
    ) for r in results]


@router.post("/admin/users", response_model=UserResponse, status_code=201)
def create_user(body: CreateUserSchema, admin=Depends(require_admin), repo=Depends(get_user_repo)):
    try:
        dto = CreateUserDTO(
            name=body.name, role_title=body.role_title,
            email=body.email, password=body.password, role=body.role
        )
        result = CreateUserUseCase(repo).execute(dto)
        return UserResponse(
            id=result.id, name=result.name, role_title=result.role_title,
            email=result.email, role=result.role, is_active=result.is_active, created_at=result.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/admin/users/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, body: UpdateUserSchema, admin=Depends(require_admin), repo=Depends(get_user_repo)):
    try:
        dto = UpdateUserDTO(
            user_id=user_id, name=body.name, role_title=body.role_title,
            email=body.email, role=body.role, is_active=body.is_active, password=body.password
        )
        result = UpdateUserUseCase(repo).execute(dto)
        return UserResponse(
            id=result.id, name=result.name, role_title=result.role_title,
            email=result.email, role=result.role, is_active=result.is_active, created_at=result.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/admin/users/{user_id}", status_code=204)
def delete_user(user_id: UUID, admin=Depends(require_admin), repo=Depends(get_user_repo)):
    try:
        DeleteUserUseCase(repo).execute(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))