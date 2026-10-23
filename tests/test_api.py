
import pytest
from fastapi.testclient import TestClient

import db
import init_db
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Give each API test its own temporary database."""
    test_db_path = tmp_path / "test_supportpilot.db"

    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    monkeypatch.setattr(init_db, "DB_PATH", test_db_path)

    init_db.initialize_database()

    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_existing_order(client):
    response = client.get("/orders/ORD1003")

    assert response.status_code == 200

    data = response.json()
    assert data["order_id"] == "ORD1003"
    assert data["order_status"] == "delayed"
    assert data["customer_id"] == 3
    assert data["customer_name"] == "Rohan Mehta"


def test_get_missing_order(client):
    response = client.get("/orders/ORD9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found."


def test_create_ticket(client):
    payload = {
        "customer_id": 3,
        "order_id": "ORD1003",
        "issue": "My order is delayed. Please investigate.",
        "priority": "high",
    }

    response = client.post("/tickets", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["ticket_id"].startswith("TKT")
    assert data["customer_id"] == 3
    assert data["order_id"] == "ORD1003"
    assert data["priority"] == "high"
    assert data["status"] == "open"

    # Verify the API actually saved the ticket.
    saved_ticket = db.get_ticket(data["ticket_id"])
    assert saved_ticket is not None
    assert saved_ticket["issue"] == payload["issue"]


def test_reject_wrong_customer_for_order(client):
    payload = {
        "customer_id": 2,
        "order_id": "ORD1003",
        "issue": "I want to complain about this order.",
        "priority": "medium",
    }

    response = client.post("/tickets", json=payload)

    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"]


def test_reject_invalid_priority(client):
    payload = {
        "customer_id": 1,
        "issue": "My product has an issue.",
        "priority": "critical",
    }

    response = client.post("/tickets", json=payload)

    assert response.status_code == 422


def test_reject_missing_issue(client):
    payload = {
        "customer_id": 1,
        "priority": "medium",
    }

    response = client.post("/tickets", json=payload)

    assert response.status_code == 422


def test_reject_empty_issue(client):
    payload = {
        "customer_id": 1,
        "issue": "   ",
        "priority": "medium",
    }

    response = client.post("/tickets", json=payload)

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_reject_nonexistent_customer(client):
    payload = {
        "customer_id": 999,
        "issue": "Test invalid customer.",
        "priority": "medium",
    }

    response = client.post("/tickets", json=payload)

    assert response.status_code == 400
    assert "Could not create ticket" in response.json()["detail"]
