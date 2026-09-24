"""
Тесты запросов к сервису клиентов.
"""

import pytest


def test_create_account_returns_201_and_card(client, account_payload):
    response = client.post("/accounts", json=account_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["name"] == account_payload["name"]
    assert body["email"] == account_payload["email"]
    assert body["created_at"]


def test_duplicate_email_returns_409(client, account_payload):
    client.post("/accounts", json=account_payload)

    response = client.post("/accounts", json=account_payload)

    assert response.status_code == 409
    assert "уже существует" in response.json()["detail"]


@pytest.mark.parametrize(
    "broken_field",
    [
        {"email": "это-не-адрес"},
        {"name": ""},
        {"name": "x" * 200},
    ],
)
def test_invalid_payload_returns_422(client, account_payload, broken_field):
    payload = account_payload | broken_field

    response = client.post("/accounts", json=payload)

    assert response.status_code == 422


def test_read_created_account(client, account_payload):
    created = client.post("/accounts", json=account_payload).json()

    response = client.get(f"/accounts/{created['id']}")

    assert response.status_code == 200
    assert response.json()["email"] == account_payload["email"]


def test_read_missing_account_returns_404(client):
    response = client.get("/accounts/99999")

    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_list_is_empty_before_any_account(client):
    response = client.get("/accounts")

    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_accounts_in_creation_order(client, account_payload):
    for number in range(3):
        client.post("/accounts", json=account_payload | {"email": f"user{number}@example.com"})

    response = client.get("/accounts")

    emails = [item["email"] for item in response.json()]
    assert emails == ["user0@example.com", "user1@example.com", "user2@example.com"]


def test_list_supports_limit_and_offset(client, account_payload):
    for number in range(5):
        client.post("/accounts", json=account_payload | {"email": f"user{number}@example.com"})

    response = client.get("/accounts", params={"limit": 2, "offset": 1})

    emails = [item["email"] for item in response.json()]
    assert emails == ["user1@example.com", "user2@example.com"]


def test_patch_updates_only_sent_fields(client, account_payload):
    created = client.post("/accounts", json=account_payload).json()

    response = client.patch(f"/accounts/{created['id']}", json={"name": "Пётр Иванов"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Пётр Иванов"
    assert body["email"] == account_payload["email"]


def test_patch_to_taken_email_returns_409(client, account_payload):
    first = client.post("/accounts", json=account_payload).json()
    client.post("/accounts", json=account_payload | {"email": "second@example.com"})

    response = client.patch(f"/accounts/{first['id']}", json={"email": "second@example.com"})

    assert response.status_code == 409


def test_patch_missing_account_returns_404(client):
    response = client.patch("/accounts/99999", json={"name": "Кто-то"})

    assert response.status_code == 404


def test_delete_account_returns_204_and_it_disappears(client, account_payload):
    created = client.post("/accounts", json=account_payload).json()

    response = client.delete(f"/accounts/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/accounts/{created['id']}").status_code == 404


def test_delete_missing_account_returns_404(client):
    response = client.delete("/accounts/99999")

    assert response.status_code == 404
