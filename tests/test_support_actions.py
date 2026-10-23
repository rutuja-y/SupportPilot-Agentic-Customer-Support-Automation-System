
import pytest

import support_actions


def test_order_lookup_success(monkeypatch):
    fake_order = {
        "order_id": "ORD1001",
        "customer_id": 1,
        "product_name": "Wireless Headphones",
        "order_status": "shipped",
    }

    monkeypatch.setattr(
        support_actions.db,
        "get_order",
        lambda order_id: fake_order,
    )

    result = support_actions.lookup_order_for_customer("ORD1001", 1)

    assert result["success"] is True
    assert result["order"]["order_id"] == "ORD1001"


def test_order_lookup_hides_other_customers_orders(monkeypatch):
    fake_order = {
        "order_id": "ORD1001",
        "customer_id": 1,
        "product_name": "Wireless Headphones",
        "order_status": "shipped",
    }

    monkeypatch.setattr(
        support_actions.db,
        "get_order",
        lambda order_id: fake_order,
    )

    result = support_actions.lookup_order_for_customer("ORD1001", 2)

    assert result["success"] is False
    assert result["order"] is None


def test_order_lookup_handles_missing_order(monkeypatch):
    monkeypatch.setattr(
        support_actions.db,
        "get_order",
        lambda order_id: None,
    )

    result = support_actions.lookup_order_for_customer("ORD9999", 1)

    assert result["success"] is False


def test_ticket_creation_success(monkeypatch):
    fake_ticket = {
        "ticket_id": "TKT9999",
        "customer_id": 1,
        "issue": "Headphones will not connect",
        "priority": "medium",
        "status": "open",
    }

    def fake_create_ticket(**kwargs):
        assert kwargs["customer_id"] == 1
        assert kwargs["issue"] == "Headphones will not connect"
        return fake_ticket

    monkeypatch.setattr(
        support_actions.db,
        "create_ticket",
        fake_create_ticket,
    )

    result = support_actions.create_support_ticket(
        customer_id=1,
        issue=" Headphones will not connect ",
    )

    assert result["success"] is True
    assert result["ticket"]["ticket_id"] == "TKT9999"


def test_ticket_creation_rejects_empty_issue():
    with pytest.raises(ValueError):
        support_actions.create_support_ticket(
            customer_id=1,
            issue="   ",
        )


def test_ticket_creation_rejects_invalid_priority():
    with pytest.raises(ValueError):
        support_actions.create_support_ticket(
            customer_id=1,
            issue="Delivery problem",
            priority="critical",
        )


def test_ticket_creation_rejects_invalid_customer():
    with pytest.raises(ValueError):
        support_actions.create_support_ticket(
            customer_id=0,
            issue="Delivery problem",
        )
