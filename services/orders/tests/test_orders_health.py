"""Единственный тест, который проходит с самого начала.

Он нужен, чтобы на первом занятии вы увидели зелёную проверку и убедились,
что окружение собрано правильно.
"""

from fastapi.testclient import TestClient

from orders.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "orders"}
