"""Помощники для тестов сервисов."""

from rag_common.auth import USER_ID_HEADER, USER_ROLE_HEADER


def as_user(user_id: str = "user-1", role: str = "user") -> dict[str, str]:
    """Заголовки, которые gateway ставит после проверки JWT."""
    return {USER_ID_HEADER: user_id, USER_ROLE_HEADER: role}


def as_admin(user_id: str = "admin-1") -> dict[str, str]:
    return as_user(user_id, "admin")
