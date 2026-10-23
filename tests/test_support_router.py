
import pytest

import support_router


def test_order_request_is_routed():
    result = support_router.classify_intent(
        {"query": "Where is my order?"}
    )
    assert result["intent"] == "order_lookup"


def test_ticket_request_is_routed():
    result = support_router.classify_intent(
        {"query": "Please create a support ticket"}
    )
    assert result["intent"] == "ticket"


def test_policy_question_uses_knowledge():
    result = support_router.classify_intent(
        {"query": "How long do refunds take?"}
    )
    assert result["intent"] == "knowledge"


def test_order_lookup_requires_context():
    result = support_router.handle_order_lookup(
        {
            "query": "Where is my order?",
            "customer_id": None,
            "order_id": None,
        }
    )
    assert result["action_result"]["success"] is False


def test_ticket_requires_confirmation(monkeypatch):
    def fail_if_called(**kwargs):
        pytest.fail("Ticket creation must not run without confirmation.")

    monkeypatch.setattr(
        support_router,
        "confirm_ticket_creation",
        fail_if_called,
    )

    result = support_router.handle_ticket_request(
        {
            "query": "Create a ticket",
            "customer_id": 1,
            "order_id": None,
            "ticket_issue": "Delivery problem",
            "ticket_priority": "medium",
            "ticket_confirmed": False,
        }
    )

    assert result["action_result"]["requires_confirmation"] is True
