
import support_router


def test_knowledge_request_uses_rag(monkeypatch):
    monkeypatch.setattr(
        support_router,
        "classify_request",
        lambda state: {"category": "returns"},
    )
    monkeypatch.setattr(
        support_router,
        "retrieve_knowledge",
        lambda state: {
            "retrieved_chunks": [],
            "sources": ["returns_refunds.md"],
        },
    )
    monkeypatch.setattr(
        support_router,
        "generate_answer",
        lambda state: {"answer": "Refunds take 5–7 business days after approval."},
    )
    
    monkeypatch.setattr(
    support_router,
    "routed_support_graph",
    support_router.build_routed_support_graph(),
    )

    result = support_router.run_routed_support(
        "How long do refunds take?"
    )

    assert result["intent"] == "knowledge"
    assert result["category"] == "returns"
    assert "5–7 business days" in result["answer"]
    assert result["sources"] == ["returns_refunds.md"]


def test_order_request_calls_safe_lookup(monkeypatch):
    def fake_lookup(order_id, customer_id):
        assert order_id == "ORD1001"
        assert customer_id == 1
        return {
            "success": True,
            "message": "Order retrieved successfully.",
            "order": {
                "order_id": "ORD1001",
                "order_status": "shipped",
                "expected_delivery_date": "2026-10-24",
            },
        }

    monkeypatch.setattr(
        support_router,
        "lookup_order_for_customer",
        fake_lookup,
    )

    result = support_router.run_routed_support(
        "Where is my order?",
        customer_id=1,
        order_id="ORD1001",
    )

    assert result["intent"] == "order_lookup"
    assert "shipped" in result["answer"]
    assert result["action_result"]["success"] is True


def test_ticket_request_does_not_create_without_confirmation(
    monkeypatch,
):
    def fail_if_called(**kwargs):
        raise AssertionError("Ticket must not be created.")

    monkeypatch.setattr(
        support_router,
        "confirm_ticket_creation",
        fail_if_called,
    )

    result = support_router.run_routed_support(
        "Please create a support ticket",
        customer_id=1,
        ticket_issue="Delivery problem",
    )

    assert result["intent"] == "ticket"
    assert result["action_result"]["requires_confirmation"] is True
    assert "confirm" in result["answer"].lower()


def test_confirmed_ticket_request_calls_action(monkeypatch):
    def fake_create(**kwargs):
        assert kwargs["confirmed"] is True
        return {
            "success": True,
            "requires_confirmation": False,
            "message": "Support ticket created successfully.",
            "ticket": {"ticket_id": "TKTTEST"},
        }

    monkeypatch.setattr(
        support_router,
        "confirm_ticket_creation",
        fake_create,
    )

    result = support_router.run_routed_support(
        "Please create a support ticket",
        customer_id=1,
        ticket_issue="Delivery problem",
        ticket_confirmed=True,
    )

    assert result["action_result"]["success"] is True
    assert "TKTTEST" in result["answer"]
