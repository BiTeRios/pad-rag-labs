from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class Credentials(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN, max_length=254, examples=["user@example.com"])
    # bcrypt учитывает только первые 72 байта пароля, поэтому длиннее не принимаем
    password: str = Field(min_length=1, max_length=64, examples=["secret-password"])

    @field_validator("email", mode="before")  # до проверки шаблона: « User@Mail.ru » → «user@mail.ru»
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(description="секунд до истечения токена")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    role: Literal["user", "admin"]
    created_at: datetime


class RoleUpdate(BaseModel):
    role: Literal["user", "admin"]
