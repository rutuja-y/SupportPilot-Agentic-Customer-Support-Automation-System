
import support_router


def test_knowledge_question_end_to_end(monkeypatch):
    """Knowledge questions should pass through the RAG workflow."""

    monkeypatch.setattr(
        support_router,
        "classify_request",
        lambda state: {"category": "returns"},
    )
    monkeypatch.setattr(
        support_router,
        "retrieve_knowledge",
        lambda state: {
            "retrieved_chunks": [
                {
                    "text": "Refunds take 5-7 business days after approval.",
                    "metadata": {"source": "returns_refunds.md"},
                    "distance": 0.1,
                }
            ],
            "sources": ["returns_refunds.md"],
        },
    )
    monkeypatch.setattr(
        support_router,
        "generate_answer",
        lambda state: {
            "answer": "Refunds take 5-7 business days after approval."
        },
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
    assert "5-7 business days" in result["answer"]
    assert "returns_refunds.md" in result["sources"]


def test_order_lookup_end_to_end(monkeypatch):
    """Order requests should use the safe order lookup action."""

    monkeypatch.setattr(
        support_router,
        "lookup_order_for_customer",
        lambda order_id, customer_id: {
            "success": True,
            "order": {
                "order_id": "ORD1001",
                "order_status": "shipped",
                "expected_delivery_date": "2026-10-24",
            },
        },
    )

    result = support_router.run_routed_support(
        query="Where is my order?",
        customer_id=1,
        order_id="ORD1001",
    )

    assert result["intent"] == "order_lookup"
    assert "ORD1001" in result["answer"]
    assert "shipped" in result["answer"]


def test_ticket_requires_confirmation_end_to_end(monkeypatch):
    """A ticket request must not create a ticket before confirmation."""

    def unexpected_ticket_creation(*args, **kwargs):
        raise AssertionError("Ticket creation occurred without confirmation")

    monkeypatch.setattr(
        support_router,
        "confirm_ticket_creation",
        unexpected_ticket_creation,
    )

    result = support_router.run_routed_support(
        query="Create a support ticket for a damaged product",
        customer_id=1,
        ticket_confirmed=False,
    )

    assert result["intent"] == "ticket"
    assert result["action_result"]["requires_confirmation"] is True
    assert "confirm" in result["answer"].lower()


def test_confirmed_ticket_end_to_end(monkeypatch):
    """A confirmed request should invoke the ticket action."""

    monkeypatch.setattr(
        support_router,
        "confirm_ticket_creation",
        lambda **kwargs: {
            "success": True,
            "requires_confirmation": False,
            "ticket": {"ticket_id": "TKTTEST"},
            "message": "Ticket created.",
        },
    )

    result = support_router.run_routed_support(
        query="Create a support ticket",
        customer_id=1,
        ticket_issue="Damaged product",
        ticket_confirmed=True,
    )

    assert result["intent"] == "ticket"
    assert result["action_result"]["success"] is True
    assert "TKTTEST" in result["answer"]
