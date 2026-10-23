
import shutil
from pathlib import Path

import pytest

import db
import support_router
from vector_store import search_knowledge


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    """Use a temporary copy of the demo database for each test."""
    original_db = Path(db.DB_PATH)
    test_db = tmp_path / "supportpilot_test.db"

    shutil.copy2(original_db, test_db)
    monkeypatch.setattr(db, "DB_PATH", test_db)

    return test_db


def test_real_knowledge_retrieval():
    """Retrieve relevant content from the actual Chroma vector store."""
    results = search_knowledge("refund policy and processing time", top_k=3)

    assert results, "No knowledge chunks were retrieved."
    assert any(
        result.get("text", "").strip()
        for result in results
    ), "Retrieved chunks contain no text."


def test_real_order_lookup(isolated_database):
    """Route an order question to the actual SQLite database."""
    result = support_router.run_routed_support(
        query="Where is my order?",
        customer_id=1,
        order_id="ORD1001",
    )

    assert result["intent"] == "order_lookup"
    assert "ORD1001" in result["answer"]
    assert "shipped" in result["answer"].lower()
    assert result["action_result"]["success"] is True


def test_real_ticket_creation_after_confirmation(isolated_database):
    """Create a ticket in the temporary database and verify it."""
    result = support_router.run_routed_support(
        query="Create a support ticket",
        customer_id=1,
        ticket_issue="Integration test: damaged product",
        ticket_priority="medium",
        ticket_confirmed=True,
    )

    assert result["intent"] == "ticket"
    assert result["action_result"]["success"] is True

    ticket_id = result["action_result"]["ticket"]["ticket_id"]
    saved_ticket = db.get_ticket(ticket_id)

    assert saved_ticket is not None
    assert saved_ticket["customer_id"] == 1
    assert saved_ticket["issue"] == "Integration test: damaged product"
