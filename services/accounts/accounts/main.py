"""Точка входа сервиса клиентов.

Запуск вручную:
    uvicorn accounts.main:app --reload --port 8001

Документация по адресам, которые сервис понимает: http://localhost:8001/docs
"""

from fastapi import FastAPI

from accounts.api import router
from accounts.config import settings
from accounts.schemas import HealthRead

app = FastAPI(
    title="Сервис клиентов",
    description=("Пример реализации сервиса для предмета DevOps практики. "),
    version="0.1.0",
)

app.include_router(router)


@app.get("/health", response_model=HealthRead, tags=["Служебное"], summary="Жив ли сервис")
def health() -> HealthRead:
    """Короткий ответ для проверки после установки новой версии.

    Намеренно не обращается к базе данных: этот запрос должен отвечать
    быстро и всегда, иначе им нельзя пользоваться при выкатке.
    """
    return HealthRead(status="ok", service=settings.service_name)
