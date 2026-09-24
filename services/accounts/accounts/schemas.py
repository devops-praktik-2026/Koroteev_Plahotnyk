"""Описание того, что сервис принимает и что отдаёт.

Эти классы — не формальность. Из них FastAPI сам собирает документацию
по адресу /docs и сам проверяет входящие данные.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AccountCreate(BaseModel):
    """Данные для создания клиента."""

    name: str = Field(min_length=1, max_length=64, examples=["Иван Петров"])
    email: EmailStr = Field(examples=["ivan@example.com"])
    phone: str | None = Field(default=None, max_length=32, examples=["+7 900 000-00-00"])


class AccountUpdate(BaseModel):
    """Данные для изменения клиента. Можно прислать только часть полей."""

    name: str | None = Field(default=None, min_length=1, max_length=64)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)


class AccountRead(BaseModel):
    """То, что сервис отдаёт наружу."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str | None
    created_at: datetime


class HealthRead(BaseModel):
    """Ответ служебной проверки «жив ли сервис»."""

    status: str
    service: str
