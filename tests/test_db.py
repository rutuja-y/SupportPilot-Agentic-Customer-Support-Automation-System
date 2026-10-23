
import pytest

import db
import init_db


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Create a fresh, isolated database for every test."""
    test_db_path = tmp_path / "test_supportpilot.db"

    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    monkeypatch.setattr(init_db, "DB_PATH", test_db_path)

    init_db.initialize_database()

    return test_db_path


def test_order_lookup(test_database):
    order = db.get_order("ORD1003")

    assert order is not None
    assert order["order_status"] == "delayed"
    assert order["customer_id"] == 3
    assert order["customer_name"] == "Rohan Mehta"


def test_missing_order(test_database):
    assert db.get_order("ORD9999") is None


def test_customer_orders(test_database):
    orders = db.get_customer_orders(1)

    order_ids = {order["order_id"] for order in orders}

    assert order_ids == {"ORD1001", "ORD1004"}


def test_create_and_retrieve_ticket(test_database):
    ticket = db.create_ticket(
        customer_id=3,
        order_id="ORD1003",
        issue="My order is delayed.",
        priority="high",
    )

    assert ticket is not None
    assert ticket["ticket_id"].startswith("TKT")
    assert ticket["status"] == "open"
    assert ticket["priority"] == "high"

    saved_ticket = db.get_ticket(ticket["ticket_id"])

    assert saved_ticket["issue"] == "My order is delayed."
    assert saved_ticket["order_id"] == "ORD1003"


def test_reject_order_belonging_to_another_customer(test_database):
    with pytest.raises(ValueError, match="does not belong"):
        db.create_ticket(
            customer_id=2,
            order_id="ORD1003",
            issue="I want to complain about this order.",
        )


def test_reject_invalid_customer(test_database):
    with pytest.raises(ValueError, match="Could not create ticket"):
        db.create_ticket(
            customer_id=999,
            issue="Test invalid customer.",
        )


def test_reject_empty_issue(test_database):
    with pytest.raises(ValueError, match="cannot be empty"):
        db.create_ticket(
            customer_id=1,
            issue="   ",
        )


def test_reject_invalid_priority(test_database):
    with pytest.raises(ValueError, match="Invalid ticket priority"):
        db.create_ticket(
            customer_id=1,
            issue="Test invalid priority.",
            priority="critical",
        )
