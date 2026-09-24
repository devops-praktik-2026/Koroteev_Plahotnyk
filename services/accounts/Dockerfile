# Сборка образа сервиса клиентов.
#
# Собирается в два этапа. На первом ставятся зависимости (это долго и требует
# компилятора), на втором остаётся только результат. Готовый образ получается
# примерно в шесть раз меньше, чем при сборке «в один слой», и в нём нет ни
# компилятора, ни исходников зависимостей.
#

# ---------- этап 1: собираем зависимости ----------
FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml ./
COPY accounts ./accounts
RUN pip install --no-cache-dir --prefix=/install .

# ---------- этап 2: собираем итоговый образ ----------
FROM python:3.12-slim

# Не запускаем приложение от имени администратора: если его взломают,
# злоумышленник получит права обычного пользователя, а не все сразу.
RUN useradd --create-home --uid 1000 app

COPY --from=builder /install /usr/local

WORKDIR /app
COPY accounts ./accounts
COPY alembic.ini ./
COPY migrations ./migrations

USER app
EXPOSE 8000

# Docker сам регулярно спрашивает у сервиса, жив ли он. Если сервис перестал
# отвечать, это видно в `docker compose ps` без чтения журналов.
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "accounts.main:app", "--host", "0.0.0.0", "--port", "8000"]
