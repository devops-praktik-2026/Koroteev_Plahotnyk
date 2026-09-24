"""Настройки сервиса.

Все настройки приходят снаружи — из переменных окружения или файла .env.
Ни одного адреса базы данных или пароля в коде быть не должно: один и тот же
образ должен одинаково работать и на ноутбуке, и на сервере.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # По умолчанию — файл рядом с проектом, чтобы сервис запускался без Docker.
    # В compose.yaml сюда подставляется адрес PostgreSQL.
    database_url: str = "sqlite:///./accounts.db"

    service_name: str = "accounts"
    log_level: str = "info"


settings = Settings()
