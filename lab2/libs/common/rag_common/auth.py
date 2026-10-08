"""Аутентификация и авторизация.

- auth-service выпускает JWT (create_token), gateway проверяет подпись (decode_token).
- Gateway передаёт сервисам личность пользователя заголовками X-User-Id / X-User-Role и удаляет
  такие заголовки из запросов клиента, поэтому подделать их снаружи нельзя: наружу открыт только gateway.
- Сервисы проверяют права сами (require_role): защита не держится на одном gateway.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, Header

from rag_common.errors import Forbidden, Unauthorized

USER_ID_HEADER = "X-User-Id"
USER_ROLE_HEADER = "X-User-Role"
ROLES = ("user", "admin")


@dataclass(frozen=True)
class Identity:
    user_id: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def headers(self) -> dict[str, str]:
        """Заголовки для вызова соседнего сервиса от имени пользователя."""
        return {USER_ID_HEADER: self.user_id, USER_ROLE_HEADER: self.role}


def current_identity(
    # имена с префиксом x_: не должны совпадать с path-параметрами эндпоинтов (например, /users/{user_id})
    x_user_id: str | None = Header(None, alias=USER_ID_HEADER, description="Ставит gateway по JWT; от клиента удаляется"),
    x_user_role: str | None = Header(None, alias=USER_ROLE_HEADER, description="Ставит gateway по JWT: user | admin"),
) -> Identity:
    if not x_user_id or x_user_role not in ROLES:
        raise Unauthorized("Требуется авторизация: передайте Bearer-токен через gateway")
    return Identity(x_user_id, x_user_role)


def require_role(*roles: str):
    def dependency(identity: Identity = Depends(current_identity)) -> Identity:
        if identity.role not in roles:
            raise Forbidden(f"Недостаточно прав: нужна роль {' или '.join(roles)}")
        return identity

    return dependency


def create_token(subject: str, role: str, *, secret: str, algorithm: str, ttl_minutes: int, issuer: str) -> str:
    now = datetime.now(UTC)
    claims = {"sub": subject, "role": role, "iss": issuer, "iat": now, "exp": now + timedelta(minutes=ttl_minutes)}
    return jwt.encode(claims, secret, algorithm=algorithm)


def decode_token(token: str, *, secret: str, algorithm: str, issuer: str) -> Identity:
    try:
        claims = jwt.decode(token, secret, algorithms=[algorithm], issuer=issuer, options={"require": ["sub", "exp"]})
    except jwt.ExpiredSignatureError as error:
        raise Unauthorized("Срок действия токена истёк", code="token_expired") from error
    except jwt.PyJWTError as error:
        raise Unauthorized("Недействительный токен", code="invalid_token") from error
    if claims.get("role") not in ROLES:
        raise Unauthorized("Недействительный токен: неизвестная роль", code="invalid_token")
    return Identity(str(claims["sub"]), claims["role"])
