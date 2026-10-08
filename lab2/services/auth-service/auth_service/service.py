"""Бизнес-логика пользователей: регистрация, вход, роли. Пароли хранятся только как bcrypt-хеш."""

import logging

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models import User
from rag_common.errors import BadRequest, Conflict, NotFound, Unauthorized

log = logging.getLogger(__name__)
# Хеш для несуществующего email: проверка пароля занимает то же время, что и для настоящего пользователя,
# поэтому по времени ответа нельзя узнать, зарегистрирован ли email.
_DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt()).decode()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode())


class UserService:
    def __init__(self, session: AsyncSession, password_min_length: int):
        self.session = session
        self.password_min_length = password_min_length

    async def register(self, email: str, password: str, role: str = "user") -> User:
        if len(password) < self.password_min_length:
            raise BadRequest(f"Пароль короче {self.password_min_length} символов", code="weak_password")
        if await self._by_email(email):
            raise Conflict("Пользователь с таким email уже зарегистрирован", code="email_taken")
        user = User(email=email, password_hash=hash_password(password), role=role)
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError as error:  # одновременная регистрация того же email
            await self.session.rollback()
            raise Conflict("Пользователь с таким email уже зарегистрирован", code="email_taken") from error
        log.info("Пользователь зарегистрирован", extra={"user_id": user.id, "role": role})
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._by_email(email)
        if not verify_password(password, user.password_hash if user else _DUMMY_HASH) or user is None:
            raise Unauthorized("Неверный email или пароль", code="invalid_credentials")
        return user

    async def get(self, user_id: str) -> User:
        user = await self.session.get(User, user_id)
        if user is None:
            raise NotFound("Пользователь не найден")
        return user

    async def list(self, limit: int, offset: int) -> tuple[list[User], int]:
        total = await self.session.scalar(select(func.count()).select_from(User))
        users = await self.session.scalars(select(User).order_by(User.created_at).limit(limit).offset(offset))
        return list(users), total

    async def set_role(self, user_id: str, role: str) -> User:
        user = await self.get(user_id)
        if user.role == "admin" and role != "admin" and await self._admins() == 1:
            raise Conflict("Нельзя снять роль с последнего администратора", code="last_admin")
        user.role = role
        await self.session.commit()
        log.info("Роль изменена", extra={"user_id": user_id, "role": role})
        return user

    async def ensure_admin(self, email: str, password: str) -> None:
        if await self._by_email(email) is None:
            try:
                await self.register(email, password, role="admin")
            except Conflict:  # несколько реплик стартуют одновременно: администратора уже создала другая
                log.info("Администратор уже создан другой репликой")

    async def _by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def _admins(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
