"""Заведомо падающий тест

СЕЙЧАС ОН ПРОПУСКАЕТСЯ. Снимите строку со skip ниже, запустите проверки
и убедитесь, что тест падает. Это нормальное и правильное состояние:
сначала появляется тест, который описывает нужное поведение, и только
потом — код, который заставляет его пройти.

"""

import pytest
from fastapi.testclient import TestClient

from orders.main import app

# ↓↓↓ Уберите эту строку на занятии 2 ↓↓↓
pytest.skip("Реализуется на занятии 2: снимите пропуск", allow_module_level=True)

client = TestClient(app)


def test_create_order_returns_201():
    payload = {"account_id": 1, "item": "Кофемолка", "quantity": 2}

    response = client.post("/orders", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["account_id"] == payload["account_id"]
    assert body["item"] == payload["item"]
    assert body["quantity"] == payload["quantity"]
