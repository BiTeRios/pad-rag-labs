from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel

from auth_service.schemas import Credentials, RoleUpdate, TokenResponse, UserOut
from auth_service.service import UserService
from rag_common.auth import Identity, create_token, current_identity, require_role
from rag_common.errors import error_docs
from rag_common.events import publish_safely

router = APIRouter(prefix="/api/auth", tags=["auth"])


class UserPage(BaseModel):
    items: list[UserOut]
    total: int


async def user_service(request: Request) -> AsyncIterator[UserService]:
    async with request.app.state.sessions() as session:
        yield UserService(session, request.app.state.settings.password_min_length)


@router.post("/register", status_code=201, response_model=UserOut, summary="Регистрация (роль user)",
             responses=error_docs(400, 409, 422))
async def register(body: Credentials, request: Request, users: UserService = Depends(user_service)):
    user = await users.register(body.email, body.password)
    # email в событие не кладём: аналитике он не нужен
    await publish_safely(request.app.state.event_bus, "user.registered", {"user_id": user.id, "role": user.role})
    return user


@router.post("/login", response_model=TokenResponse, summary="Вход: выдаёт JWT", responses=error_docs(401, 422))
async def login(body: Credentials, request: Request, users: UserService = Depends(user_service)):
    user = await users.authenticate(body.email, body.password)
    settings = request.app.state.settings
    token = create_token(
        user.id, user.role, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
        ttl_minutes=settings.token_ttl_minutes, issuer=settings.jwt_issuer,
    )
    return TokenResponse(access_token=token, expires_in=settings.token_ttl_minutes * 60)


@router.get("/me", response_model=UserOut, summary="Текущий пользователь", responses=error_docs(401, 404))
async def me(identity: Identity = Depends(current_identity), users: UserService = Depends(user_service)):
    return await users.get(identity.user_id)


@router.get("/users", response_model=UserPage, summary="Список пользователей (admin)", responses=error_docs(401, 403))
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: Identity = Depends(require_role("admin")),
    users: UserService = Depends(user_service),
):
    items, total = await users.list(limit, offset)
    return UserPage(items=items, total=total)


@router.patch("/users/{user_id}/role", response_model=UserOut, summary="Сменить роль (admin)",
              description="Новая роль действует со следующего входа: в выданном токене роль прежняя.",
              responses=error_docs(401, 403, 404, 409, 422))
async def set_role(
    user_id: str, body: RoleUpdate,
    _: Identity = Depends(require_role("admin")),
    users: UserService = Depends(user_service),
):
    return await users.set_role(user_id, body.role)
