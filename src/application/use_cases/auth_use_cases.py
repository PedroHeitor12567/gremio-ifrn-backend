from datetime import datetime, timedelta
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext

from src.application.dtos.user_dto import (
    CreateUserDTO, UpdateUserDTO, UserResponseDTO, LoginDTO, TokenDTO
)
from src.domain.entities.user import User, UserRole
from src.domain.ports.user_repository import UserRepository

SECRET_KEY = "gremio-ifrn-secret-key-2024-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _to_response(user: User) -> UserResponseDTO:
    return UserResponseDTO(
        id=user.id,
        name=user.name,
        role_title=user.role_title,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _create_token(user_id: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


class LoginUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def execute(self, dto: LoginDTO) -> TokenDTO:
        user = self._repository.find_by_email(dto.email.lower().strip())
        if not user:
            raise ValueError("Credenciais inválidas")
        if not user.is_active:
            raise ValueError("Usuário inativo")
        if not _verify_password(dto.password, user.hashed_password):
            raise ValueError("Credenciais inválidas")
        token = _create_token(str(user.id), user.role.value)
        return TokenDTO(
            access_token=token,
            token_type="bearer",
            user=_to_response(user),
        )


class CreateUserUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def execute(self, dto: CreateUserDTO) -> UserResponseDTO:
        existing = self._repository.find_by_email(dto.email.lower().strip())
        if existing:
            raise ValueError("Email já cadastrado")
        user = User(
            name=dto.name.strip(),
            role_title=dto.role_title.strip(),
            email=dto.email.lower().strip(),
            hashed_password=_hash_password(dto.password),
            role=dto.role,
        )
        saved = self._repository.save(user)
        return _to_response(saved)


class ListUsersUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def execute(self) -> list[UserResponseDTO]:
        return [_to_response(u) for u in self._repository.find_all()]


class UpdateUserUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def execute(self, dto: UpdateUserDTO) -> UserResponseDTO:
        user = self._repository.find_by_id(dto.user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        existing = self._repository.find_by_email(dto.email.lower().strip())
        if existing and existing.id != dto.user_id:
            raise ValueError("Email já cadastrado")
        user.name = dto.name.strip()
        user.role_title = dto.role_title.strip()
        user.email = dto.email.lower().strip()
        user.role = dto.role
        user.is_active = dto.is_active
        if dto.password:
            user.hashed_password = _hash_password(dto.password)
        updated = self._repository.update(user)
        return _to_response(updated)


class DeleteUserUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def execute(self, user_id: UUID) -> bool:
        user = self._repository.find_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        if user.role == UserRole.ADMIN:
            count = self._repository.count_admins()
            if count <= 1:
                raise ValueError("Não é possível remover o único administrador")
        return self._repository.delete(user_id)


class SeedAdminUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def execute(self):
        existing = self._repository.find_by_email("admin@gremio.ifrn")
        if existing:
            return
        user = User(
            name="Administrador",
            role_title="Administrador do Sistema",
            email="admin@gremio.ifrn",
            hashed_password=_hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        self._repository.save(user)