"""Настройки сервиса заказов.

Адрес сервиса клиентов приходит снаружи. Локально это http://localhost:8001,
внутри docker compose — http://accounts:8000, на сервере — тоже своё значение.
Именно поэтому его нельзя записывать прямо в код.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "orders"

    # Куда ходить за проверкой клиента.
    accounts_url: str = "http://localhost:8001"

    # Сколько секунд ждать ответа от сервиса клиентов, прежде чем сдаться.
    accounts_timeout_seconds: float = 2.0


settings = Settings()
